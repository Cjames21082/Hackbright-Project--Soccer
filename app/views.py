from flask import Flask, render_template, redirect, flash, session, url_for, request, g

# connection to LoginHandler in Flask
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required

#connection to forms.py
from forms import LoginForm, RegisterForm, RegisterContForm
from forms import PostForm, TeamForm, SeasonCycleForm, EditProfileForm
from forms import TeamCreateForm

# connection to flask object
from server import app

# connection to model.py
from model import ROLE_ADMIN, ROLE_TEAMLEADER, ROLE_USER
import model
import create_team

from datetime import datetime

#import config pagination
from config import POSTS_PER_PAGE


#------------End of Imports--------------#

### Start LoginHandler settings

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

@lm.user_loader
def load_user(id):
	return model.session.query(model.User).get(id)

@app.before_request
def before_request():	
	g.user = current_user

	if current_user.is_authenticated():
		# to update the last access time for user 
		# when user has to login again
		current_user.last_seen = datetime.utcnow()
		model.session.add(current_user)
		model.session.commit()
### End LoginHandler settings


@app.route('/')
def homepage():
	open_registration = model.registration()
	
	return render_template('index.html',
							title='Homepage',
							open_registration= open_registration)

@app.route('/edit', methods=["GET", "POST"])
@login_required
def edit():
	form = EditProfileForm()

	if form.validate_on_submit():
		current_user.firstname = form.firstname.data
		current_user.lastname = form.lastname.data
		current_user.address = form.address.data
		current_user.city = form.city.data
		current_user.state = form.state.data
		current_user.zipcode = form.zipcode.data
		current_user.country = form.country.data
		current_user.about_me = form.about_me.data
		current_user.user_disabled = form.user_disabled.data

		model.session.add(current_user)
		model.session.commit()

		flash('Your changes have been saved!')
		return redirect(url_for('edit'))
		#renders the fields with data from database
	else:
		form.firstname.data= current_user.firstname
		form.lastname.data= current_user.lastname 
		form.address.data= current_user.address 
		form.city.data= current_user.city 
		form.state.data= current_user.state
		form.zipcode.data= current_user.zipcode
		form.country.data= current_user.country
		form.about_me.data= current_user.about_me
		form.user_disabled.data= current_user.user_disabled

	return render_template("edit_profile.html",
							form=form)


@app.route('/login', methods=['GET','POST'])
def login():
	# determine if registration is open; checks flag
	open_registration = model.registration()

	# if user hasn't logged out redirect don't reload login page
	if current_user is not None and current_user.is_authenticated():
		return redirect(url_for('user'))

	form = LoginForm()
	if form.validate_on_submit():

		user= model.session.query(model.User).filter_by(email=form.email.data, password=form.password.data).first()
	
		if user is not None:
			login_user(user)	
			flash("Welcome")
		else:
			flash("Invalid login")

		#pass arg to user profile
		
		return redirect(request.args.get("next") or url_for('user'))
		
	
	return render_template('login.html',
							title='Sign In',
							form=form,
							open_registration= open_registration)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect('/')


@app.route('/post_edit', methods=['POST'])
@login_required
def post_edit():
	
	post= request.form['edit_post']

	#print post

	model.session.query(model.Post).\
	filter(model.Post.id == int(post)).\
	delete()

	model.session.commit()

	return redirect(url_for('user'))



@app.route('/register', methods=['GET','POST'])
def register():
	form = RegisterForm()

	if form.validate_on_submit():
	# check if email already exists
		email_exists = model.session.query(model.User).\
		               filter_by(email = form.email.data).first()
	
		if email_exists != None:
			flash('Email already exists')
			return render_template('register.html', 
				                    title='Register', 
				                    form=form)
		else:
			user = model.session.\
				   add(model.User(firstname= form.firstname.data,
								  lastname= form.lastname.data,
								  email= form.email.data,
								  password= form.password.data,
								  address= form.address.data,
								  city= form.city.data,
								  state= form.state.data,
								  zipcode= form.zipcode.data,
								  country= form.country.data,
								  dob= form.dob.data,
								  gender= form.gender.data))
		    # add user
			model.session.commit()

			flash("Registration almost done. Login to complete.")
		   	#user must login with new email/password
			return redirect(url_for('login'))

	return render_template('register.html',
							title='Register',
							form=form)

