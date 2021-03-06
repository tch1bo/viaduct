"""added_alumnus_column

Revision ID: 2105015bafe
Revises: 404db3c1f74
Create Date: 2016-09-10 18:20:33.935231

"""

# revision identifiers, used by Alembic.
revision = '2105015bafe'
down_revision = '404db3c1f74'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('alumnus', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'alumnus')
    ### end Alembic commands ###
