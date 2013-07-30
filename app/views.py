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

	if form.validate_on_submit():
		# check if email already exists
		email_exists = model.session.query(model.User).filter_by(email = form.email.data).first()
		
		if email_exists == None:
			
			user = model.session.add(model.User(firstname= form.firstname.data,
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

			model.session.commit()

			# new_user= model.session.query(model.User).filter_by(email = form.email.data).first()

			# #new_user.positions.append(Position(position_type= form.data.positions))

			flash("You are registered") 
	   		#user must login with new email/password
			return redirect('login')
		else:
			flash('Email already exists')

	else:
		return render_template('register.html',
								title='Register',
								form=form)

@app.route('/team_assign', methods=['GET','POST'])
@login_required
def make_teams():

	users = model.session.query(model.User).all()
	health_issues = model.session.query(model.HealthType).all()

	# # FItness Display
	# if request.method == "POST":
 #        fitness = request.form[int("fitness")]
	



	return render_template('team_assign.html', 
							title= 'Create Teams',
							users=users,
							health_issues= health_issues)


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
	