"""Keep one progress row per Stage.

Without this a `PUT` could record the same Stage twice, and every read would
have to decide which row wins. Progress is a fold, not a log: a Stage is
either done or it is not.

The index uses `coalesce(stage_id, '')` because `stage_id` is nullable for
Goal-level completion, and a plain unique index would treat every NULL as
distinct, silently permitting duplicates for exactly the rows that are hardest
to notice.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0005_learning_progress_unique"
down_revision: str | None = "0004_run_candidate_patch"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Written as SQL rather than `op.create_index` because Alembic quotes index
    # expressions as column names, which Postgres then reads as a column that
    # does not exist.
    op.execute(
        """
        CREATE UNIQUE INDEX uq_learning_progress_stage
        ON learning_progress (version_id, goal_id, coalesce(stage_id, ''))
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_learning_progress_stage")
