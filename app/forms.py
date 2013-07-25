from flask.ext.wtf import Form, validators
from flask.ext.wtf import FormField, TextField, PasswordField, IntegerField, DateField, BooleanField


class LoginForm(Form):
	email = TextField('Email',[validators.Email(message= (u'Invalid email address'))])
	password = PasswordField('Password', [validators.Required(), validators.length(min=6, max=25)])
										  					
class RegisterForm(Form):
	firstname = TextField('First Name', [validators.Required()])
	lastname = TextField('Last Name',[validators.Required()])
	login = FormField(LoginForm)
	address= TextField('Address',[validators.Required()])
	city= TextField('City',[validators.Required()])
	state = TextField('State', [validators.Required(), validators.length(max=2)])
	zipcode = TextField('Zipcode', [validators.Required()])
	country = TextField('Country',[validators.Required()])
	dob = DateField('DOB', [validators.Required()], format='%Y-%m-%d')
	gender = IntegerField('Gender', [validators.Required()])
	fitness = IntegerField('Fitness Level', [validators.Required()])
	experience = IntegerField('Years Played', [validators.Required()])
	willing_teamLeader = BooleanField('Team Leader?')


def length(min=-1, max=-1):
    message = 'Must be between %d and %d characters long.' % (min, max)

    def _length(form, field):
        l = field.data and len(field.data) or 0
        if l < min or max != -1 and l > max:
            raise ValidationError(message)

    return _length