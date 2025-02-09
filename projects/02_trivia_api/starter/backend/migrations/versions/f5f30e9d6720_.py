"""empty message

Revision ID: f5f30e9d6720
Revises: 3517f6cb08b3
Create Date: 2021-06-09 08:55:20.702336

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5f30e9d6720'
down_revision = '3517f6cb08b3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.rename_table('game', 'games')
    # op.add_column('games', sa.Column('score', sa.Integer(), nullable=False))
    op.create_unique_constraint('unique_category_type' 'categories', ['type'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('game', 'score')
    # ### end Alembic commands ###
