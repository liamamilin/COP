"""Record user edits on the draft, so a later AI patch cannot overwrite them.

M6 lets the model propose changes to one entity. Without a record of what the
user wrote by hand, the model would confidently rewrite a field the user had
just corrected, and the user would have no way to tell their own words apart from
the model's.

The M4 Harness already tracks `locked_paths` inside a run's context. That is not
enough: a refinement run is a separate run from the manual edit, so the lock has
to live on the draft, where both can see it.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0003_draft_locked_paths"
down_revision: str | None = "0002_draft_provenance"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # A plain JSON array, not a JSONB object, because the Harness and the
    # refiner both treat a locked path as a flat string and membership tests
    # must stay trivial. Defaulted to an empty array so existing drafts are
    # valid without a backfill.
    op.add_column(
        "drafts",
        sa.Column(
            "locked_paths",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
    )
    # The server default is only for existing rows; new writes always set it.
    op.alter_column("drafts", "locked_paths", server_default=None)


def downgrade() -> None:
    op.drop_column("drafts", "locked_paths")
