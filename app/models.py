from app import db

class Judge(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(32), index = True, unique = True)
    passwd = db.Column(db.String(32))
    createDate = db.Column(db.DateTime)
    comment = db.Column(db.String(100))

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)
        except NameError:
            return str(self.id)

    def __repr__(self):
        return 'Judge %r' % self.name

class Player(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(32), index = True)
    phone = db.Column(db.String(32), index = True, unique = True)
    score = db.Column(db.Integer)
    createDate = db.Column(db.DateTime)
    comment = db.Column(db.String(100))
    judge_id = db.Column(db.Integer, db.ForeignKey('judge.id'))
    def __repr__(self):
        return 'Player %r' % self.name
