"""Draft provenance, and allow a candidate draft to have no base version.

`drafts.base_version_id` was NOT NULL, which made the first COP of a project
unpublishable-by-draft: a candidate produced by a run with no `base_version_id`
had nowhere to point. It becomes nullable.

`source_run_id` records whether the draft came from a run candidate or a
published version, so publishing can record provenance instead of inferring it.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0002_draft_provenance"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "drafts",
        "base_version_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=True,
    )
    op.add_column(
        "drafts",
        sa.Column("source_run_id", postgresql.UUID(as_uuid=True)),
    )


def downgrade() -> None:
    op.drop_column("drafts", "source_run_id")
    # Restore NOT NULL only when no row would violate it. A draft created from a
    # first-run candidate has a null base, so the downgrade reports the conflict
    # rather than silently deleting or inventing a base version.
    op.execute(
        "DO $$ BEGIN "
        "  IF EXISTS (SELECT 1 FROM drafts WHERE base_version_id IS NULL) THEN "
        "    RAISE EXCEPTION "
        "      'Cannot restore NOT NULL: % draft(s) have no base_version_id', "
        "      (SELECT count(*) FROM drafts WHERE base_version_id IS NULL); "
        "  END IF; "
        "END $$;"
    )
    op.alter_column(
        "drafts",
        "base_version_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )
