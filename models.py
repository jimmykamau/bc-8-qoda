from app import db, User


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

	def __repr__(self):
		return self.id