@app.route('/register_cont', methods=['GET', 'POST']) # To fix, delete not working properly
@login_required
def register_cont():
	form= RegisterContForm()

	if form.validate_on_submit():

		current_user.fitness = int(form.fitness.data)
		current_user.experience = int(form.experience.data)
		current_user.willing_teamLeader = form.willing_teamLeader.data

		# Add positions
		if form.positions.data == [] and current_user.show_positions != []:
			pass #don't change anything
		
		elif form.positions.data == [] and current_user.show_positions == []:
			model.session.add(model.Position(user_id= current_user.id, position_type= 'none'))
		
		elif form.positions.data != [] and current_user.show_positions != []:
			for old_position in current_user.positions:
				model.session.delete(old_position)

			for value in form.positions.data:
				model.session.add(model.Position(user_id= current_user.id, position_type= value))
		else:
			for value in form.positions.data:
				model.session.add(model.Position(user_id= current_user.id, position_type= value))
	

		# Add health_issues
		if current_user.health_issues != []:
			for issue in current_user.health_issues:
				model.session.delete(issue)

		for value in form.health.data:
			model.session.add(model.UserHealth(user_id=current_user.id, health_id=int(value)))

		current_user.user_registered = True

		model.session.commit()

		#add update to rating
		current_user.getRating()
		
		flash("Registration Complete")
		#user directed to profile page
		return redirect(url_for('user'))
				
	return render_template('register_cont.html', 
							title="RegisterCont", 
							form=form)

@app.route('/seasons', methods=['GET'])
@login_required
def seasons():

	return render_template('season.html',
							title='Season')


@app.route('/seasons_create', methods=['GET', 'POST'])
@login_required
def create_season():
	#load users to reset when new cycle created
	users= model.session.query(model.User).all()

	# load form to create new season_cycle (form)
	form = SeasonCycleForm()

	# create new cycle

	if form.validate_on_submit():
		cycle = model.session.\
				add(model.SeasonCycle(admin_id= current_user.id,
									  leaguename= form.leaguename.data,
									  cyclename= form.cyclename.data,
									  num_of_teams= form.num_of_teams.data,
									  home_region= form.home_region.data,
									  fee_resident= form.fee_resident.data,
									  fee_nonresident= form.fee_nonresident.data,
									  reg_start= form.reg_start.data,
									  reg_end= form.reg_end.data,
									  active= True))	
		#print form.errors		
		model.session.commit()

		# reset all users to false
		for user in users:
			user.user_registered = False

		model.session.commit()
		flash("Cycle created")
		return redirect('seasons')

	
	return render_template('season_create.html',
						title='SeasonCreate',
						form=form)


@app.route('/seasons_edit', methods=['GET','POST'])
@login_required
def edit_season():	
	current_cycle = model.session.query(model.SeasonCycle).\
					filter(model.SeasonCycle.active ==True).\
					first()

	message = ""

	form = SeasonCycleForm()

	# if registration for the last season is closed
	if current_cycle == None:
		message = "Registration is closed. You can no longer edit."
	   
	   	current_cycle = model.session.query(model.SeasonCycle).\
					   	order_by(model.SeasonCycle.id.desc()).\
					   	first()
	
    #Check which submit button is clicked
	if request.form.get("current_season") == 'edit' and form.validate_on_submit() :
		# edit current season if status is active
		current_cycle.leaguename= form.leaguename.data 
		current_cycle.cyclename= form.cyclename.data 
		current_cycle.num_of_teams= form.num_of_teams.data 
		current_cycle.home_region= form.home_region.data 
		current_cycle.fee_resident= form.fee_resident.data
		current_cycle.fee_nonresident= form.fee_nonresident.data
		current_cycle.reg_start= form.reg_start.data
		current_cycle.reg_end= form.reg_end.data 

		model.session.add(current_cycle)
		model.session.commit()
		

		flash('Your changes have been saved!')
		
	else:
		#renders the fields with data from database
		form.leaguename.data= current_cycle.leaguename 
		form.cyclename.data= current_cycle.cyclename
		form.num_of_teams.data= current_cycle.num_of_teams 
		form.home_region.data= current_cycle.home_region
		form.fee_resident.data= current_cycle.fee_resident
		form.fee_nonresident.data= current_cycle.fee_nonresident
		form.reg_start.data= current_cycle.reg_start
		form.reg_end.data= current_cycle.reg_end 
	
		
	if request.form.get("current_season") == 'close':

		
		current_cycle.active = False
		model.session.commit()	
		
		return redirect('seasons_edit')
	

	return render_template("season_edit.html",
						title= 'SeasonEdit',
						form=form,
						current_cycle= current_cycle,
						message=message)


