from flask import render_template, redirect, flash
from forms import LoginForm, RegisterForm
from app import app

@app.route('/')

@app.route('/index')
def homepage():
	return render_template('index.html',
							title='Homepage')

@app.route('/login', methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		flash("Welcome")
		return redirect('index')
	return render_template('login.html',
							title='Sign In',
							form=form)
 
@app.route('/register', methods=['GET','POST'])
def register():
	form = RegisterForm()
	if form.validate_on_submit()
	   flash("You are registered")
	   return redirect('index')
	return render_template('register.html',
							title='Register',
							form=form)