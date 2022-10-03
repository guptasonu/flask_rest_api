from functools import wraps

import jwt
from flask import jsonify, request

from config import app
from models import User


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if "auth-access-token" in request.headers:
            token = request.headers.get("auth-access-token")
        if not token:
            return jsonify({"message": "Token is Missing"}), 401
        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms="HS256")
            current_user = User.query.filter_by(id=data.get("id")).first()
        except:
            return jsonify({"message": "Token Is Invalid"}), 401
        return f(current_user, *args, **kwargs)

    return decorated_function
