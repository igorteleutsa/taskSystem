"""Add projects table

Revision ID: 3d9b44c8e7a7
Revises: dce954b9ea86
Create Date: 2024-09-18 12:38:26.862055

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3d9b44c8e7a7"
down_revision: Union[str, None] = "dce954b9ea86"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "projects",
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "INACTIVE", "ARCHIVED", name="projectstatus"),
            nullable=False,
        ),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_projects_id"), "projects", ["id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_projects_id"), table_name="projects")
    op.drop_table("projects")
    # ### end Alembic commands ###
