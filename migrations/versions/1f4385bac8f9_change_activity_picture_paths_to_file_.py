"""Change activity picture paths to file ids.

Revision ID: 1f4385bac8f9
Revises: c8cd32037cde
Create Date: 2018-03-30 16:01:56.532893

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

import os
import re

from app import app, hashfs
from app.models.base_model import BaseEntity
from app.enums import FileCategory

# revision identifiers, used by Alembic.
revision = '1f4385bac8f9'
down_revision = 'c8cd32037cde'

# op.get_bind() will fail when the migration is created,
# so catch the AttributeError
try:
    Base = declarative_base()
    db = sa
    Session = sessionmaker()

    conn = op.get_bind()
    session = Session(bind=conn)

    db.Model = Base
    db.relationship = relationship
    db.session = session
except AttributeError:
    pass


filename_regex = re.compile(r'(.+)\.([^\s.]+)')


class File(db.Model, BaseEntity):
    __tablename__ = 'file'

    hash = db.Column(db.String(200), nullable=False)
    extension = db.Column(db.String(20), nullable=False)

    category = db.Column(db.Enum(FileCategory), nullable=False)
    display_name = db.Column(db.String(200))


class IntermediateActivity(db.Model, BaseEntity):
    __tablename__ = 'activity'

    picture = db.Column(db.String(255))

    picture_file_id = db.Column(db.Integer, db.ForeignKey('file.id'))
    picture_file = db.relationship(File, foreign_keys=[picture_file_id],
                                   lazy='joined')


def migrate_files():
    picture_dir = 'app/static/activity_pictures/'

    activities = db.session.query(IntermediateActivity).all()

    total = len(activities)
    stepsize = 10

    for i, activity in enumerate(activities):
        if (i + 1) % stepsize == 0:
            print("{}/{}".format(i + 1, total))

        if activity.picture is None:
            continue

        path = os.path.join(picture_dir, activity.picture)
        if not os.path.isfile(path):
            print("File does not exist:", path)

            activity.picture_file = None
            continue

        with open(path, 'rb') as file_reader:
            address = hashfs.put(file_reader)

        f = File()
        f.category = FileCategory.ACTIVITY_PICTURE
        f.hash = address.id

        m = filename_regex.match(activity.picture)
        if m is not None:
            f.extension = m.group(2).lower()
        else:
            f.extension = ""

        activity.picture_file = f

        db.session.add(f)

    db.session.commit()


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('activity', sa.Column('picture_file_id', sa.Integer(), nullable=True))
    op.create_foreign_key(op.f('fk_activity_picture_file_id_file'), 'activity', 'file', ['picture_file_id'], ['id'])

    # Change ACTIVITY_PICTURES -> ACTIVITY_PICTURE
    op.alter_column('file', 'category',
                    existing_type=mysql.ENUM('UPLOADS', 'EXAMINATION', 'ACTIVITY_PICTURE', 'ALV_DOCUMENT', 'COMPANY_LOGO', 'USER_AVATAR'),
                    nullable=False)

    try:
        migrate_files()
    except:
        op.drop_constraint(op.f('fk_activity_picture_file_id_file'), 'activity', type_='foreignkey')
        op.drop_column('activity', 'picture_file_id')
        raise

    op.drop_column('activity', 'picture')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    raise Exception("Undoing this migration is impossible")

    op.add_column('activity', sa.Column('picture', mysql.VARCHAR(length=255), nullable=True))
    op.drop_constraint(op.f('fk_activity_picture_file_id_file'), 'activity', type_='foreignkey')
    op.drop_column('activity', 'picture_file_id')
    # ### end Alembic commands ###


# vim: ft=python
