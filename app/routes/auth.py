from flask import Blueprint, render_template, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from app.models.auth import User
from app.forms.auth_forms import LoginForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        user_role = (session.get('role') or '').lower()
        if user_role == 'client':
            return redirect(url_for('portal.dashboard'))
        return redirect(url_for('inventory.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.username.data)
        ).first()

        if user and check_password_hash(user.password_hash, form.password.data):
            if not user.is_active:
                flash('Account is deactivated. Contact admin.', 'danger')
                return render_template('auth/login.html', form=form)

            session['user_id'] = user.id
            session['username'] = user.username
            role_name = user.role.name if user.role else 'Client'
            session['role'] = role_name

            flash(f'Welcome back, {user.username}!', 'success')

            if role_name.lower() == 'client':
                return redirect(url_for('portal.dashboard'))
            else:
                return redirect(url_for('inventory.dashboard'))

        flash('Invalid username or password.', 'danger')

    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
