from flask import Flask
from models.db import db, init_db
from flask_login import LoginManager
from routes.auth import bp_auth      # Blueprint de autenticação
from routes.admin import bp_admin    # Blueprint de administração (já existente)
from models.usuario import Usuario   # Modelo de usuário para autenticação

def format_real(value):
    """
    Formata um valor numérico para o formato de moeda brasileira.
    Exemplo: 100000.0 -> R$100.000,00
    """
    return "R${:,.2f}".format(value).replace(",", "X").replace(".", ",").replace("X", ".")

def create_app():
    app = Flask(__name__)
    
    # Configuração do banco de dados MySQL
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://uaico420_est1114:ghstdrk1566@192.185.211.123:3306/uaico420_est1114'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = "your-secret-key"
    
    # Inicializa o banco de dados e cria as tabelas (caso ainda não existam)
    init_db(app)
    
    # Registra o filtro customizado para formatação de moeda no Jinja
    app.jinja_env.filters['real'] = format_real
    
    # Configuração do Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))
    
    # Registrar os blueprints
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_admin)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
