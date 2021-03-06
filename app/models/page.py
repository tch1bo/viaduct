import sys

from flask_babel import lazy_gettext as _
from sqlalchemy import event
from typing import Dict, Any, Optional

from app import db, get_locale
from app.models.base_model import BaseEntity


class Page(db.Model, BaseEntity):
    __tablename__ = 'page'

    path = db.Column(db.String(200), unique=True)
    needs_paid = db.Column(db.Boolean)
    custom_read_permission = db.Column(db.Boolean)

    type = db.Column(db.String(256))

    def __init__(self, path, type='page'):
        self.path = path.rstrip('/')
        self.type = type

        # Store the page's revision class, based upon its type.
        self.revision_cls = self.get_revision_class()

    def __repr__(self):
        return '<Page(%s, "%s")>' % (self.id, self.path)

    def get_latest_revision(self):
        """Get the latest revision of this page."""
        revision = self.revision_cls.get_query()\
            .filter(self.revision_cls.page_id == self.id)\
            .order_by(self.revision_cls.id.desc())\
            .first()

        return revision

    def get_revision_class(self):
        """Turn a page's type into a revision class."""
        if not self.type:
            return None

        class_name = '%sRevision' % (self.type.capitalize())
        try:
            revision_class = getattr(
                sys.modules['app.models.%s' % (self.type)], class_name)
        except AttributeError:
            return None

        return revision_class

    @staticmethod
    def strip_path(path):
        return path.rstrip('/')


@event.listens_for(Page, 'load')
def set_revision_class(page, context):
    """Calculate revision class."""
    page.revision_cls = page.get_revision_class()


class SuperRevision(db.Model, BaseEntity):
    """
    Contains all general revision fields, as well as some helper functions.

    Any revision class should inherit from this one.
    NOTE: I am not able to get a relationship to work with page here, so you
    will have to implement that yourself.
    """

    __abstract__ = True

    # Things needed in template context.
    context: Dict[str, Any] = {}

    nl_title = db.Column(db.String(128))
    en_title = db.Column(db.String(128))
    comment = db.Column(db.String(1024))

    def __init__(self, nl_title, en_title, comment):
        self.title = None
        self.nl_title = nl_title
        self.en_title = en_title
        self.comment = comment

    def get_comparable(self):
        """Compare titles, as long as no alternative comparable is given."""
        return self.title

    @classmethod
    def get_query(cls):
        return cls.query.order_by(cls.id.desc())


class PageRevision(SuperRevision):
    __tablename__ = 'page_revision'

    filter_html = db.Column(db.Boolean)
    nl_content = db.Column(db.Text)
    en_content = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('page_edits',
                                                      lazy='dynamic'))

    custom_form_id = db.Column(db.Integer, db.ForeignKey('custom_form.id'))
    custom_form = db.relationship('CustomForm',
                                  backref=db.backref('page_revision',
                                                     lazy='dynamic'))

    page_id = db.Column(db.Integer, db.ForeignKey('page.id'))
    page = db.relationship('Page', backref=db.backref('page_revisions',
                                                      lazy='dynamic',
                                                      cascade='all,delete'))

    def __init__(self, page: Optional[Page], nl_title, en_title, comment, user,
                 nl_content, en_content, filter_html=True,
                 custom_form_id=None) -> None:
        super(PageRevision, self).__init__(nl_title, en_title, comment)

        self.page = page

        self.filter_html = filter_html
        self.custom_form_id = custom_form_id
        self.content: Optional[str] = None
        self.nl_content = nl_content
        self.en_content = en_content
        self.user_id = user.id if user else None

    def get_comparable(self):
        return self.content


@event.listens_for(PageRevision, 'load')
def set_page_revision_locale(page_rev, context):
    """
    Load the correct info in the model.

    This function is called after an PageRevision model is filled with data
    from the database, but before is used in all other code.

    Use the locale of the current user/client to determine which language to
    display on the whole website. If the users locale is unavailable, select
    the alternative language, suffixing the title of the activity with the
    displayed language.
    """
    locale = get_locale()
    nl_available = page_rev.nl_title and page_rev.nl_content
    en_available = page_rev.en_title and page_rev.en_content
    if locale == 'nl' and nl_available:
        page_rev.title = page_rev.nl_title
        page_rev.content = page_rev.nl_content
    elif locale == 'en' and en_available:
        page_rev.title = page_rev.en_title
        page_rev.content = page_rev.en_content
    elif nl_available:
        page_rev.title = page_rev.nl_title + " (" + _('Dutch') + ")"
        page_rev.content = page_rev.nl_content
    elif en_available:
        page_rev.title = page_rev.en_title + " (" + _('English') + ")"
        page_rev.content = page_rev.en_content
    else:
        page_rev.title = 'N/A'
        page_rev.content = 'N/A'


class PageReadPermission(db.Model, BaseEntity):
    """Contains page group combinations with use custom read permissions."""

    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    group = db.relationship('Group')

    page = db.relationship('Page')
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'))
