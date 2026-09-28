"""Give a generation run its own candidate-patch state.

The spec (`16-state-machines.md` §5) models a patch as its own object with a
lifecycle of generating → ready → accepted | rejected | expired. Modelling it
on the run keeps the patch tied to the run that produced it, and keeps
"accepting never touches a published version" checkable in one place.

Both columns are nullable because a normal full-generation run has no patch.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0004_run_candidate_patch"
down_revision: str | None = "0003_draft_locked_paths"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "generation_runs",
        sa.Column("candidate_patch_json", postgresql.JSONB(astext_type=sa.Text())),
    )
    op.add_column(
        "generation_runs",
        sa.Column(
            "patch_state",
            sa.String(16),
            # 'idle' rather than NULL: a run that has no patch and a run whose
            # patch was never generated are different situations, and a
            # non-null default makes the first one say so out loud.
            nullable=False,
            server_default="idle",
        ),
    )
    op.create_check_constraint(
        "ck_generation_runs_patch_state",
        "generation_runs",
        "patch_state IN ('idle', 'generating', 'ready', 'accepted', 'rejected', 'expired')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_generation_runs_patch_state", "generation_runs", type_="check")
    op.drop_column("generation_runs", "patch_state")
    op.drop_column("generation_runs", "candidate_patch_json")
