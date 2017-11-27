"""Generated oauth tables.

Revision ID: b34856689dec
Revises: c633060ef804
Create Date: 2017-11-24 21:01:47.067380

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'b34856689dec'
down_revision = 'c633060ef804'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'oauth_client',
        sa.Column('name', sa.String(length=64), nullable=True),
        sa.Column('description', sa.String(length=512),
                  nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('client_id', sa.String(length=64),
                  nullable=False),
        sa.Column('client_secret', sa.String(length=64),
                  nullable=False),
        sa.Column('confidential', sa.Boolean(), nullable=True),
        sa.Column('_redirect_uris', sa.Text(), nullable=True),
        sa.Column('_default_scopes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'],
                                name=op.f(
                                    'fk_oauth_client_user_id_user')),
        sa.PrimaryKeyConstraint('client_id',
                                name=op.f('pk_oauth_client'))
    )
    op.create_index(op.f('ix_oauth_client_client_secret'), 'oauth_client',
                    ['client_secret'], unique=True)
    op.create_table(
        'oauth_grant',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('client_id', sa.String(length=64),
                  nullable=False),
        sa.Column('code', sa.String(length=255), nullable=False),
        sa.Column('redirect_uri', sa.String(length=255),
                  nullable=True),
        sa.Column('expires', sa.DateTime(), nullable=True),
        sa.Column('_scopes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['client_id'],
                                ['oauth_client.client_id'],
                                name=op.f(
                                    'fk_oauth_grant_client_id_oauth_client')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'],
                                name=op.f(
                                    'fk_oauth_grant_user_id_user'),
                                ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_oauth_grant'))
    )
    op.create_index(op.f('ix_oauth_grant_code'), 'oauth_grant', ['code'],
                    unique=False)
    op.create_table(
        'oauth_token',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.String(length=64),
                  nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('token_type', sa.String(length=64),
                  nullable=True),
        sa.Column('access_token', sa.String(length=255),
                  nullable=True),
        sa.Column('refresh_token', sa.String(length=255),
                  nullable=True),
        sa.Column('expires', sa.DateTime(), nullable=True),
        sa.Column('_scopes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['client_id'],
                                ['oauth_client.client_id'],
                                name=op.f(
                                    'fk_oauth_token_client_id_oauth_client')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'],
                                name=op.f(
                                    'fk_oauth_token_user_id_user')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_oauth_token')),
        sa.UniqueConstraint('access_token', name=op.f(
            'uq_oauth_token_access_token')),
        sa.UniqueConstraint('refresh_token', name=op.f(
            'uq_oauth_token_refresh_token'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('oauth_token')
    op.drop_index(op.f('ix_oauth_grant_code'), table_name='oauth_grant')
    op.drop_table('oauth_grant')
    op.drop_index(op.f('ix_oauth_client_client_secret'),
                  table_name='oauth_client')
    op.drop_table('oauth_client')
    # ### end Alembic commands ###
