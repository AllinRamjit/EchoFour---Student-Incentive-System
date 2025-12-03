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
    
    @staticmethod
    def login(username, password):
        # Business logic for authentication lives in `App.controllers.auth.login`.
        # Keep a thin compatibility wrapper here so existing call sites
        # can continue to call `User.login(...)`.
        # Lightweight compatibility: return the User object when credentials
        # are correct. Controller `login` may return tokens for HTTP flows.
        try:
            result = db.session.execute(db.select(User).filter_by(username=username))
            user = result.scalar_one_or_none()
            if user and user.check_password(password):
                return user
            return None
        except Exception:
            return None

    def change_password(self, old_password, new_password):
        # Only update the in-memory password here; committing the
        # session should be the responsibility of the controller.
        if self.check_password(old_password):
            self.set_password(new_password)
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

