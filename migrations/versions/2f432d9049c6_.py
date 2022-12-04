"""empty message

Revision ID: 2f432d9049c6
Revises: 7bac40cd2dba
Create Date: 2022-11-04 12:10:42.212646

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2f432d9049c6'
down_revision = '7bac40cd2dba'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('parqueadero', sa.Column('url_mapa', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('parqueadero', 'url_mapa')
    # ### end Alembic commands ###