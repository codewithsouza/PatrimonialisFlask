from flask import Flask, request, redirect, url_for
from flask_login import LoginManager
from flask_migrate import Migrate
from models.db import db
from config import Config
from admin.routes import admin_bp
from cliente import cliente_bp
from models.usuario import Usuario
from auth.routes.auth_routes import auth_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicialização do banco de dados
    db.init_app(app)
    migrate = Migrate(app, db)

    # Configuração do Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    @login_manager.unauthorized_handler
    def unauthorized():
        if request.path.startswith('/admin'):
            return redirect(url_for('auth.admin_login'))
        return redirect(url_for('auth.cliente_login'))

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Registro dos blueprints
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(cliente_bp, url_prefix='/cliente')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)



