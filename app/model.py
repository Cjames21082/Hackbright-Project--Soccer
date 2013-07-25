from app import db

ROLE_USER = 0
ROLE_TEAMLEADER = 1
ROLE_ADMIN = 2

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	firstname = db.Column(db.String(64))
	lastname = db.Column(db.String(64))
	email = db.Column(db.String(120), index=True, unique=True)
	password = db.Column(db.String(64),index=True, unique=True)
	address = db.Column(db.String(120))
	city = db.Column(db.String(64))
	state = db.Column(db.String(64))
	zipcode = db.Column(db.String(64))
	country = db.Column(db.String(64))
	role = db.Column(db.SmallInteger, default= ROLE_USER)
	dob = db.Column(db.DateTime(64))
	gender = db.Column(db.SmallInteger)
	fitness = db.Column(db.SmallInteger)
	experience = db.Column(db.Integer)
	willing_teamLeader = db.Column(db.Boolean, default=False)

	positions = db.relationship('Position', backref = 'player')
	issues = db.relationship('UserHealth',backref='player')


	def __repr__(self):
		return '<User %r %r>' %(self.firstname, self.lastname)

class Position(db.Model):
	id = db.Column(db.Integer, primary_key=True) 
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	positionType = db.Column(db.String(64))

	def __repr__(self):
		return '<Position %r>' %(self.positionType)

class HealthType(db.Model):
	id = db.Column(db.Integer, primary_key=True) 
	issue = db.Column(db.String(64))

	def __repr__(self):
		return '<HealthType %r>' %(self.issue)

class UserHealth(db.Model):
	id = db.Column(db.Integer, primary_key=True) 
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	health_id = db.Column(db.Integer, db.ForeignKey('health_type.id'))

