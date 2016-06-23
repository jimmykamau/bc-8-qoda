import os
import redis
import gevent
from flask import Flask, render_template, \
    url_for, redirect, request, \
    jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect
from flask_sockets import Sockets
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_mail import Mail, Message
from forms import newUserForm, editUserForm, changeUserPass, \
    StringField, validators, PasswordField

# Initialize app and app's variables
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)
CsrfProtect(app)
mail = Mail(app)
sockets = Sockets(app)
redis = redis.from_url(app.config['REDIS_URL'])

# Import other modules. Not imported at top of file due to cyclic imports error 
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user
from code import *
from chat import *

# Define flask-security models
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

    @property
    def serialize(self):
        return {
            'id' : self.id,
            'email' : self.email,
            'full_name' : self.full_name,
        }


    def __repr__(self):
        return (self.email)


# Import RegisterForm from flask-security for Login's customization
from flask_security.forms import RegisterForm


class ExtendedRegisterForm(RegisterForm):
    full_name = StringField('Full Name',
                            validators=[validators.input_required()])

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore,
                    confirm_register_form=ExtendedRegisterForm)


# Import models
from models import CodeSessions, CurrentUserSession, CodingSessionUsers


admin = Admin(app, name='Qoda', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(CodeSessions, db.session))
#admin.add_view(ModelView(CurrentUserSession, db.session))
admin.add_view(ModelView(CodingSessionUsers, db.session))


def create_new_coding_session(session_name, session_desc=''):
    new_session = CodeSessions(session_owner=str(current_user),
                            session_name=session_name,
                            session_desc=session_desc)
    db.session.add(new_session)
    db.session.commit()
    return new_session.id


def change_user_current_sesion(session_id):
    try:
        current_user_session = db.session.query(CurrentUserSession).filter_by(user_id=int(current_user.id)).one()
    except:
        current_user_session = CurrentUserSession()

    current_user_session.user_id = int(current_user.id)
    current_user_session.session_id = int(session_id)
    db.session.add(current_user_session)
    db.session.commit()
    current_session_name = db.session.query(CodeSessions).filter_by(id=int(current_user_session.session_id)).one()
    return current_user_session.session_id, current_session_name.session_name, current_session_name.session_desc


def add_user_to_coding_session(s_id, u_id):
    new_user = db.session.query(CodingSessionUsers).filter_by(user_id=u_id,
                                                            session_id=s_id).all()
    if new_user:
        pass
    else:
        new_user = CodingSessionUsers(user_id=u_id, session_id=s_id)
        db.session.add(new_user)
        db.session.commit()
    return new_user


def check_user_owns_session(session_id):
    try:
        sess = db.session.query(CodeSessions).filter_by(id=session_id).one()
        if sess.session_owner == str(current_user.email):
            return True
        else:
            return False
    except:
        return False


def get_registered_users():
    return db.session.query(User).filter_by(active=True).all()


@app.route('/')
@login_required
def index():
    try:
        session_request = db.session.query(CurrentUserSession).filter_by(user_id=int(current_user.id)).one()
        current_session = session_request.session_id
    except:
        current_u_session = CodeSessions(session_owner=str(current_user.email), session_name="My first session", session_desc="My first Qoda coding session")
        db.session.add(current_u_session)
        db.session.commit()
        current_session = current_u_session.id
    return redirect(url_for('change_session', session_number=current_session))


@app.route('/create_new_session')
def create_new_session():
    session_name = request.args.get('name', type=str)
    session_description = request.args.get('desc')
    new_session = create_new_coding_session(session_name, session_description)
    change_user_current_sesion(new_session)
    return jsonify(session_id=new_session)


@app.route('/my_sessions')
def get_user_sessions():
    user_sessions = db.session.query(CodeSessions).filter_by(session_owner=str(current_user)).all()
    return jsonify(user_sessions=[u.serialize for u in user_sessions])


@app.route('/sessions/<int:session_number>')
def change_session(session_number):
    new_session_id, new_session_name, new_session_desc = change_user_current_sesion(session_number)
    return render_template('index.html', 
                            user=current_user, chan=new_session_id, 
                            chan_name=new_session_name, chan_desc=new_session_desc, 
                            user_list=[u.serialize for u in get_registered_users()])


@app.route('/add_user_to_session/<session_id>/<user_id>')
def add_user(session_id, user_id):
    if check_user_owns_session(int(session_id)):
        add_user_to_coding_session(int(session_id), int(user_id))
        return jsonify(message="Success")
    else:
        return jsonify(message="Fail")


@app.route('/get_session_users/<session_id>')
def get_session_users(session_id):
    session_id = int(session_id)
    user_dets = db.session.query(CodingSessionUsers).filter_by(
        session_id=session_id).all()
    return jsonify(users=[u.serialize for u in user_dets])


@app.route('/edit_session')
def edit_session():
    session_id = request.args.get('session_id')
    session_name = request.args.get('session_name')
    session_desc = request.args.get('session_desc')
    if check_user_owns_session(int(session_id)):
        current_session = db.session.query(CodeSessions).filter_by(id=int(session_id)).one()
        current_session.session_name = session_name
        current_session.session_desc = session_desc
        db.session.add(current_session)
        db.session.commit()
        return jsonify(message="Pass")
    else:
        return jsonify(message="Fail")


@app.route("/delete_session")
def delete_session():
    session_id = request.args.get('session_id')
    if check_user_owns_session(int(session_id)):
        sesssion_to_delete = db.session.query(CodeSessions).filter_by(id=int(session_id)).one()
        delete_coding_session_userstore = db.session.query(CodingSessionUsers).filter_by(session_id=int(session_id)).all()
        unset_current_session = db.session.query(CurrentUserSession).filter_by(user_id=int(current_user.id)).one()
        db.session.delete(unset_current_session)
        for i in delete_coding_session_userstore:
            db.session.delete(i)
        db.session.delete(sesssion_to_delete)
        db.session.commit()
        try:
            cuurrent_session = db.session.query(CodeSessions).filter_by(session_owner=str(current_user.email)).one()
            current_session = cuurrent_session.id
        except:
            current_u_session = CodeSessions(session_owner=str(current_user.email), session_name="My first session", session_desc="My first Qoda coding session")
            db.session.add(current_u_session)
            db.session.commit()
            current_session = current_u_session.id
        flash("Session deleted successfully", 'success')
        return redirect(url_for('change_session', session_number=current_session))
    else:
        return jsonify(message="Unauthorized")

if __name__ == '__main__':
    app.run()
