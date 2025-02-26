"""add user_person_id column to user table

Revision ID: 9d1936e66caf
Revises: ae65514adff9
Create Date: 2024-09-21 23:06:18.290366

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9d1936e66caf"
down_revision: Union[str, None] = "ae65514adff9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = "ae65514adff9"


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("user", sa.Column("person_id", sa.Uuid(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("user", "person_id")
    # ### end Alembic commands ###
