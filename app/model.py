import os
# postgres connection
import psycopg2
#sqlalchemy properties
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import ForeignKey, Table, Column
from sqlalchemy import Integer, String, DateTime, Boolean, Float, Date
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy

# avatar image
from hashlib import md5
#matching algorithm
import eloalgorithm
# timestamp default
from datetime import datetime, date

#--------End Imports-----------------#


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
	gender = Column(String(64), index=True)
	fitness = Column(Integer, index=True)
	experience = Column(Integer, index=True)
	dob = Column(Date)
	willing_teamLeader = Column(Boolean, default=False)
	about_me= Column(String(140))
	last_seen= Column(DateTime)
	user_disabled= Column(Boolean, default=False)
	user_registered=Column(Boolean, index= True, default=False)

	initial_rating = 1400


	#--------Relationship to Other Tables--------#

	# creates a one to many relationship and vice versa
	positions = relationship('Position', backref=backref('user', lazy='joined'))

	posts = relationship('Post', backref=backref('user', lazy='joined'))

	ratings = relationship('PlayerRating', backref=backref('user', lazy='joined'))

	team = relationship('TeamMember', backref=backref('user', lazy='joined'))
	
	#creates the relationship to HealthType thru 
	# a many to many view
	health_issues = relationship('HealthType',
				secondary= 'users_health',
				backref=backref('user', lazy='joined'))

	# proxy the 'issue' attribute from the 'health_issues' relationship
	# to view health issues joined by the UserHealth table
	health = association_proxy('health_issues','issue')


	#--------------End Relationships----------------#

	#-----------User Functions----------------------#
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

	def show_posts(self):
		# This is a query
		return session.query(Post).\
			filter(Post.user_id == self.id).\
			order_by(Post.timestamp.desc())


	# admin function to assign roles--#
	def update_role(self, new_role):
		self.role = new_role

	def undo_role(self):
		self.role = ROLE_USER
	#---End admin functions-----------#

	# this is a user related task, thus goes in User class
	# https://en.gravatar.com/site/implement/images
	def avatar(self, size):
		return ('http://www.gravatar.com/avatar/' + 
				 md5(self.email).hexdigest() +
				'?d=identicon&s=' + str(size)
				)
	#---------Algorithms functions---------------#

	def getRating(self):
		
		query= session.query(PlayerRating).\
					  join(User, User.id == PlayerRating.player_id).\
					  filter(User.id == self.id).\
					  order_by(PlayerRating.player_rating.desc()).\
					  first()

		if query == None:
			session.add(PlayerRating(player_id =self.id,
									 player_rating= self.getStrength() + self.initial_rating))
			session.commit()
			last = self.getRating()
		else:
			last= query.player_rating

		return last

	def getStrength(self):
	# strength is a calculation of age, fitness, 
	# likely injury, and years experience
	# the strength remains constant during a season_cycle
		
		fitness = calculate_fitness(self.fitness)
		experience = calculate_experience(self.experience)
		
		health_conversion= 'none'
		for h in self.health:
			if h != 'none':
			  health_conversion = len(self.health_issues)
			else:
				break
		
		health = calculate_health(health_conversion)
		
		return fitness + experience + health
	

	#------End User Algorithm Functions--------#


class Game(Base):
	__tablename__= "games"
	id = Column(Integer, primary_key=True) 
	game_date = Column(DateTime)
	home_team = Column(Integer, ForeignKey('teams.id'))
	away_team = Column(Integer, ForeignKey('teams.id'))
	home_score = Column(Integer)
	away_score = Column(Integer)

class HealthType(Base):
	# one to many table
	__tablename__= 'health_types'
	id = Column(Integer, primary_key=True) 
	issue = Column('issue', String(64))

	def __repr__(self):
		return '<HealthType %r>' %(self.issue)


class PlayerRating(Base):
	""" Stores the final calculation of a player's rating
	 by game based on wins/loss/tie. 
	 Calculated using a percentage amt from team's calculation """
	 # many to on table
	__tablename__= "player_ratings"
	id = Column(Integer, primary_key=True)
	team_id = Column(Integer, ForeignKey('teams.id'))
	game_id = Column(Integer, ForeignKey('games.id'))
	player_id= Column(Integer, ForeignKey('users.id'))
	player_rating = Column(Integer)


class PlayerStat(Base):
	#many to one table
	__tablename__ = "player_stats"
	id = Column(Integer, primary_key=True)
	game_id = Column(Integer, ForeignKey('games.id'))
	player_id= Column(Integer, ForeignKey('users.id'))
	goals = Column(Integer)
	absence = Column(Boolean, default = False)
	goalie_win = Column(Boolean, default = False)
	goalie_loss = Column(Boolean, default = False)
	assists= Column(Integer)
	strength= Column(Integer)


class Position(Base):
	#many to one table
	__tablename__='positions'
	id = Column(Integer, primary_key=True) 
	user_id = Column(Integer, ForeignKey('users.id'))
	position_type = Column(String(64), index= True)

	def __repr__(self):
		return '<Position %r>' %(self.position_type)


class Post(Base):
	# many to one table
	__tablename__= 'posts'
	id= Column(Integer, primary_key=True)
	body= Column(String(140))
	timestamp = Column(DateTime, default= datetime.utcnow())
	user_id = Column(Integer, ForeignKey('users.id'))

	def __repr__(self):
		return '<Post %r>' %(self.body)


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
	active = Column(Boolean, default=False)


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

	

	def getRating(self):
		
		last= session.query(TeamRating).\
					  join(Team, Team.id == TeamRating.team_id).\
					  filter(Team.id == self.id).\
					  order_by(TeamRating.team_rating.desc()).\
					  first()

		return last.team_rating


class TeamMember(Base):
	""" Connects the user(player) to a team"""
	# many to many table
	__tablename__= 'team_members'
	id = Column(Integer, primary_key=True)
	team_id= Column(Integer, ForeignKey('teams.id'))
	player_id = Column(Integer, ForeignKey('users.id'))


class TeamRating(Base):
	""" Stores the final calculation of a team's rating
	 by game based on wins/loss/tie """
	# many to one table
	__tablename__= "team_ratings"
	id = Column(Integer, primary_key=True)
	team_id = Column(Integer, ForeignKey('teams.id'))
	game_id = Column(Integer, ForeignKey('games.id'))
	team_rating = Column(Integer)


class UserHealth(Base):
	#many to many table
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

#-----------Determine if registration is active--#
def registration():
	registration= None
	active_registration = session.query(SeasonCycle).\
				   		  filter(SeasonCycle.active == True).\
				   		  first()

	if active_registration != None:
	   	return True
	else:
		return False

#---------Functions to calculate Strength---#
def calculate_age(born):
    today = date.today()
    try: 
        birthday = born.replace(year=today.year)
    except ValueError: 
    	print "raised when birth date is February 29", 
    	print "and the current year is not a leap year"
       
        birthday = born.replace(year=today.year, day=born.day-1)
    
    if birthday > today:
        return today.year - born.year - 1
    else:
        return today.year - born.year

def calculate_fitness(fitness):
	if fitness == 3:
		return 50
	elif fitness == 2:
		return 30
	else:
		return 20

def calculate_health(health):
	if health == 'none':
		return 50
	else:
		# health converted to a number of issues
		return health * (-15)

def calculate_experience(experience):
	new_experience = max(0, min(experience, 10))

	return new_experience * 10



def main():
    """In case we need this for something"""
    pass
  
if __name__ == "__main__":
    main()


