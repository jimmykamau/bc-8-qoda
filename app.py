import os
import redis
import gevent
from flask import Flask, render_template, \
    url_for, redirect, session, request, json, \
    jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect
from flask_sockets import Sockets
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_mail import Mail, Message
from forms import newUserForm, editUserForm, changeUserPass, \
    StringField, validators, PasswordField

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)
CsrfProtect(app)
mail = Mail(app)
sockets = Sockets(app)
redis = redis.from_url(app.config['REDIS_URL'])

from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user, utils
from code import *

# Define models
roles_users = db.Table('roles_users',
                        db.Column('user_id', db.Integer(),
                                    db.ForeignKey('user.id')),
                        db.Column('role_id', db.Integer(),
                                    db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    full_name = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(45))
    current_login_ip = db.Column(db.String(45))
    login_count = db.Column(db.Integer)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return (self.email)


from flask_security.forms import RegisterForm


class ExtendedRegisterForm(RegisterForm):
    full_name = StringField('Full Name',
                            validators=[validators.input_required()])

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore,
                    confirm_register_form=ExtendedRegisterForm)


from models import CodeSessions


admin = Admin(app, name='Qoda', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(CodeSessions, db.session))


def create_new_coding_session(session_name):
    new_session = CodeSessions(session_owner=str(current_user),
                                session_name=session_name)
    db.session.add(new_session)
    db.session.commit()
    return new_session.id

@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/create_new_session')
def create_new_session():
    session_name = request.args.get('name', type=str)
    new_session = create_new_coding_session(session_name)
    session['current_session'] = new_session
    return jsonify(session_id=session['current_session'])

if __name__ == '__main__':
    app.run()
