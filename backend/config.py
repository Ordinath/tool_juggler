import os

SQLALCHEMY_DATABASE_URI = 'sqlite:///conversations.db'
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
SESSION_SECRET_KEY = os.getenv('SESSION_SECRET_KEY')