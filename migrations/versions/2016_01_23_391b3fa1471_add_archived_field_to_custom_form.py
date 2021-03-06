"""Add archived field to custom form

Revision ID: 391b3fa1471
Revises: 473f91b5874
Create Date: 2016-01-23 15:51:40.304025

"""

# revision identifiers, used by Alembic.
revision = '391b3fa1471'
down_revision = '473f91b5874'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('custom_form', sa.Column('archived', sa.Boolean(), nullable=True))
    op.alter_column('custom_form', 'price',
               existing_type=mysql.FLOAT(),
               nullable=True,
               existing_server_default=sa.text("'0'"))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('custom_form', 'price',
               existing_type=mysql.FLOAT(),
               nullable=False,
               existing_server_default=sa.text("'0'"))
    op.drop_column('custom_form', 'archived')
    ### end Alembic commands ###
