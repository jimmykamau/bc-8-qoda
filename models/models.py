from app import db, User

'''
Model for code sessions. `session_owner` > Email address of session's owner, \
`session_name` > Session's name, `session_desc` > Session's description
'''


class CodeSessions(db.Model):
	__tablename__ = 'codesessions'

	id = db.Column(db.Integer, primary_key=True)
	session_owner = db.Column(db.String, db.ForeignKey('user.email'))
	session_name = db.Column(db.String)
	session_desc = db.Column(db.String)
	user = db.relationship(User)

	def __init__(self, session_owner='', session_name='', session_desc=''):
		self.session_owner = session_owner
		self.session_name = session_name
		self.session_desc = session_desc

	@property
	def serialize(self):
	    return {
	    	'id' : self.id,
	    	'session_owner' : self.session_owner,
	    	'session_name' : self.session_name,
	    	'session_desc' : self.session_desc,
	    }

	def __repr__(self):
		return self.id


'''
Model for user's current session. `user_id` > Current user's ID \
of session's owner, \
`session_id` > Session's id
'''


class CurrentUserSession(db.Model):
	__tablename__ = 'currentusersession'

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	session_id = db.Column(db.Integer, db.ForeignKey('codesessions.id'))
	user = db.relationship(User)
	codesessions = db.relationship(CodeSessions)

	def __init__(self, user_id='', session_id=''):
		self.user_id = user_id
		self.session_id = session_id

	@property
	def serialize(self):
		return {
			'user_id' : self.user_id,
			'session_id' : self.session_id,
		}
	 
	def __repr__(self):
		return self.user_id


'''
Model for code session's invited users. \
`user_id` > Invited user's ID, \
`user_name` > Invited user's name, \
`user_email` > Invited user's name
'''


class CodingSessionUsers(db.Model):
	__tablename__ = 'codingsessionusers'

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	session_id = db.Column(db.Integer, db.ForeignKey('codesessions.id'))
	user_name = db.Column(db.String)
	user_email = db.Column(db.String)
	user = db.relationship(User)
	codesessions = db.relationship(CodeSessions)

	def __init__(self, user_id='', session_id='', user_email='', user_name=''):
		self.user_id = user_id
		self.session_id = session_id
		self.user_email = user_email
		self.user_name = user_name

	@property
	def serialize(self):
		return {
			'user_id' : self.user_id,
			'session_id' : self.session_id,
			'user_email' : self.user_email,
			'user_name' : self.user_name,
		}
	 
	def __repr__(self):
		return self.user_id
