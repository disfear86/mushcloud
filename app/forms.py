from wtforms import Form, BooleanField, StringField, PasswordField, validators
from wtforms.validators import DataRequired, Email


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=20)])
    email = StringField('Email Address', [
        validators.Length(min=6, max=20),
        validators.Email()
        ])
    password = PasswordField('Password', [
        validators.Length(min=6),
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
      ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the Terms of Service', [validators.DataRequired()])


class ChangePwdForm(Form):
    old_pwd = PasswordField('Old Password', [
        validators.DataRequired()
        ])
    new_pwd = PasswordField('New Password', [
        validators.Length(min=6),
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
      ])
    confirm = PasswordField('Repeat New Password')


class EnterEmail(Form):
    email = StringField('Email Address', [
        validators.Length(min=6, max=50),
        validators.Email(),
        validators.DataRequired()
        ])


class ForgotPass(Form):
    new_pwd = PasswordField('New Password', [
        validators.Length(min=6),
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat New Password')
