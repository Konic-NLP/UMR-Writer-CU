"""empty message

Revision ID: 901066fcff9d
Revises: 
Create Date: 2023-01-07 15:54:44.379984

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '901066fcff9d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'username',
               existing_type=sa.VARCHAR(length=20),
               type_=sa.String(length=40),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'username',
               existing_type=sa.String(length=40),
               type_=sa.VARCHAR(length=20),
               existing_nullable=False)
    # ### end Alembic commands ###
