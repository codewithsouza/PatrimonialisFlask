import os
from flask import Flask, render_template
from flask_login import LoginManager
from models.db import db
from models.usuario import Usuario
from config import Config
from routes.notificacoes import notificacoes_bp


# Importando os blueprints
from routes.admin import bp_admin
from routes.auth import auth  # caso você tenha um blueprint de auth

def create_app():
    app = Flask(__name__)
    
    #banco de dados no
    app.register_blueprint(notificacoes_bp)

    # 📦 Configurações
    app.config.from_object(Config)

    # 🔗 Inicializa extensões
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # 🔌 Registra Blueprints
    app.register_blueprint(auth)
    app.register_blueprint(bp_admin)

    # Rota pública simples
    @app.route('/')
    def home():
        return render_template('public/index.html')

    # Exemplo de rota com calendário (temporária para debug)
    @app.route('/calendario')
    def calendario():
        eventos = [
            {"title": "Consultoria Fiscal", "start": "2024-04-04"},
            {"title": "Revisão de Contrato", "start": "2024-04-06"},
            {"title": "Reunião Jurídica", "start": "2024-04-09"}
        ]
        return render_template('admin/notificacoes.html', eventos=eventos)

    return app


# 🟢 Rodar localmente
if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(debug=app.config['DEBUG'], port=port)



