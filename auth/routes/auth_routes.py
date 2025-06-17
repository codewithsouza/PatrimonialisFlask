from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models.db import db
from models.usuario import Usuario
from models.clientes_db import Cliente

auth_bp = Blueprint('auth', __name__)

# --------------------- ROTAS DE LOGIN ---------------------
@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.index'))
        return redirect(url_for('cliente.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and usuario.check_senha(senha) and usuario.is_admin:
            login_user(usuario)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.index'))
            
        flash('Email ou senha inválidos, ou você não tem permissão de administrador', 'error')
    
    return render_template('auth/admin_login.html')

@auth_bp.route('/cliente/login', methods=['GET', 'POST'])
def cliente_login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.index'))
        return redirect(url_for('cliente.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and usuario.check_senha(senha) and not usuario.is_admin:
            login_user(usuario)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('cliente.index'))
            
        flash('Email ou senha inválidos', 'error')
    
    return render_template('auth/cliente_login.html')

# --------------------- ROTAS DE CADASTRO ---------------------
@auth_bp.route('/admin/cadastro', methods=['GET', 'POST'])
def admin_cadastro():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.index'))
        return redirect(url_for('cliente.index'))

    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        confirmar_senha = request.form.get('confirmar_senha')
        codigo_admin = request.form.get('codigo_admin')
        
        if senha != confirmar_senha:
            flash('As senhas não coincidem', 'error')
            return render_template('auth/admin_cadastro.html')
        
        if Usuario.query.filter_by(email=email).first():
            flash('Email já cadastrado', 'error')
            return render_template('auth/admin_cadastro.html')
        
        # Verificar código de administrador
        if codigo_admin != 'ADMIN123':  # Você pode mudar este código ou colocar em variável de ambiente
            flash('Código de administrador inválido', 'error')
            return render_template('auth/admin_cadastro.html')
        
        usuario = Usuario(nome=nome, email=email, is_admin=True)
        usuario.set_senha(senha)
        
        try:
            db.session.add(usuario)
            db.session.commit()
            flash('Cadastro de administrador realizado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('auth.admin_login'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao realizar cadastro. Tente novamente.', 'error')
    
    return render_template('auth/admin_cadastro.html')

@auth_bp.route('/cliente/cadastro', methods=['GET', 'POST'])
def cliente_cadastro():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.index'))
        return redirect(url_for('cliente.index'))

    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        confirmar_senha = request.form.get('confirmar_senha')
        
        if senha != confirmar_senha:
            flash('As senhas não coincidem', 'error')
            return render_template('auth/cliente_cadastro.html')
        
        if Usuario.query.filter_by(email=email).first():
            flash('Email já cadastrado', 'error')
            return render_template('auth/cliente_cadastro.html')
        
        usuario = Usuario(nome=nome, email=email, is_admin=False)
        usuario.set_senha(senha)
        
        try:
            db.session.add(usuario)
            db.session.commit()
            flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('auth.cliente_login'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao realizar cadastro. Tente novamente.', 'error')
    
    return render_template('auth/cliente_cadastro.html')

# --------------------- ROTAS DE LOGOUT ---------------------
@auth_bp.route('/admin/logout')
@login_required
def admin_logout():
    if not current_user.is_admin:
        flash('Acesso não autorizado', 'error')
        return redirect(url_for('cliente.index'))
    
    logout_user()
    flash('Você foi desconectado', 'info')
    return redirect(url_for('auth.admin_login'))

@auth_bp.route('/cliente/logout')
@login_required
def cliente_logout():
    if current_user.is_admin:
        flash('Acesso não autorizado', 'error')
        return redirect(url_for('admin.index'))
    
    logout_user()
    flash('Você foi desconectado', 'info')
    return redirect(url_for('auth.cliente_login')) 