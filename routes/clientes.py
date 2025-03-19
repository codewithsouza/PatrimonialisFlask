from flask import Blueprint, render_template, request, redirect, url_for

bp_cliente = Blueprint('cliente', __name__, url_prefix='/cliente')

@bp_cliente.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Simulação de usuário cliente (troque por autenticação real)
        if email == "cliente@email.com" and password == "1234":
            return redirect(url_for('cliente.dashboard'))  # Redireciona para a base do cliente

        return "Usuário ou senha inválidos!", 401  # Retorna erro se os dados estiverem errados

    return render_template('cliente/login.html')

@bp_cliente.route('/dashboard')
def dashboard():
    return render_template('cliente/base_cliente.html')  # Página principal do cliente após login

@bp_cliente.route('/cadastro')
def cadastro():
    return render_template('cliente/cadastro.html')  # Criar esse arquivo em templates/cliente/
