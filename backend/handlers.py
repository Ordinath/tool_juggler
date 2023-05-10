from flask import g
from auth import get_authenticated_user


def register_handlers(app):

    app.secret_key = app.config['SESSION_SECRET_KEY']

    @app.before_request
    def load_user():
        g.user = get_authenticated_user()
        print('before_request g.user: ', g.user)