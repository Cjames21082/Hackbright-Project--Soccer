import os
# postgres connection
import psycopg2
#sqlalchemy properties
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy import ForeignKey, Table, Column
from sqlalchemy import Integer, String, DateTime, Boolean, Float, Date
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy

# avatar image
from hashlib import md5
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
	positions = relationship('Position', backref=backref('users', lazy='joined'))

	posts = relationship('Post', backref=backref('user', lazy='joined'))

	ratings = relationship('PlayerRating', backref=backref('user', lazy='joined'))

	teams = relationship('TeamMember', backref=backref('user', lazy='joined'))
	
	stats = relationship('PlayerStat', backref=backref('user',lazy='joined'))
	#creates the relationship to HealthType thru 
	# a many to many view
	health_issues = relationship('HealthType',
				secondary= 'users_health',
				backref=backref('users', lazy='joined'))

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
	game_date = Column(Date)
	home_team = Column(Integer, ForeignKey('teams.id'))
	away_team = Column(Integer, ForeignKey('teams.id'))
	home_score = Column(Integer, default=0)
	away_score = Column(Integer, default=0)
	game_saved = Column(Boolean, default=False)
	home_win = Column(Integer, default=0)
	away_win = Column(Integer, default=0)
	home_tie = Column(Float, default=0.00)
	away_tie = Column(Float, default=0.00)
	home_loss = Column(Integer, default=0)
	away_loss = Column(Integer, default=0)
	home_differential = Column(Float, default=0.00)
	away_differential = Column(Float, default=0.00)
	expectation = Column(Float, default= 0.00)

	game_ratings = relationship('TeamRating', backref=backref('game', lazy='joined'))

	def calculate_score(self):
		if self.home_score > self.away_score:
		   self.home_win = 1
		   self.away_loss = -1
		elif self.away_score > self.home_score:
			self.away_win = 1
			self.home_loss = -1
		else:
			self.home_tie = 0.50 
			self.away_tie = 0.50
		
		session.add(self)		

	

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
	goals = Column(Integer, default= 0)
	absence = Column(Boolean, default = False)
	goalie_win = Column(Boolean, default = False)
	goalie_loss = Column(Boolean, default = False)
	assists= Column(Integer, default= 0)
	strength= Column(Integer, default= 0)
	stat_saved=Column(Boolean, default=False)
	
	def calculate_stat(self):
		if self.goals != 0:
			goals = self.goals * 20
		else:
			goals = 0

		if self.absence == False:
			absence = 1
		else:
			absence = 0

		if self.goalie_win == False:
			goalie_win = 0
		else:
			goalie_win =50

		if self.goalie_loss == False:
			goalie_loss = 0
		else:
			goalie_loss =-50

		if self.assists != 0:
			assists = self.assists * 10
		else:
			assists = 0

		self.strength = (goals + goalie_win + goalie_loss + assists)* absence
		session.add(self)


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
	# disable registration links
	active = Column(Boolean, default=False)
	# disable changing teams
	saved = Column(Boolean, default=False)


class Team(Base):
	# one to many table
	__tablename__= 'teams'
	id = Column(Integer, primary_key=True)
	seasoncycle= Column(Integer, ForeignKey('season_cycles.id'))
	teamname= Column(String(64))
	team_wins= Column(Integer, default=0)
	team_ties= Column(Integer, default=0)
	team_losses= Column(Integer, default=0)
	team_goals= Column(Integer, default=0)

	ratings = relationship('TeamRating', backref=backref('team', lazy='joined'))

	members = relationship('TeamMember', backref=backref('team', lazy='joined'))


	def __repr__(self):
		return '<Team %r>' %(self.teamname)

	def initialRating(self):
		first_rating = 0

		teamMembers = session.query(TeamMember).\
					  filter(TeamMember.team_id == self.id).all()

		for member in teamMembers:
			first_rating = member.user.getRating()

		session.add(TeamRating(team_id= self.id,
							   team_rating=first_rating))

		session.commit()
		
	def getRating(self):
		
		query = session.query(TeamRating).\
					  join(Team, Team.id == TeamRating.team_id).\
					  filter(TeamRating.team_id == self.id).\
					  order_by(TeamRating.team_rating.desc()).\
					  first()

		if query == None:
			self.initialRating()
			return self.getRating()
		

		return query.team_rating


class TeamMember(Base):
	""" Connects the user(player) to a team"""
	# many to many table
	__tablename__= 'team_members'
	id = Column(Integer, primary_key=True)
	team_id= Column(Integer, ForeignKey('teams.id'))
	player_id = Column(Integer, ForeignKey('users.id'))
	team_leader = Column(Integer, default= 0)


class TeamRating(Base):
	""" Stores the final calculation of a team's rating
	 by game based on wins/loss/tie """
	# many to one table
	__tablename__= "team_ratings"
	id = Column(Integer, primary_key=True)
	team_id = Column(Integer, ForeignKey('teams.id'))
	game_id = Column(Integer, ForeignKey('games.id'))
	team_rating = Column(Integer, default=0)
	


class UserHealth(Base):
	#many to many table
	__tablename__='users_health'
	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey('users.id'))
	health_id = Column(Integer, ForeignKey('health_types.id'))	
###  End class declarations


#----------- Common Queries --------------------#

def current_season():
	cycle = session.query(SeasonCycle).\
		   order_by(SeasonCycle.id.desc()).first()
    
    #return last cycle record
	return cycle

def current_teams():
	#scalar(): to just read the first column of the first row and then close the result
	cycle = session.query(func.max(SeasonCycle.id)).scalar()
	
	query= session.query(Team).\
    	join(SeasonCycle,Team.seasoncycle == cycle).\
    	join(TeamMember, TeamMember.team_id == Team.id).all()
    
    #return current season teams with members
	return query

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

#-------------Modify Rating---------#
def getExpectation(home_rating, away_rating):
    calc = (1.0 / (1.0 + pow(10, ((home_rating- away_rating) / 400))));
    return calc
 
def modifyTeamRating(current_rating, expected, actual, kfactor):
	return modifyRating(current_rating, expected, actual, kfactor)

def modifyPlayerRating(last_rating, expected, actual,strength, team_points, kfactor):
		current_rating = last_rating + strength + team_points 
		return modifyRating(current_rating, expected, actual, kfactor)

def modifyRating(current_rating, expected, actual, kfactor):
	calc = (current_rating + kfactor * (actual - expected))
	return calc


#-------Calling module ------------#
def main():
    """In case we need this for something"""
    pass
  
if __name__ == "__main__":
    main()


