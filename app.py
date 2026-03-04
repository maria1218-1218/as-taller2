"""
Aplicación Flask - Punto de entrada principal
Este archivo configura y ejecuta la aplicación Flask siguiendo el patrón MVC
"""

from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from config import config
import os

# Crear instancia de SQLAlchemy
db = SQLAlchemy()


def create_app(config_name=None):
    """
    Factory function para crear y configurar la aplicación Flask
    
    Args:
        config_name (str): Nombre de la configuración a usar ('development', 'production', etc.)
    
    Returns:
        Flask: Instancia configurada de la aplicación
    """
    app = Flask(__name__)
    
    # Determinar configuración a usar
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    # Aplicar configuración
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    db.init_app(app)
    
    # Importar modelos para que SQLAlchemy los reconozca
    from models.task import Task
    from models.user import User

    # Context processor para exponer usuario actual en las plantillas
    @app.context_processor
    def inject_user():
        user = None
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
        return dict(current_user=user)

    # Registrar blueprints (controladores)
    from controllers.task_controller import register_routes
    from controllers.auth_controller import register_auth_routes
    # primero autenticación para que login_required quede disponible
    register_auth_routes(app)
    register_routes(app)
    
    # Crear tablas de base de datos
    with app.app_context():
        db.create_all()
    
    return app


if __name__ == '__main__':
    print("Iniciando aplicación To-Do MVC...")
    app = create_app()
    
    print("Accede a: http://127.0.0.1:5000")
    print("Modo debug activado - Los cambios se recargarán automáticamente")
    app.run(host='127.0.0.1', port=5000, debug=True)

