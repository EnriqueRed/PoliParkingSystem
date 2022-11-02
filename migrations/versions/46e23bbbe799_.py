"""empty message

Revision ID: 46e23bbbe799
Revises: ad7dcdfbe915
Create Date: 2022-11-02 01:12:28.093652

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '46e23bbbe799'
down_revision = 'ad7dcdfbe915'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('movimiento_vehiculo', sa.Column('minutos', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('movimiento_vehiculo', 'minutos')
    # ### end Alembic commands ###