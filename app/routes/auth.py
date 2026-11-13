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

@auth_bp.route('/register', methods=['POST'])
def register():
    from werkzeug.security import generate_password_hash
    from app.extensions import db
    import app.models as models

    User = getattr(models, 'User')
    Role = getattr(models, 'Role', None)
    full_name = request.form.get('full_name', '').strip()
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()

    if not username or not password:
        flash('Username and password are required.', 'danger')
        return redirect(url_for('auth.login', tab='register'))

    if User.query.filter_by(username=username).first():
        flash('Username already registered. Please Login.', 'warning')
        return redirect(url_for('auth.login'))

    ucols = {c.name for c in User.__table__.columns}
    ukw = {'username': username}
    if 'email' in ucols: ukw['email'] = email or f"{username}@client.local"
    if 'full_name' in ucols: ukw['full_name'] = full_name or username
    if 'company_name' in ucols: ukw['company_name'] = full_name or username
    if 'is_active' in ucols: ukw['is_active'] = True

    client_role = None
    if Role and 'role_id' in ucols:
        client_role = Role.query.filter(Role.name.ilike('%client%')).first() or Role.query.order_by(Role.id.desc()).first()
        if client_role: ukw['role_id'] = client_role.id

    user = User(**ukw)
    if hasattr(user, 'set_password'): user.set_password(password)
    elif 'password_hash' in ucols: user.password_hash = generate_password_hash(password)
    elif 'password' in ucols: user.password = generate_password_hash(password)

    db.session.add(user)
    db.session.commit()

    session['user_id'] = user.id
    session['username'] = user.username
    session['role'] = client_role.name if client_role else 'Client'
    session['role_name'] = client_role.name if client_role else 'Client'
    flash(f'Account created! Welcome, {full_name or username}.', 'success')
    return redirect(url_for('portal.dashboard'))
