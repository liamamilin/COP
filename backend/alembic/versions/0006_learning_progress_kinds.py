"""Let one progress row describe a Stage, a Practice, or a Checkpoint.

M7 stored Stage progress only, so a Practice could be read but never completed
and a checkpoint question could be read but never answered. Rather than add
three near-identical tables, the same row grows a `kind` discriminator.

The old unique index is replaced rather than extended. It was built on
`(version_id, goal_id, coalesce(stage_id, ''))`, which cannot tell a Foundation
Stage row from a Main Process Stage row: both have a NULL `goal_id`, so they
collide. The new index includes `kind` and uses a coalesced *owner* pair, so a
Foundation row and a Practice row for the same Goal are different things.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0006_learning_progress_kinds"
down_revision: str | None = "0005_learning_progress_unique"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE learning_progress ADD COLUMN kind varchar(16) NOT NULL DEFAULT 'stage'")
    op.execute("DROP INDEX IF EXISTS uq_learning_progress_stage")
    # Written as SQL for the same reason as 0005: Alembic quotes an index
    # expression as a column name, and Postgres then reports a column that does
    # not exist. Two coalesces because Foundation progress has no goal and
    # Practice progress has no stage, and both are legitimate keys.
    #
    # `notes` is deliberately absent: it holds the learner's own text, so
    # including it would let the same activity be recorded twice under two
    # different answers. Identity is (version, kind, goal, stage).
    op.execute(
        """
        CREATE UNIQUE INDEX uq_learning_progress_activity
        ON learning_progress (
            version_id,
            kind,
            coalesce(goal_id, ''),
            coalesce(stage_id, '')
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_learning_progress_activity")
    op.execute(
        """
        CREATE UNIQUE INDEX uq_learning_progress_stage
        ON learning_progress (version_id, goal_id, coalesce(stage_id, ''))
        """
    )
    op.execute("ALTER TABLE learning_progress DROP COLUMN IF EXISTS kind")
