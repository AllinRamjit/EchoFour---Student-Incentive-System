import os

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///temp-database.db')

if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)

SECRET_KEY = os.environ.get('SECRET_KEY', 'secret key')
JWT_SECRET_KEY = os.environ.get('SECRET_KEY', 'super-secret-jwt-key')
JWT_TOKEN_LOCATION = ["cookies"]
JWT_COOKIE_SECURE = True
JWT_COOKIE_SAMESITE = "None"
JWT_COOKIE_CSRF_PROTECT = False
JWT_ACCESS_TOKEN_EXPIRES = 86400