from flask import Flask, render_template, redirect, flash, session, url_for, request, g
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from forms import LoginForm, RegisterForm, SeasonCycleForm, EditProfileForm
from server import app
from model import ROLE_ADMIN, ROLE_TEAMLEADER, ROLE_USER
import model
from datetime import datetime


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
	# to update the last access time for user 
	# when user has to login again
	if current_user.is_authenticated():
		current_user.last_seen = datetime.utcnow()
		model.session.add(current_user)
		model.session.commit()

### End LoginHandler settings

@app.route('/assign_role', methods=["GET", "POST"])
@login_required
def role_assignment():
	users = model.session.query(model.User).\
			order_by(model.User.willing_teamLeader)
	
	if request.method == "GET":
		admins= users.filter(model.User.role == ROLE_ADMIN)
		captains = users.filter(model.User.role == ROLE_TEAMLEADER)

		return render_template("assign_role.html", 
								users= users,
								admins= admins,
								captains= captains)

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
		
	return redirect("assign_role")

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

@app.route('/')

@app.route('/index')
def homepage():

	return render_template('index.html',
							title='Homepage')

@app.route('/login', methods=['GET','POST'])
def login():
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

		return redirect(request.args.get("next") or url_for('user'))
		
	
	return render_template('login.html',
							title='Sign In',
							form=form)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect('index')

@app.route('/register', methods=['GET','POST'])
def register():
	form = RegisterForm()

	if request.method =="GET":
		return render_template('register.html',
							title='Register',
							form=form)

	if request.method =="POST":
		if form.validate_on_submit():
		# check if email already exists
			email_exists = model.session.query(model.User).filter_by(email = form.email.data).first()
		
			if email_exists == None:
				
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
									  gender= form.gender.data,
									  fitness=int(form.fitness.data),
									  experience= int(form.experience.data),
									  willing_teamLeader=form.willing_teamLeader.data))
			    # add user
				model.session.commit()

				user = model.session.query(model.User).filter_by(email = form.email.data).first()
				user_id = user.id

				# Add positions
				if form.positions.data == []:
					model.session.add(model.Position(user_id= user_id, position_type= 'none'))
				else:
					for value in form.positions.data:
						model.session.add(model.Position(user_id= user_id, position_type= value))
				# print form.health.data	

				# Add health_issues	
				for value in form.health.data:
					model.session.add(model.UserHealth(user_id=user_id, health_id=int(value)))

				model.session.commit()
				
				flash("You are registered")
		   		#user must login with new email/password
				return redirect('login')
				
			else:
				flash('Email already exists')
				# print form.errors

		return render_template('register.html', title="Register", form=form)


@app.route('/seasons', methods=['GET','POST'])
@login_required
def create_season():
	# generate list for Past Cycle Dropdown
	all_cycles = model.session.query(model.SeasonCycle).all()

	# load form to create new season_cycle
	form =SeasonCycleForm()

	if request.method =="GET":
		cycle_id = request.args.get("cycle_history")

		if cycle_id != None:
			# From user input retrieve selected cycle
			past_cycle = model.session.query(model.SeasonCycle).get(int(cycle_id))
			#print past_cycle

			return render_template('seasoncycle.html',
									title='SeasonCycle',
									form=form,
									all_cycles= all_cycles,
									past_cycle= past_cycle)

	if request.method =="POST":
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
										  reg_end= form.reg_end.data))	
			#print form.errors	
				
			model.session.commit()
			flash("Cycle created")
			return redirect('seasons')

	return render_template('seasoncycle.html',
						title='SeasonCycle',
						form=form,
						all_cycles= all_cycles)


@app.route('/user')
@login_required
def user():
	# user= model.session.query(model.User).\
	# 	  filter_by(model.User.email == email).first()

	if current_user == None:
	   flash('User' + current_user.fullname + 'not found')
	   return redirect(url_for('index'))


	other_users= model.session.query(model.User).all()
	#print other_users

	#stub function
	posts = [
		{ 'author': current_user, 'body':'I\'m awesome!'},
		{ 'author': current_user, 'body':'His shots have fire'}
	]
	
	return render_template('user.html',
							title= 'Profile',
							user=current_user, 
							posts=posts,
							other_users=other_users)

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
	
# End Filters


	# Note: This query only works if all three filters are not "all" or 0
	# users = model.session.query(model.Users).\
	# 		join(model.Position, model.User.id == model.Position.user_id).\
	# 		join(model.UserHealth, model.User.id == model.UserHealth.user_id).\
	# 		filter(model.Position.position_type == position).\
	# 		filter(model.UserHealth.health_id == int(health)).\
	# 		filter(model.User.fitness == int(fitness)).all()

	return render_template('view_players.html', 
							title='View Players',
							users=users,
							health_issues=health_issues)