"""
Controlador de autenticación – registro, inicio/cierre de sesión
"""
from flask import render_template, request, redirect, url_for, flash, session
from models.user import User
from app import db
from functools import wraps


def login_required(f):
    """Decorador que redirige a login si no hay usuario en sesión"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            # mantener url de destino en parámetro "next"
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated


def register_auth_routes(app):
    """Registra las rutas de autenticación en la aplicación"""

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        # si ya está autenticado redirigir
        if session.get('user_id'):
            return redirect(url_for('task_list'))
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            confirm = request.form.get('confirm')

            if not username or not password:
                flash('Usuario y contraseña son obligatorios', 'error')
                return render_template('register.html')

            if password != confirm:
                flash('Las contraseñas no coinciden', 'error')
                return render_template('register.html')

            # verificar si ya existe usuario
            existing = User.query.filter_by(username=username).first()
            if existing:
                flash('El nombre de usuario ya está en uso', 'error')
                return render_template('register.html')

            user = User(username, password)
            db.session.add(user)
            db.session.commit()
            flash('Registro exitoso, ya puedes iniciar sesión', 'success')
            return redirect(url_for('login'))

        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if session.get('user_id'):
            return redirect(url_for('task_list'))
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                session['user_id'] = user.id
                flash(f'Bienvenido, {user.username}!', 'success')
                next_url = request.args.get('next') or url_for('task_list')
                return redirect(next_url)
            else:
                flash('Credenciales inválidas', 'error')
                return render_template('login.html')
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        flash('Has cerrado sesión', 'success')
        return redirect(url_for('login'))

    # exponer decorador para otros módulos si se necesita
    app.login_required = login_required
