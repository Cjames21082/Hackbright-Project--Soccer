import os
import psycopg2
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import ForeignKey, Table, Column
from sqlalchemy import Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy


# Connection
ENGINE = create_engine('postgresql+psycopg2:///hackbright', echo = False)
session = scoped_session(sessionmaker(bind = ENGINE, autocommit = False, autoflush = False))

# Declare a mapping
Base = declarative_base()
# Create a Session: talking to the database
Base.query = session.query_property()

#Global variables
ROLE_USER = 0
ROLE_TEAMLEADER = 1
ROLE_ADMIN = 2

###   Start class declarations

class User(Base):
	# one to many
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

	# creates a one to many relationship and vice versa
	positions = relationship('Position', backref=backref('user', lazy='joined'))

	def list_positions(self):
		positions=[]

		for position in self.positions:
			positions.append(position.position_type)

		return ",".join(positions)


	
	#creates the relationship to HealthType thru 
	# a many to many view
	health_issues = relationship('HealthType',
				secondary= 'users_health',
				backref=backref('user', lazy='joined'))

	# proxy the 'issue' attribute from the 'health_issues' relationship
	# to view health issues joined by the UserHealth table
	health_types = association_proxy('health_issues','issue')

	@hybrid_property
    	def fullname(self):
        	return self.firstname + " " + self.lastname

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return unicode(self.id)


	def __repr__(self):
		return '<User %r>' %(self.fullname)


class Position(Base):
	#many to one table
	__tablename__='positions'
	id = Column(Integer, primary_key=True) 
	user_id = Column(Integer, ForeignKey('users.id'))
	position_type = Column(String(64))

	def __repr__(self):
		return '<Position %r>' %(self.position_type)

class HealthType(Base):
	# one to many
	__tablename__= 'health_types'
	id = Column(Integer, primary_key=True) 
	issue = Column('issue', String(64))

	def __repr__(self):
		return '<HealthType %r>' %(self.issue)
	
class UserHealth(Base):
	__tablename__='users_health'
	id = Column(Integer, primary_key=True) 
	user_id = Column(Integer, ForeignKey('users.id'))
	health_id = Column(Integer, ForeignKey('health_types.id'))
	
# #many to many - VIEW
# health_table = Table('users_health', Base.metadata,
# 	Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
# 	Column('health_id', Integer, ForeignKey('health_types.id'), primary_key= True)
# )

###  End class declarations
	

def main():
    """In case we need this for something"""
    pass
  
if __name__ == "__main__":
    main()