@app.route('/seasons_view', methods=['GET'])
@login_required
def review_season():
	
	# generate list for Past Cycle Dropdown
	all_cycles = model.session.query(model.SeasonCycle).\
				 order_by(model.SeasonCycle.id.desc()).all()
	past_cycle = None
	# load form to create new season_cycle (form)
	form = SeasonCycleForm()
	

	# From user input retrieve selected cycle
	cycle_id = request.args.get("cycle_history")
	
	if cycle_id != None:
		past_cycle = model.session.query(model.SeasonCycle).\
					 get(int(cycle_id))

		form.leaguename.data = past_cycle.leaguename
		form.cyclename.data = past_cycle.cyclename
		form.num_of_teams.data = past_cycle.num_of_teams
		form.home_region.data = past_cycle.home_region
		form.fee_resident.data= past_cycle.fee_resident
		form.fee_nonresident.data= past_cycle.fee_nonresident
		form.reg_start.data= past_cycle.reg_start
		form.reg_end.data = past_cycle.reg_end

	return render_template('season_view.html',
						title='SeasonView',
						form=form,
						all_cycles= all_cycles,
						past_cycle= past_cycle)


@app.route('/teams', methods=['GET'])
@login_required
def teams():

	return render_template('teams.html',
							title='Teams')


@app.route('/team_create', methods=['GET','POST'])
@login_required
def create_teams():

	form= TeamCreateForm()

	team_members = model.session.query(model.TeamMember).\
				   join(model.Team, model.Team.id == model.TeamMember.team_id).\
				   join(model.SeasonCycle, model.Team.seasoncycle == form.cycle.id)
	

	if form.validate_on_submit():
		if team_members != None:
			for member in team_members:
				model.session.delete(member)

			model.session.commit()

		create_team.team_generate(int(form.team_num.data))

	
	return render_template('teams_create.html',
							title='TeamCreate',
							team_members=team_members,
							form=form)


@app.route('/team_names', methods=['GET', 'POST'])
@login_required
def teamname():
	#Determinant for current season
	max_teams = 0
	teams = None
	team_count = 0
	
	current_season = model.session.query(model.SeasonCycle).\
		             order_by(model.SeasonCycle.id.desc()).first()
    
	print current_season.id 

	if current_season is not None:
		# created teams by cycle.id
		teams = model.session.query(model.Team).\
				filter(model.Team.seasoncycle == current_season.id).\
				all()

		team_count= len(teams)

		# number of teams based on season cycle
		max_teams = current_season.num_of_teams

	#Create Team Names
	form = TeamForm()

	if form.validate_on_submit():
	
		new_team = model.session.\
				   add(model.Team(teamname= form.teamname.data,
				   				  seasoncycle= current_season.id))

		model.session.commit()
		return redirect('team_names')

	return render_template('team_names.html',
							title='Teamname',
							form=form,
							max_teams=max_teams,
							teams= teams,
							team_count= team_count,
							current_season=current_season)



