from viaduct import db
import datetime

# many to many relationship tables
task_group = db.Table('pimpy_task_group',
	db.Column('task_id', db.Integer, db.ForeignKey('pimpy_task.id')),
	db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)

task_user = db.Table('pimpy_task_user',
	db.Column('task_id', db.Integer, db.ForeignKey('pimpy_task.id')),
	db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

class Task(db.Model):
	__tablename__ = 'pimpy_task'

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.Text)
	content = db.Column(db.Text)
	deadline = db.Column(db.DateTime)
	timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow())
	line = db.Column(db.Integer)

	minute_id = db.Column(db.Integer, db.ForeignKey('pimpy_minute.id'))

	group_id = db.Column(db.Integer, db.ForeignKey('group.id'))

	group = db.relationship('Group', backref=db.backref('tasks',
		lazy='dynamic'))

	users = db.relationship('User', secondary=task_user,
		backref=db.backref('tasks', lazy='dynamic'), lazy='dynamic')

	status = db.Column(db.Integer)

	status_meanings = ["not started", "started", "done", "checked", "not done",			"removed"]

	def __init__(self, title, content, deadline, group_id, users,
				minute_id, line, status):
		self.title = title
		self.content = content
		self.deadline = deadline
		self.group_id = group_id
		self.line = line
		self.users = users
		self.minute_id = minute_id
		self.status = status

	def get_status_string(self):
		"""
		Returns a string representing the status
		"""
		if self.status >= 0 and self.status < len(self.status_meanings):
			return self.status_meanings[self.status]
		return "unknown"

	def get_users(self):
		"""
		Returns a list of users, comma separated
		"""
		return ", ".join(map(lambda x: "%s %s" % (x.first_name, x.last_name),
			self.users))

class Minute(db.Model):
	__tablename__ = 'pimpy_minute'

	id = db.Column(db.Integer, primary_key=True)
	timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow())
	content = db.Column(db.Text)
	group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
	group = db.relationship('Group', backref=db.backref('minutes',
		lazy='dynamic'))

	tasks = db.relationship('Task', backref='minute', lazy='dynamic')

	def __init__(self, content, group_id):
		self.content = content
		self.group_id = group_id

	def get_title(self):
		return '%s van %s' % (self.group.name, self.timestamp)
