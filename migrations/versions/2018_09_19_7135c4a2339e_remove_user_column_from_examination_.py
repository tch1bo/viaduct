"""Remove user column from examination table.

Revision ID: 7135c4a2339e
Revises: 6aff43ad8f2a
Create Date: 2018-09-19 21:22:56.309265

"""
from alembic import op
import sqlalchemy as sa


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# revision identifiers, used by Alembic.
revision = '7135c4a2339e'
down_revision = '6aff43ad8f2a'

Base = declarative_base()
db = sa
db.Model = Base
db.relationship = relationship


def create_session():
    connection = op.get_bind()
    session_maker = sa.orm.sessionmaker()
    session = session_maker(bind=connection)
    db.session = session


def upgrade():
    create_session()

    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_examination_user_id_user', 'examination', type_='foreignkey')
    op.drop_column('examination', 'user_id')
    # ### end Alembic commands ###


def downgrade():
    create_session()

    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('examination', sa.Column('user_id', sa.BIGINT(), autoincrement=False, nullable=True))
    op.create_foreign_key('fk_examination_user_id_user', 'examination', 'user', ['user_id'], ['id'])
    # ### end Alembic commands ###


# vim: ft=python
