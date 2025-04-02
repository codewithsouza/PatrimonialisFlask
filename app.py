import os
from flask import Flask, render_template
from flask_login import LoginManager
from models.db import db
from models.usuario import Usuario
from config import Config  # importa o config.py

# Blueprints
from routes.auth import auth
from routes.admin import bp_admin

def create_app():
    app = Flask(__name__)
    
    # 📦 Configurações centralizadas
    app.config.from_object(Config)

    # 🔗 Inicializa extensões
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # 🔌 Registra blueprints
    app.register_blueprint(auth)
    app.register_blueprint(bp_admin)

    # Página pública
    @app.route('/')
    def home():
        return 'Página pública'

    return app

# 🟢 Rodar localmente
if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(debug=app.config['DEBUG'], port=port)
