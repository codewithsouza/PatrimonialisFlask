import os
from flask import Flask, render_template
from flask_login import LoginManager
from models.db import db
from models.usuario import Usuario
from config import Config


# Importando os blueprints
from routes.admin import bp_admin
from routes.auth import auth
from routes.notificacoes import notificacoes_bp



def create_app():
    app = Flask(__name__)
    
    # Configuração principal
    app.config.from_object(Config)

    # Inicialização do banco de dados
    db.init_app(app)
    
    # Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Registro de Blueprints
    app.register_blueprint(auth)
    app.register_blueprint(bp_admin)
    app.register_blueprint(notificacoes_bp)
    
    


    # Página inicial pública
    @app.route('/')
    def home():
        return render_template('public/index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(debug=app.config['DEBUG'], port=port)



