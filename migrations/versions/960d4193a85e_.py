"""empty message

Revision ID: 960d4193a85e
Revises: 4fa9a879ff38
Create Date: 2022-10-04 22:26:10.707255

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '960d4193a85e'
down_revision = '4fa9a879ff38'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('parqueadero',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=150), nullable=True),
    sa.Column('capacidad_carros', sa.Integer(), nullable=True),
    sa.Column('capacidad_motos', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tipovehiculo',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=150), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('vehiculo',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('placa', sa.String(length=10), nullable=True),
    sa.Column('imagen', sa.Text(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('tipo_vehiculo_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['tipo_vehiculo_id'], ['tipovehiculo.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('movimiento_vehiculo',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('fecha_ingreso', sa.DateTime(timezone=True), nullable=True),
    sa.Column('fecha_salida', sa.DateTime(timezone=True), nullable=True),
    sa.Column('estado', sa.String(length=20), nullable=True),
    sa.Column('vehiculo_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['vehiculo_id'], ['vehiculo.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('rol', sa.Column('nombre', sa.String(length=150), nullable=True))
    op.drop_column('rol', 'name')
    op.drop_column('rol', 'date')
    op.add_column('user', sa.Column('nombre', sa.String(length=150), nullable=True))
    op.add_column('user', sa.Column('usuario', sa.String(length=50), nullable=True))
    op.drop_constraint('user_username_key', 'user', type_='unique')
    op.create_unique_constraint(None, 'user', ['usuario'])
    op.drop_column('user', 'placa')
    op.drop_column('user', 'username')
    op.drop_column('user', 'name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('name', sa.VARCHAR(length=150), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('username', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('placa', sa.VARCHAR(length=10), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'user', type_='unique')
    op.create_unique_constraint('user_username_key', 'user', ['username'])
    op.drop_column('user', 'usuario')
    op.drop_column('user', 'nombre')
    op.add_column('rol', sa.Column('date', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True))
    op.add_column('rol', sa.Column('name', sa.VARCHAR(length=150), autoincrement=False, nullable=True))
    op.drop_column('rol', 'nombre')
    op.drop_table('movimiento_vehiculo')
    op.drop_table('vehiculo')
    op.drop_table('tipovehiculo')
    op.drop_table('parqueadero')
    # ### end Alembic commands ###