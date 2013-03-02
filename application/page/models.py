import datetime

from application import db

class Page(db.Model):
	__tablename__ = 'page'

	id = db.Column(db.Integer, primary_key=True)
	path = db.Column(db.String(256), unique=True)
	revisions = db.relationship('PageRevision', backref='page', lazy='dynamic')

	def __init__(self, path):
		self.path = path

	def get_most_recent_revision(self):
		page = self.revisions.order_by(PageRevision.timestamp.desc()).first()
		if page is not None:
			page.path = self.path
		return page

	@classmethod
	def get_all_pages(self):
		pages = map(lambda x: x.get_most_recent_revision(), Page.query.all())
		return filter(lambda x: x is not None, pages)



class PageRevision(db.Model):
	__tablename__ = 'page_revision'

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(128))
	content = db.Column(db.Text)
	timestamp = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	page_id = db.Column(db.Integer, db.ForeignKey('page.id'))

	def __init__(self, page, author, title, content,
		timestamp=datetime.datetime.utcnow()):
		self.title = title
		self.path = ''
		self.content = content
		self.user_id = author.id
		self.page_id = page.id
		self.timestamp = timestamp

class PagePermission(db.Model):
	__tablename__ = 'page_permission'

	id = db.Column(db.Integer, primary_key=True)
	view = db.Column(db.Boolean)
	create = db.Column(db.Boolean)
	edit = db.Column(db.Boolean)
	delete = db.Column(db.Boolean)
	page_id = db.Column(db.Integer, db.ForeignKey('page.id'))
	group_id = db.Column(db.Integer, db.ForeignKey('group.id'))

	def __init__(self, group, page, view=False, create=False, edit=False,
		delete=False):
		self.view = view
		self.create = create
		self.edit = edit
		self.delete = delete
		self.group_id = group.id
		self.page_id = page.id

	@staticmethod
	def get_user_rights(user, page_path):
		rights = {'view': False, 'create': False, 'edit': False,
			'delete': False}
		groups = user.groups.all()

		for group in groups:
			current_path = page_path

			while True:
				page = Page.query.filter(Page.path==current_path).first()

				if page:
					permissions = group.page_permissions.filter(Page.id==page.id).first()

					if permissions:
						rights['view'] = rights['view'] or permissions.view
						rights['create'] = rights['create'] or permissions.create
						rights['edit'] = rights['edit'] or permissions.edit
						rights['delete'] = rights['delete'] or permissions.delete

						break

				if len(current_path) == 0:
					break

				if not '/' in current_path:
					current_path = ''
				else:
					current_path = current_path.rsplit('/', 1)[0]

		return rights

