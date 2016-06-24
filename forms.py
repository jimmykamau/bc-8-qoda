from flask_wtf import Form
from wtforms import StringField, PasswordField, SelectField, validators


# Registration form
class newUserForm(Form):
	fullname = StringField('Full Name',
		validators=[validators.input_required(),
		validators.Length(max=50)])
	email = StringField('Email Address',
		validators=[validators.input_required(),
		validators.Length(max=30)])
	passw1 = PasswordField('Password',
		validators=[validators.input_required(),
		validators.EqualTo('passw2',
			message='Passwords must match')])
	passw2 = PasswordField('Repeat Password',
		validators=[validators.input_required()])


# Form for editing user's credentials
class editUserForm(Form):
	fullname = StringField('Full Name',
		validators=[validators.input_required(),
		validators.Length(max=50)])
	email = StringField('Email Address',
		validators=[validators.input_required(),
		validators.Length(max=30)])


# Form for changing password
class changeUserPass(Form):
	passw1 = PasswordField('Password',
		validators=[validators.input_required(),
		validators.EqualTo('passw2', message='Passwords must match')])
	passw2 = PasswordField('Repeat Password',
		validators=[validators.input_required()])