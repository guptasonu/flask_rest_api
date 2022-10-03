import datetime
import os

import jwt
from flask import jsonify, make_response, request
from flask_restful import Api, Resource
from werkzeug.security import check_password_hash, generate_password_hash

from authentication import token_required
from config import app, db
from models import User

api = Api(app)


class HelloWorld(Resource):
    def get(self):
        return {"data": "Hello World"}


api.add_resource(HelloWorld, "/")


@app.route("/user", methods=["GET"])
@token_required
def get_all_users(current_user):
    users = User.query.all()
    users_serializable = []
    for user in users:
        new_user = {}
        new_user["id"] = user.id
        new_user["name"] = user.name
        new_user["password"] = user.password
        users_serializable.append(new_user)

    return jsonify({"users": users_serializable})


@app.route("/user/<user_id>", methods=["GET"])
@token_required
def get_one_user(current_user, user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"message": "No User Found"})
    new_user = {}
    new_user["id"] = user.id
    new_user["name"] = user.name
    new_user["password"] = user.password
    return jsonify({"user": new_user})


@app.route("/user", methods=["POST"])
def create_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data.get("password"), method="sha256")
    new_user = User(name=data.get("name"), password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "New User Created"})


@app.route("/user/<user_id>", methods=["PUT"])
@token_required
def update_user(current_user, user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"message": "No User Found"})
    data = request.get_json()
    user.name = data.get("name")
    db.session.commit()
    return jsonify({"message": "User is updated"})


@app.route("/user/<user_id>", methods=["DELETE"])
@token_required
def delete_user(current_user, user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"message": "No User Found"})
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "The User has been deleted"})


@app.route("/login")
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response(
            "Could not verify",
            401,
            {"WWW-Authenticate": "Basic realm ='Login Required!'"},
        )
    user = User.query.filter_by(name=auth.username).first()
    if not user:
        return jsonify({"message": "No User Found!"})
    if check_password_hash(user.password, auth.password):
        token = jwt.encode(
            {
                "id": user.id,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            },
            app.config["SECRET_KEY"],
        )
        return jsonify({"token": token})
    return make_response(
        "Could not verify",
        401,
        {"WWW-Authenticate": "Basic realm ='Login Required!'"},
    )


if __name__ == "__main__":
    if not os.path.exists("sqllite3.db"):
        db.create_all()
    app.run(debug=True)
