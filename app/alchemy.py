from app import app, db
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(150))
    email = db.Column(db.String(50))
    plan_mb = db.Column(db.Float(2))
    mb_left = db.Column(db.Float(2))
    reset_pass = db.Column(db.Boolean, default=False)

    def __init__(self, id, username=None, email=None, password=None, plan_mb=None, mb_left=None, reset_pass=None):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.plan_mb = plan_mb
        self.mb_left = mb_left
        self.reset_pass = reset_pass

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def get_token(self, expiration=300):
        s = Serializer(app.config['SECRET_KEY'], expiration)
        return s.dumps({'user': self.id}).decode('utf-8')

    @staticmethod
    def verify_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        id = data.get('user')
        if id:
            return User.query.get(id)
        return None

    def __repr__(self):
        return '<User {}>'.format(self.username)


############################################################################
# db model to dynamycally create personal user tables                      #
# wrapped in the tablename() function so we can access the table.                                                     #
#                                                                          #
# Tables are not created by this model. It exists only so we can acces     #
# each individual user table.                                              #
# Pesronal user table is created in the auth module.                       #
############################################################################
def tablename(user):
    class User_table(db.Model):
        __tablename__ = user
        __table_args__ = {'extend_existing': True}
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(150))
        code = db.Column(db.String(150))
        path = db.Column(db.String(150))
        date = db.Column(db.String(15))
        size = db.Column(db.Float)

        def __init__(self, name, code, path, date, size):
            self.name = name
            self.code = code
            self.path = path
            self.date = date
            self.size = size

        def __repr__(self):
            return '<Table %r>' % self.__tablename__
    return User_table

#########################################################
# Defined in auth.registration to create dynamic tables #
# based on users username                               #
#########################################################
"""
class user_folder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    code = db.Column(db.String(150))
    path = db.Column(db.String(150))
    date = db.Column(db.String(15))
    size = db.Column(db.Float)
"""
