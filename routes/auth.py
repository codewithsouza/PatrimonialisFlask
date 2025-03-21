from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from models.usuario import Usuario  # Certifique-se de que a classe se chama "Usuario"
from models.db import db
from flask_login import login_user, logout_user, login_required

bp_auth = Blueprint('auth', __name__, url_prefix='/auth')

@bp_auth.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        data = request.get_json() or request.form
        nome = data.get('nome')
        email = data.get('email')
        senha = data.get('senha')
        confirmar_senha = data.get('confirmar_senha')

        # Validação: as senhas devem ser iguais
        if senha != confirmar_senha:
            flash('As senhas não conferem.', 'danger')
            return redirect(url_for('auth.cadastro'))

        # Verifica se o email já está cadastrado
        if Usuario.query.filter_by(email=email).first():
            flash('Email já cadastrado.', 'warning')
            return redirect(url_for('auth.cadastro'))

        # Cria o usuário e insere no banco de dados
        usuario = Usuario(nome=nome, email=email)
        usuario.set_senha(senha)
        db.session.add(usuario)
        db.session.commit()

        flash('Usuário cadastrado com sucesso!', 'success')
        return redirect(url_for('auth.login'))
    
    # Se for GET, renderiza o template de cadastro
    return render_template('admin/cadastro.html')

@bp_auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json() or request.form
        email = data.get('email')
        senha = data.get('senha')
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.check_senha(senha):
            login_user(usuario)
            return jsonify({'success': True, 'message': 'Login realizado com sucesso.'})
        flash('Credenciais inválidas.', 'danger')
        return redirect(url_for('auth.login'))
    
    return render_template('admin/login.html')

@bp_auth.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'success': True, 'message': 'Logout realizado com sucesso.'})
