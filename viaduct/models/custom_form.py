from viaduct import db
import datetime

class CustomForm(db.Model):
	__tablename__ = 'custom_form'

	id				= db.Column(db.Integer, primary_key=True)
	owner_id		= db.Column(db.Integer, db.ForeignKey('user.id'))
	name			= db.Column(db.String(256))
	origin			= db.Column(db.String(4096))
	html			= db.Column(db.UnicodeText())
	msg_success = db.Column(db.String(2048))
	max_attendants	= db.Column(db.Integer)
	created			= db.Column(db.DateTime, default=datetime.datetime.now())
	price			= db.Column(db.Float)
	owner			= db.relationship('User', backref=db.backref('custom_forms', lazy='dynamic'))
	transaction_description = db.Column(db.String(256))

	def __init__(self, owner_id=None, name="", origin="", html="", msg_success="", max_attendants=150):
		self.owner_id = owner_id
		self.name = name
		self.origin = origin
		self.html = html
		self.msg_success	= msg_success
		self.max_attendants = max_attendants

class CustomFormResult(db.Model):
	__tablename__ = 'custom_form_result'

	id				= db.Column(db.Integer, primary_key=True)
	owner_id	= db.Column(db.Integer, db.ForeignKey('user.id'))
	form_id		= db.Column(db.Integer, db.ForeignKey('custom_form.id'))
	transaction_id = db.Column(db.Integer, db.ForeignKey('mollie_transaction.id'))
	data			= db.Column(db.String(4096))
	is_reserve = db.Column(db.Boolean)
	has_payed	= db.Column(db.Boolean)
	created		= db.Column(db.DateTime, default=datetime.datetime.now())

	owner = db.relationship('User', backref=db.backref('custom_form_results', lazy='dynamic'))
	form  = db.relationship('CustomForm', backref=db.backref('custom_form_results', lazy='dynamic'))
	transaction = db.relationship('Transaction', backref=db.backref('custom_form_results', lazy='dynamic'))

	def __init__(self, owner_id=None, form_id=None, data="", is_reserve=False, has_payed=False, transaction_id=None, price=0.0):
		self.owner_id = owner_id
		self.form_id = form_id
		self.data = data
		self.is_reserve = is_reserve
		self.has_payed = has_payed

	def __repr__(self):
		return "<FormResult owner:%s has_payed:%s>" % (self.owner.first_name, self.has_payed)

class CustomFormFollower(db.Model):
	__tablename__ = 'custom_form_follower'

	id				= db.Column(db.Integer, primary_key=True)
	owner_id	= db.Column(db.Integer, db.ForeignKey('user.id'))
	form_id		= db.Column(db.Integer)

	owner = db.relationship('User', backref=db.backref('custom_form_follower', lazy='dynamic'))

	def __init__(self, owner_id=None, form_id=None):
		self.owner_id = owner_id
		self.form_id = form_id

