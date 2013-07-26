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
	return model.session.query(model.User).get(int(id))

@app.before_request
def before_request():
	g.user = current_user

### End LoginHandler settings

@app.route('/')
@app.route('/index')
# @login_required
def homepage():
	user = g.user

	return render_template('index.html',
							title='Homepage',
							user=user)

@app.route('/login', methods=['GET','POST'])
def login():
	if g.user is not None and g.user.is_authenticated():
		return redirect(url_for('user'))

	form = LoginForm()
	if form.validate_on_submit():
		#print form.email.data

		user= model.session.query(model.User).filter_by(email = form.email.data).first()
		print user
		print user.email
		
		if user is None:
			flash("Invalid login. Please try again")
		else:
			login_user(user)
			flash("Welcome")
		
		return redirect(request.args.get("next") or url_for('user'))
		
	return render_template('login.html',
							title='Sign In',
							form=form)
 
@app.route('/register', methods=['GET','POST'])
def register():
	form = RegisterForm()

	if form.validate_on_submit():
	   flash("You are registered")
	   return redirect('login')

	#print form.errors

	return render_template('register.html',
							title='Register',
							form=form)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect('index')

@app.route('/user')
@login_required
def user():
	user = model.User.get(int(id))

	if user is None:
		return redirect(url_for('login'))

	return render_template('user.html')

# if __name__ == "__main__":
#     app.run(debug = True)