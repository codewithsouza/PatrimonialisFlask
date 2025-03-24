from flask import Flask
from flask_login import LoginManager
from models.db import db
from models.usuario import Usuario

# Blueprints
from routes.auth import auth
from routes.admin import bp_admin  # Importa o blueprint admin corretamente

app = Flask(__name__)
app.secret_key = 'lv4Jk0WyEUT2_L52ku1s0ExOg1HEXyjW3Rvsc_noaLM4'

# Configurações do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://uaico420_est1114:ghstdrk1566@192.185.211.123:3306/uaico420_est1114'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa extensões
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

# Carregamento do usuário
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Registra os blueprints depois da criação do app
app.register_blueprint(auth)
app.register_blueprint(bp_admin)

# Rota pública opcional
@app.route('/')
def home():
    return 'Página pública'

if __name__ == '__main__':
    app.run(debug=True)
