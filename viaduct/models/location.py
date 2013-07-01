from viaduct import db

class Location(db.Model):
	__tablename__ = 'location'

	id = db.Column(db.Integer, primary_key=True)
	city = db.Column(db.String(256))
	country = db.Column(db.String(256))
	address = db.Column(db.String(256))
	zip = db.Column(db.String(32))
	postoffice_box = db.Column(db.String(32))
	email = db.Column(db.String(256), unique=True)
	phone_nr = db.Column(db.String(64))

	def __init__(self, city, country, address, zip, postoffice_box, email,
			phone_nr):
		self.city = city
		self.country = country
		self.address = address
		self.zip = zip
		self.postoffice_box = postoffice_box
		self.email = email
		self.phone_nr = phone_nr