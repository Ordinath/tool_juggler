import os

SQLALCHEMY_DATABASE_URI = 'sqlite:///conversations.db'
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')