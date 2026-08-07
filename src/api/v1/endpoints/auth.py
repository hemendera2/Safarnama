from datetime import timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from src.models import User, UserRole, db

router = Blueprint("auth", __name__)


@router.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 400

    user = User(email=data["email"], full_name=data.get("full_name"))
    user.set_password(data["password"])

    # First user is admin (for demo purposes)
    if User.query.count() == 0:
        user.role = UserRole.ADMIN

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@router.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data["email"]).first()

    if user and user.check_password(data["password"]):
        access_token = create_access_token(
            identity=user.id,
            additional_claims={"role": user.role.value},
            expires_delta=timedelta(days=1),
        )
        return jsonify(access_token=access_token), 200

    return jsonify({"error": "Invalid credentials"}), 401


@router.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify(
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
        }
    )
