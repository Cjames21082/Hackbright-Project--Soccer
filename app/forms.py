from flask.ext.wtf import Form, validators
from flask.ext.wtf import TextAreaField, FloatField, TextField
from flask.ext.wtf import PasswordField, IntegerField, DateField, SubmitField
from flask.ext.wtf import BooleanField, SelectField, RadioField, SelectMultipleField
import model

class EditProfileForm(Form):
	firstname = TextField('First Name', [validators.Optional()], 
						  description=u'First Name')
	lastname = TextField('Last Name',[validators.Optional()], 
						 description=u'Last Name')
	address= TextField('Address',[validators.Optional()], 
					   description=u'Address')
	city= TextField('City',[validators.Optional()], description=u'City')
	state = TextField('State', [validators.length(max=2), 
								validators.Optional()], description=u'State')
	zipcode = TextField('Zipcode', [validators.Optional()], description=u'Zipcode')
	country = TextField('Country',[validators.Optional()], description=u'Country')
	user_disabled= BooleanField('Taking a break? Disable Account')
	about_me= TextAreaField('About Me', [validators.length(min=0, max=140)],
						description=u'About Me!!')


class GameForm(Form):	
	all_teams = model.current_teams()
		    	
	game_date = DateField('Game Date', [validators.Required(message= (u'Game Date: mm/dd/yyyy'))], 
						 format= '%m/%d/%Y', description=u'Game Date(mm/dd/yyyy)')
	home_team = SelectField('Home', [validators.Required(message=(u'Select Team'))],
							choices=[(str(i.id),i.teamname) for i in all_teams],
							description=u'Home Team')
	away_team = SelectField('Away', [validators.Required(message=(u'Select Team'))],
							choices=[(str(i.id),i.teamname) for i in all_teams],
							description=u'Opponent')
	home_score = IntegerField('Home Score', [validators.Optional()],
						 description=u'Home Score')
	away_score = IntegerField('Away Score', [validators.Optional()],
						 description=u'Opponent Score')


class LoginForm(Form):
	email = TextField('Email',
		              [validators.Email(message= (u'Invalid email address'))])
	password = PasswordField('Password', [validators.Required(), 
							 validators.length(min=6, max=25)])
class PlayerStatForm(Form):
	goals = IntegerField('Goals', [validators.Optional()],
						  description=u'Goals')
	absence = SelectField('Absence', [validators.Required()],
						  choices=[('False','No'), ('True','Yes')],
						  description=u'Absent')
	goalie_win = SelectField('Goalie Win', [validators.Optional()],
						  choices=[('False','No'),('True','Yes'),],
						  description=u'Goalie Win')
	goalie_loss = SelectField('Goalie Loss', [validators.Optional()],
						  choices=[('False','No'),('True','Yes'),],
						  description=u'Goalie Loss')
	assists= IntegerField('Assists', [validators.Optional()],
						  description=u'Assists')
	submit= SubmitField()

class PostForm(Form):
    post = TextAreaField('Post', [validators.Required(), 
    				  validators.length(min=0, max=140)],
    				  description=u'Wanna say something?!')
										  					

class RegisterForm(Form):
	firstname = TextField('First Name', [validators.Required()], 
						  description=u'First Name')
	lastname = TextField('Last Name',[validators.Required()], 
						 description=u'Last Name')
	email = TextField('Email',[validators.Email(message= (u'Invalid email address'))], 
					  description=u'Email')
	password = PasswordField('Password', [validators.Required(), 
							 validators.length(min=6, max=25)],
							 description=u'Password')
	address= TextField('Address',[validators.Required()], 
					   description=u'Address')
	city= TextField('City',[validators.Required()], description=u'City')
	state = TextField('State', [validators.Required(), 
					  validators.length(max=2)], description=u'State')
	zipcode = TextField('Zipcode', [validators.Required()], description=u'Zipcode')
	country = TextField('Country',[validators.Required()], description=u'Country')
	dob = DateField('DOB', [validators.Required(message= (u'Enter birthdate: mm/dd/yyyy'))], 
					format= '%m/%d/%Y', description=u'Date of Birth (mm/dd/yyyy)')
	gender = RadioField('Gender', [validators.Required()], 
						choices=[('male', 'M'),('female','F')], description=u'Gender')
	

class RegisterContForm(Form):
	fitness = SelectField('Fitness Level', [validators.Required()], 
						  choices=[ ('1', 'low'), ('2', 'medium'), ('3', 'high')], 
						  description=u'Fitness Level')
	# need to convert fitness value to int
	
	experience = SelectField('Years Played?', [validators.Required()], 
							 choices=[(str(i),i) for i in range(50)], 
							 description=u'Years Played?')
	# need to covert experience value to int
	
	willing_teamLeader = BooleanField('Team Leader?')
	
	positions = SelectMultipleField(u'Positions', [validators.Required()],
									choices=[ ('none', 'none'),('offense', 'offense'), ('defense', 'defense'), 
											 ('midfield', 'midfield'), ('goalie','goalie')],
									description=u'Positions (Optional)')

	health = SelectMultipleField(u'Health Issues', [validators.Required()],
									choices=[(str(i.id), i.issue) for i in model.session.query(model.HealthType).\
																	order_by(model.HealthType.id).all()],
									description=u'Health Issues')


class ScoreForm(Form):
	home_score = IntegerField('Home Score', [validators.Optional()],
						 description=u'Home Score')
	away_score = IntegerField('Away Score', [validators.Optional()],
						 description=u'Opponent Score')

class SeasonCycleForm(Form):
	leaguename = TextField('League Name', [validators.Required()],
							description=u'League Name')
	cyclename = TextField('Cycle Name', [validators.Required(), 
						   validators.length(min=6, max=25)],
						   description=u'Season Cycle Description')
	num_of_teams = IntegerField('Number Of Teams', [validators.Required()],
								description=u'Max # Teams')
	home_region = TextField('League Name', [validators.Required()],
							description=u'Home Region')
	fee_resident = FloatField('Resident Fee', [validators.Required()],
							  description=u'Resident Fee')
	fee_nonresident = FloatField('Resident Fee', [validators.Optional()],
								  description=u'Nonresident Fee (Optional)') 
	reg_start = DateField('Registration Starts', [validators.Required(message=(u'start date: mm/dd/yyyy'))], 
						   format= '%m/%d/%Y', description=u'Registration Starts (mm/dd/yyyy)')
	reg_end = DateField('Registration Ends', [validators.Required(message= (u'end date: mm/dd/yyyy'))], 
						 format= '%m/%d/%Y', description=u'Registration Ends (mm/dd/yyyy)')

class TeamCreateForm(Form):
	cycle = model.session.query(model.SeasonCycle).order_by(model.SeasonCycle.id.desc()).first()
	teams = model.session.query(model.Team).join(model.SeasonCycle, model.Team.seasoncycle == cycle.id).all()

	team_num = SelectField('Total Teams', [validators.Required()],
							choices=[(str(i),i) for i in range(len(teams)+1)],
							description=u'Select Total Teams')

    

class TeamForm(Form):
	teamname = TextField('Teamname', [validators.Optional()],
						  description=u'Team Name')
	team_leader = IntegerField('Leader_id')



########## End Forms

def length(min=-1, max=-1):
    message = 'Must be between %d and %d characters long.' % (min, max)

    def _length(form, field):
        l = field.data and len(field.data) or 0
        if l < min or max != -1 and l > max:
            raise ValidationError(message)

    return _length