@app.route('/team_leaders', methods=['GET','POST'])
@login_required
def role_assignment():
	
	users= model.session.query(model.User).\
		   filter(model.User.user_registered == True)

	

	if request.method == 'GET':
		admins= users.filter(model.User.role == ROLE_ADMIN).all()
		captains = users.filter(model.User.role == ROLE_TEAMLEADER).all()
		count_players = model.session.query(model.User).count()
		

		count_captains = len(captains)
		count_admins = len(admins)


		return render_template("team_leaders.html", 
								users= users,
								admins= admins,
								captains= captains,
								count_players=count_players,
								count_captains= count_captains,
								count_admins= count_admins)

	if request.method == "POST":

		try:
			captain = request.form["captain"]
			player = model.session.query(model.User).get(int(captain))
			player.update_role(ROLE_TEAMLEADER)
			print player.role
		except KeyError:
			pass

		try:
			admin= request.form["admin"]
			player = model.session.query(model.User).get(int(admin))
			player.update_role(ROLE_ADMIN)
			print player.role
		except KeyError:
			pass

		try:
			undo= request.form["undo"]
			player = model.session.query(model.User).get(int(undo))
			player.undo_role()
			print player.role
		except KeyError:
			pass

		model.session.commit()


	return redirect("team_leaders")



@app.route('/team_leaders2', methods=['GET','POST'])
@login_required
def more_captains():
	
	users= model.session.query(model.User).\
		   filter(model.User.user_registered == True)

	if request.method == 'GET':
		admins= users.filter(model.User.role == ROLE_ADMIN).all()
		captains = users.filter(model.User.role == ROLE_TEAMLEADER).all()
		count_players = model.session.query(model.User).count()

		count_captains = len(captains)
		count_admins = len(admins)


		return render_template("team_leaders2.html", 
								users= users,
								admins= admins,
								captains= captains,
								count_players=count_players,
								count_captains= count_captains,
								count_admins= count_admins)

	if request.method == "POST":

		try:
			captain = request.form["captain"]
			player = model.session.query(model.User).get(int(captain))
			player.update_role(ROLE_TEAMLEADER)
			print player.role
		except KeyError:
			pass

		try:
			admin= request.form["admin"]
			player = model.session.query(model.User).get(int(admin))
			player.update_role(ROLE_ADMIN)
			print player.role
		except KeyError:
			pass

		try:
			undo= request.form["undo"]
			player = model.session.query(model.User).get(int(undo))
			player.undo_role()
			print player.role
		except KeyError:
			pass

		model.session.commit()


	return redirect("team_leaders2")


@app.route('/user', methods=['GET','POST'])
@login_required
def user():	

	user_id = request.args.get("user_id")

	if user_id == None:
		user_id = current_user.id

	# enable registration link
	current_cycle = model.session.query(model.SeasonCycle).\
					order_by(model.SeasonCycle.id.desc()).\
					first()
	
	#print current_cycle.cyclename
	
	users= model.session.query(model.User)

	user = users.get(user_id)
	
	form= PostForm()

	if form.validate_on_submit():
		new_post = model.session.\
				   add(model.Post(body=form.post.data,
				   				  user_id= current_user.id))

		model.session.commit()
		flash('Your post is live!')
		return redirect('user')

	return render_template('user.html',
							title= 'Profile',
							users=users,
							user = user,
							current_cycle=current_cycle,
							form=form)


@app.route('/view_players', methods=['GET'])
@login_required
def view_players():
	
	#Start with all users
	users = model.session.query(model.User)
	

	# All healthtypes for dropdwon menu healthtypes
	health_issues = model.session.query(model.HealthType).\
					order_by(model.HealthType.id).all()

	#get filter variables
	position = request.args.get("position")
	print position
	fitness = request.args.get("fitness")
	print fitness
	health = request.args.get("health")
	print health

	### Begin Filter
	if position != "all" and position != None:
		users = users.join(model.Position, model.User.id == model.Position.user_id).\
				filter(model.Position.position_type == position)
	
	if fitness != "0" and position != None:
		users = users.filter(model.User.fitness == int(fitness))

	if health != "0" and position != None:
		users = users.join(model.UserHealth, model.User.id == model.UserHealth.user_id).\
				filter(model.UserHealth.health_id == int(health))
	
	return render_template('view_players.html', 
							title='View Players',
							users=users,
							health_issues=health_issues)