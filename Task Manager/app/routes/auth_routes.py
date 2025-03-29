from flask import Blueprint, render_template, redirect, url_for, flash
from ..controllers.auth_controller import AuthController
from app.forms.auth_forms import LoginForm, RegistrationForm  # Import both forms

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            success, message = AuthController.register_user(
                form.username.data,
                form.email.data,
                form.password.data
            )
            flash(message, 'success' if success else 'danger')
            return redirect(url_for('auth.login')) if success else redirect(url_for('auth.register'))
        except Exception as e:
            flash(f'Registration error: {str(e)}', 'danger')
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            success, message = AuthController.login_user(
                form.username.data,
                form.password.data,
                form.remember.data
            )
            flash(message, 'success' if success else 'danger')
            return redirect(url_for('task.dashboard')) if success else redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Login error: {str(e)}', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
def logout():
    AuthController.logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/')
@auth_bp.route('/accueil')
def accueil():
    return render_template('accueil.html')