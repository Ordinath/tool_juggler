from functools import wraps
from flask import request, jsonify, g, current_app
import jwt
from db_models import User


def get_authenticated_user():
    # print all g variables:
    print('g: ', g.__dict__)

    if hasattr(g, 'user') and g.user is not None:
        return g.user

    print('request ', request.headers)

    token = request.headers.get('Authorization')

    if not token:
        return None

    try:
        payload = jwt.decode(
            token, current_app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

    user = User.query.get(payload['user_id'])
    return user


def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function
