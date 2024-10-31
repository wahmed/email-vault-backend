import secrets
from flask import Flask, jsonify, request
from werkzeug.exceptions import BadRequest
from common.models import User  
from common.db_config import db_config
from flask_cors import CORS
import logging
import os
import jwt
import datetime
from functools import wraps
from my_flask.email_worker import send_email
from dotenv import load_dotenv
load_dotenv('/app/.env_secrets') 


app = Flask(__name__)

CORS(app=app, resources={r"*": {"origins": "*"}})
logging.debug('CORS initialised')

FRONT_END_URL=os.getenv('FRONT_END_URL')
SECRET_KEY = os.getenv('JWT_SECRET_KEY')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
            
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 403

        return f(*args, **kwargs)

    return decorated


def generate_token(user):
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }, SECRET_KEY, algorithm="HS256")
    return token


@app.route('/api/signup', methods=['POST'])
def signup():
    session = db_config.open()  
    try:
        data = request.get_json()
        required_fields = ['first_name', 'last_name', 'company_name', 'email', 'password']
        for field in required_fields:
            if field not in data:
                raise BadRequest(f"{field} is required")

        first_name = data['first_name']
        last_name = data['last_name']
        email = data['email']
        password = data['password']
        company_name = data['company_name']
        referral_number = data.get('referral_number')

        existing_user = session.query(User).filter(User.email == email).first()
        if existing_user:
            return jsonify({"message": "Email already exists."}), 400
        verification_token = secrets.token_urlsafe(16)

        new_user = User(
            first_name=first_name,
            last_name=last_name,
            company_name=company_name,
            email=email,
            referral_number=referral_number,
            verification_token=verification_token
        )
        new_user.set_password(password) 
        session.add(new_user)
        session.commit()
        verification_link = f"{FRONT_END_URL}email-verified/?token={verification_token}"

        template_variables = {
            'verify_link': verification_link,
            
        }
        subject = 'account verification link'
        print(verification_link)

        send_email(email,  6410451, template_variables,subject)
        

        return jsonify({"message": "User created successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db_config.close(session)

@app.route('/api/verify/<token>', methods=['GET'])
def verify_user(token):
    session = db_config.open()
    try:
        user = session.query(User).filter(User.verification_token == token).first()
        if user is None:
            return jsonify({"message": "Invalid or expired token."}), 400
        
        user.is_approved = True
        user.verification_token = None
        session.commit()
        
        return jsonify({"message": "User verified successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db_config.close(session)


@app.route('/api/users', methods=['GET'])
@token_required
def get_users():
    session = db_config.open()
    try:
        users = session.query(User).all()
        user_list = [
            {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'company_name': user.company_name,
                'email': user.email,
                'referral_number': user.referral_number,
                'is_approved': user.is_approved,
            } for user in users
        ]
        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500  
    finally:
        db_config.close(session)

@app.route('/api/login', methods=['POST'])
def login():
    session = db_config.open()
    try:
        data = request.get_json()
        required_fields = ['email', 'password']
        for field in required_fields:
            if field not in data:
                raise BadRequest(f"{field} is required")

        email = data['email']
        password = data['password']
        user = session.query(User).filter(User.email == email).first()
        if user is None or not user.check_password(password): 
            return jsonify({"message": "Invalid email or password."}), 401
        if user.is_approved == False:
            return jsonify({"message": "User is not approved."}), 401

        user_data = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'company_name': user.company_name,
            'email': user.email,
            'is_approved':user.is_approved
        }
        token = generate_token(user)

        return jsonify({"message": "Login successful.", "user": user_data, "token": token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db_config.close(session)

@app.route('/api/reset_password', methods=['POST'])
def reset_password():
    session = db_config.open()
    try:
        data = request.get_json()
        if 'email' not in data:
            raise BadRequest("Email is required")

        email = data['email']
        user = session.query(User).filter(User.email == email).first()
        if user is None:
            return jsonify({"message": "Email not found."}), 404
        recovery_token = secrets.token_urlsafe(16)
        user.recovery_token = recovery_token
        session.commit()
        recovery_link = f"{FRONT_END_URL}confirm-reset-password/?token={recovery_token}"
        template_variables = {
            'verify_link': recovery_link,
        }
        subject = 'reset password link'

        print(recovery_link)
        send_email(email, 6410454, template_variables,subject)


        return jsonify({"message": "Recovery email sent."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db_config.close(session)

@app.route('/api/confirm_reset_password/<token>', methods=['POST'])
def confirm_reset_password(token):
    session = db_config.open()
    try:
        data = request.get_json()
        if 'new_password' not in data:
            raise BadRequest("New password is required")

        new_password = data['new_password']
        user = session.query(User).filter(User.recovery_token == token).first()

        if user is None:
            return jsonify({"message": "Invalid or expired token."}), 400

        user.set_password(new_password)
        user.recovery_token = None
        session.commit()

        return jsonify({"message": "Password reset successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db_config.close(session)

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    session = db_config.open()
    try:
        data = request.get_json()
        user = session.query(User).filter(User.id == user_id).first()

        if user is None:
            return jsonify({"message": "User not found."}), 404


        for field in ['first_name', 'last_name', 'company_name', 'referral_number']:
            if field in data:
                setattr(user, field, data[field])

        session.commit()
        return jsonify({"message": "User updated successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db_config.close(session)

if __name__ == '__main__':
    app.run(debug=True,port=5001)
