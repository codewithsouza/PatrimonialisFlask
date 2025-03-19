from flask import Flask
from routes.admin import bp_admin
from routes.clientes import bp_cliente  # Certifique-se que está importando corretamente!

app = Flask(__name__)
app.secret_key = "chave_secreta_super_segura"  # Necessário para flash e sessão

# ✅ Registrando os Blueprints
app.register_blueprint(bp_admin)
app.register_blueprint(bp_cliente)  # Aqui garantimos que a rota do cliente está ativa

if __name__ == '__main__':
    app.run(debug=True)
