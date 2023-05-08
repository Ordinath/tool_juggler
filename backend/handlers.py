from flask import g
import auth


def register_handlers(app):
    @app.before_request
    def load_user():
        g.user = auth.get_authenticated_user()
