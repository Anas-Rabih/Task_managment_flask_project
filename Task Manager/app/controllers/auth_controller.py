from flask import session
from werkzeug.security import check_password_hash
from ..models.user import User
from ..extensions import db

class AuthController:
    @staticmethod
    def register_user(username, email, password):
        if User.query.filter_by(username=username).first():
            return False, 'Username already exists'
        if User.query.filter_by(email=email).first():
            return False, 'Email already exists'
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return True, 'User registered successfully'

    @staticmethod
    def login_user(username, password, remember=False):
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return False, 'Invalid username or password'
        
        session['user_id'] = user.id
        if remember:
            session.permanent = True
        
        return True, 'Login successful'

    @staticmethod
    def logout_user():
        session.pop('user_id', None)
        return True, 'Logout successful'

    @staticmethod
    def get_current_user():
        if 'user_id' not in session:
            return None
        return User.query.get(session['user_id'])