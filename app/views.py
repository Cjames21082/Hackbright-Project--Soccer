from flask import Flask, render_template, redirect, flash, session, url_for, request, g
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from forms import LoginForm, RegisterForm
from app import app
import model


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

### End LoginHandler settings

@app.route('/')
@app.route('/index')
def homepage():
	#user = current_user

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
	
		if user is None:
			flash("Invalid login.")
		else:
			login_user(user)
			flash("Welcome")
		
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
				return redirect('register')


@app.route('/user')
@login_required
def user():

	user = current_user

	other_users= model.session.query(model.User).all()
	#print other_users

	
	return render_template('user.html',
							title= 'Profile',
							user=user, 
							other_users=other_users)

@app.route('/view_players', methods=['GET'])
@login_required
def view_players():

	# Start list with all users
	users = model.session.query(model.User).all()

	filter_once = []
	filter_twice= []
	filter_thrice= []
	
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
	if position != "all":
		for user in users:
			if position in user.show_positions():
				filter_once.append(user)

		users = filter_once  # redefine list of users

		# print "positions:"
		# print users
	

	if fitness != "0":
		for user in users:
			if user.fitness == int(fitness):
				filter_twice.append(user)

		users = filter_twice # redefine list of users
	
		# print "fitness:"
		# print users

	if health != "all":
		for user in users:
			if health in user.health_types:
				filter_thrice.append(user)
			
		users = filter_thrice # redefine list of users
	
		# print "health:"
		# print users

	## End Filters


	# Note: This query only works if all three filters are not "all" or 0
	# users = model.session.query(model.Users).\
	# 		join(model.Positions, model.User.id == model.Position.user_id).\
	# 		join(model.UserHealth, model.User.id == model.UserHealth.user_id).\
	# 		filter(model.Position.position_type == position).\
	# 		filter(model.UserHealth.health_id == int(health)).\
	# 		filter(model.User.fitness == int(fitness)).all()
		
	return render_template('view_players.html', 
					title='Create Teams',
					users=users,
					health_issues=health_issues)