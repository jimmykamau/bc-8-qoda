import os
import redis
import gevent
from flask import Flask, render_template, \
    url_for, redirect, session, request, json
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

admin = Admin(app, name='Qoda', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))


REDIS_CHAN = 'code'


class CodeBackend(object):

    def __init__(self):
        self.clients = list()
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(REDIS_CHAN)

    def __iter_data(self):
        for message in self.pubsub.listen():
            data = message.get('data')
            if message['type'] == 'message':
                print('Sending message: {}'.format(data))
                yield data

    def register(self, client):
        self.clients.append(client)

    def send(self, client, data):
        try:
            client.send(data)
        except Exception:
            self.clients.remove(client)

    def run(self):
        for data in self.__iter_data():
            for client in self.clients:
                gevent.spawn(self.send, client, data)

    def start(self):
        gevent.spawn(self.run)

code = CodeBackend()
code.start()


@sockets.route('/submit')
def inbox(ws):
    while not ws.closed:
        gevent.sleep(0.1)
        message = ws.receive()

        if message:
            print('Inserting message: {}'.format(message))
            redis.publish(REDIS_CHAN, message)


@sockets.route('/receive')
def outbox(ws):
    code.register(ws)

    while not ws.closed:
        gevent.sleep(0.1)


@app.route('/')
@login_required
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
