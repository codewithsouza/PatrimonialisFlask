from flask import Flask
from models.db import db, init_db
from models.clientes_db import Cliente  # Importa o modelo antes de inicializar o banco

def create_app():
    app = Flask(__name__)
    
    # Configuração do banco de dados MySQL
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://uaico420_est1114:ghstdrk1566@192.185.211.123:3306/uaico420_est1114'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = "your-secret-key"
    
    # Inicializa o banco de dados com o app.
    # Como o modelo já foi importado, o create_all() criará a tabela "cliente"
    init_db(app)
    
    # Importa e registra as rotas dentro do contexto do app
    with app.app_context():
        from routes.admin import bp_admin
        app.register_blueprint(bp_admin)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)



def format_real(value):
    """
    Formata um valor numérico para o formato de moeda brasileira:
    Exemplo: 100000.0 -> R$100.000,00
    """
    return "R${:,.2f}".format(value).replace(",", "X").replace(".", ",").replace("X", ".")

# Após criar o app
app = create_app()
app.jinja_env.filters['real'] = format_real 