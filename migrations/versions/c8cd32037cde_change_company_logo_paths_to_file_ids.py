"""Change company logo paths to file ids.

Revision ID: c8cd32037cde
Revises: f05f7c8518a3
Create Date: 2018-03-25 19:36:52.617750

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

import os
import re

from app import app
from app import hashfs
from app.enums import FileCategory
from app.models.base_model import BaseEntity

# revision identifiers, used by Alembic.
revision = 'c8cd32037cde'
down_revision = 'f05f7c8518a3'

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


class IntermediateCompany(db.Model, BaseEntity):
    __tablename__ = 'company'

    name = db.Column(db.String(200), unique=True)
    logo_path = db.Column(db.String(256))
    logo_file_id = db.Column(db.Integer, db.ForeignKey('file.id'))
    logo_file = db.relationship(File, foreign_keys=[logo_file_id],
                                lazy='joined')


def migrate_files():
    print("Migrating all company logos to HashFS")

    companies = db.session.query(IntermediateCompany).all()
    logos_dir = app.config['UPLOAD_DIR']

    total = len(companies)
    stepsize = 5

    for i, company in enumerate(companies):
        if (i + 1) % stepsize == 0:
            print("{}/{}".format(i + 1, total))

        if company.logo_path is None:
            continue

        path = os.path.join(logos_dir, company.logo_path)

        if not os.path.isfile(path):
            if company.logo_path != '#':
                print("File does not exist:", path)

            company.logo_file = None
            continue

        with open(path, 'rb') as file_reader:
            address = hashfs.put(file_reader)

        f = File()
        f.category = FileCategory.COMPANY_LOGO
        f.hash = address.id

        m = filename_regex.match(company.logo_path)
        if m is not None:
            f.extension = m.group(2).lower()
        else:
            f.extension = ""

        company.logo_file = f

        db.session.add(f)

    db.session.commit()


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('company', sa.Column('logo_file_id', sa.Integer(), nullable=True))
    op.create_foreign_key(op.f('fk_company_logo_file_id_file'), 'company', 'file', ['logo_file_id'], ['id'])

    try:
        migrate_files()
    except Exception as e:
        op.drop_constraint(op.f('fk_company_logo_file_id_file'), 'company',
                           type_='foreignkey')
        op.drop_column('company', 'logo_file_id')
        raise e


    op.drop_column('company', 'logo_path')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    raise Exception("Undoing this migration is impossible")

    op.add_column('company', sa.Column('logo_path', mysql.VARCHAR(length=256), nullable=True))
    op.drop_constraint(op.f('fk_company_logo_file_id_file'), 'company', type_='foreignkey')
    op.drop_column('company', 'logo_file_id')
    # ### end Alembic commands ###


# vim: ft=python
