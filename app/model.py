import os
import psycopg2
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import ForeignKey, Table, Column
from sqlalchemy import Integer, String, DateTime, Boolean, Float
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy
from hashlib import md5


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
	password = Column(String(64),index=True)
	address = Column(String(120))
	city = Column(String(64))
	state = Column(String(64))
	zipcode = Column(String(64))
	country = Column(String(64))
	role = Column(Integer, default= ROLE_USER)
	dob = Column(DateTime)
	gender = Column(String(64), index=True)
	fitness = Column(Integer, index=True)
	experience = Column(Integer, index=True)
	willing_teamLeader = Column(Boolean, default=False)
	user_disabled= Column(Boolean, default=False)
	about_me= Column(String(140))
	last_seen= Column(DateTime)

	# creates a one to many relationship and vice versa
	positions = relationship('Position', backref=backref('user', lazy='joined'))

	#creates the relationship to HealthType thru 
	# a many to many view
	health_issues = relationship('HealthType',
				secondary= 'users_health',
				backref=backref('user', lazy='joined'))

	# proxy the 'issue' attribute from the 'health_issues' relationship
	# to view health issues joined by the UserHealth table
	health = association_proxy('health_issues','issue')



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

	# function to return a iterable list of positions
	def show_positions(self):
		position_list=[]

		for p in self.positions:
			position_list.append(p.position_type)

		return position_list

	def update_role(self, new_role):
		self.role = new_role

	def undo_role(self):
		self.role = ROLE_USER

	# this is a user related task, thus goes in User class
	# https://en.gravatar.com/site/implement/images
	def avatar(self, size):
		return ('http://www.gravatar.com/avatar/' + 
				 md5(self.email).hexdigest() +
				'?d=identicon&s=' + str(size)
				)

class HealthType(Base):
	# one to many
	__tablename__= 'health_types'
	id = Column(Integer, primary_key=True) 
	issue = Column('issue', String(64))

	def __repr__(self):
		return '<HealthType %r>' %(self.issue)


class Position(Base):
	#many to one table
	__tablename__='positions'
	id = Column(Integer, primary_key=True) 
	user_id = Column(Integer, ForeignKey('users.id'))
	position_type = Column(String(64), index= True)

	def __repr__(self):
		return '<Position %r>' %(self.position_type)


class SeasonCycle(Base):
	#one to one table
	__tablename__='season_cycles'
	id = Column(Integer, primary_key=True)
	admin_id = Column(Integer, ForeignKey('users.id'))
	leaguename = Column(String(64))
	cyclename = Column(String(64))
	num_of_teams= Column(Integer)
	home_region = Column(String(64))
	fee_resident= Column(Float)
	fee_nonresident = Column(Float, default= 0.00)
	reg_start = Column(DateTime)
	reg_end = Column(DateTime)

class UserHealth(Base):
	#many to many table
	__tablename__='users_health'
	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey('users.id'))
	health_id = Column(Integer, ForeignKey('health_types.id'))

class Team(Base):
	# one to many table
	__tablename__= 'teams'
	id = Column(Integer, primary_key=True)
	seasoncycle= Column(Integer, ForeignKey('season_cycles.id'))
	team_leader = Column(Integer, ForeignKey('users.id'))
	teamname= Column(String(64))
	team_wins= Column(Integer)
	team_ties= Column(Integer)
	team_losses= Column(Integer)
	team_goals= Column(Integer)

	def __repr__(self):
		return '<Team %r>' %(self.teamname)

class TeamMember(Base):
	# many to many table
	__tablename__= 'team_members'
	id = Column(Integer, primary_key=True)
	team_id= Column(Integer, ForeignKey('teams.id'))
	player_id = Column(Integer, ForeignKey('users.id'))
	seasoncycle= Column(Integer, ForeignKey('season_cycles.id'))
	
	
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


