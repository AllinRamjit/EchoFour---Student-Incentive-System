from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db

class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    username =  db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256), nullable=False)
    role= db.Column(db.String(256),nullable=False, default="user")  #Create role column to distinguish user types

    __mapper_args__ = {
        "polymorphic_on": role,
        "polymorphic_identity": "user"
    }

    def __init__(self, username, email,password,role):
        self.username = username
        self.role=role
        self.set_password(password)
        self.email= email

    def get_json(self):
        return{
            'id': self.user_id,
            'username': self.username,
            'email': self.email
        }

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)
    
    def login(username,password):
        user= User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return user
        return None
    
    def change_password(self, old_password, new_password):
        if self.check_password(old_password):
            self.set_password(new_password)
            db.session.commit()
            return True
        return False
    





# from werkzeug.security import check_password_hash, generate_password_hash
# from App.database import db

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username =  db.Column(db.String(20), nullable=False, unique=True)
#     password = db.Column(db.String(256), nullable=False)

#     def __init__(self, username, password):
#         self.username = username
#         self.set_password(password)

    
#     def get_json(self):
#         return{
#             'id': self.id,
#             'username': self.username
#         }

#     def set_password(self, password):
#         """Create hashed password."""
#         self.password = generate_password_hash(password)
    
#     def check_password(self, password):
#         """Check hashed password."""
#         return check_password_hash(self.password, password)

