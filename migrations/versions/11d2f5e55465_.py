"""empty message

Revision ID: 11d2f5e55465
Revises: 0f0a86db16cc
Create Date: 2023-01-05 17:40:06.911881

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, Boolean


# revision identifiers, used by Alembic.
revision = '11d2f5e55465'
down_revision = '0f0a86db16cc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tarifa', sa.Column('parqueadero_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'tarifa', 'parqueadero', ['parqueadero_id'], ['id'])
    # ### end Alembic commands ###

    passw = 'sha256$qF0w7MLsMu1q7vcG$e12f476f64f6804012b87037b51e67aa814142939ef87b48f9b00a7630222b11'
    user_table = table('user',
        column('email', String),
        column('password', String),
        column('rol_id', Integer),
        column('nombre', String),
        column('usuario', String),
        column('confirmed', Boolean)
    )
    op.bulk_insert(user_table,
    [
        {'email': 'admin', 'password': passw, 'rol_id': 3, 'nombre': 'Admin', 'usuario': 'admin', 'confirmed': True},

    ])


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tarifa', type_='foreignkey')
    op.drop_column('tarifa', 'parqueadero_id')
    # ### end Alembic commands ###