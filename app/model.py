import os
import psycopg2
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker, scoped_session

ENGINE = create_engine('postgresql+psycopg2:///hackbright', echo = False)
session = scoped_session(sessionmaker(bind = ENGINE, autocommit = False, autoflush = False))

ROLE_USER = 0
ROLE_TEAMLEADER = 1
ROLE_ADMIN = 2

Base = declarative_base()
Base.query = session.query_property()


###   Start class declarations

class User(Base):
	__tablename__='users'
	id = Column(Integer, primary_key=True)
	firstname = Column(String(64))
	lastname = Column(String(64))
	email = Column(String(120), index=True, unique=True)
	password = Column(String(64),index=True, unique=True)
	address = Column(String(120))
	city = Column(String(64))
	state = Column(String(64))
	zipcode = Column(String(64))
	country = Column(String(64))
	role = Column(Integer, default= ROLE_USER)
	dob = Column(DateTime)
	gender = Column(String(64))
	fitness = Column(Integer)
	experience = Column(Integer)
	willing_teamLeader = Column(Boolean, default=False)

	positions = relationship('Position', backref = 'player')
	issues = relationship('UserHealth',backref='player')

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return unicode(self.id)

	def __repr__(self):
		return '<User %r %r>' %(self.firstname, self.lastname)


class Position(Base):
	__tablename__='positions'
	id = Column(Integer, primary_key=True) 
	user_id = Column(Integer, ForeignKey('users.id'))
	positionType = Column(String(64))

	def __repr__(self):
		return '<Position %r>' %(self.positionType)

class HealthType(Base):
	__tablename__= 'health_types'

	id = Column(Integer, primary_key=True) 
	issue = Column(String(64))

	user = relationship('UserHealth',backref='issue_type')

	def __repr__(self):
		return '<HealthType %r>' %(self.issue)


class UserHealth(Base):
	__tablename__='users_health'
	id = Column(Integer, primary_key=True) 
	user_id = Column(Integer, ForeignKey('users.id'))
	health_id = Column(Integer, ForeignKey('health_types.id'))

###  End class declarations

def main():
    """In case we need this for something"""
    pass

if __name__ == "__main__":
    main()


