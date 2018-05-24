"""Add minutes FK constraint to ALV.

Revision ID: f05f7c8518a3
Revises: 22710e6fd2b1
Create Date: 2018-03-20 13:04:10.320984

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# revision identifiers, used by Alembic.
revision = 'f05f7c8518a3'
down_revision = '22710e6fd2b1'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    # Set any invalid minutes_file_id to NULL first
    op.execute('''UPDATE alv
LEFT JOIN file f ON f.id = alv.minutes_file_id
SET minutes_file_id = NULL
WHERE f.id IS NULL''')

    op.create_foreign_key(op.f('fk_alv_minutes_file_id_file'), 'alv', 'file', ['minutes_file_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('fk_alv_minutes_file_id_file'), 'alv', type_='foreignkey')
    # ### end Alembic commands ###


# vim: ft=python
