from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.db import db
from models.clientes_db import Cliente
from .. import cliente_bp

@cliente_bp.route('/')
@login_required
def index():
    # Aqui você pode adicionar a lógica específica para o dashboard do cliente
    return render_template('cliente/index.html')

@cliente_bp.route('/perfil')
@login_required
def perfil():
    # Lógica para exibir o perfil do cliente
    return render_template('cliente/perfil.html')

@cliente_bp.route('/documentos')
@login_required
def documentos():
    # Lógica para exibir os documentos do cliente
    return render_template('cliente/documentos.html')

@cliente_bp.route('/dividas')
@login_required
def dividas():
    # Lógica para exibir as dívidas do cliente
    return render_template('cliente/dividas.html')

@cliente_bp.route('/processos')
@login_required
def processos():
    # Lógica para exibir os processos do cliente
    return render_template('cliente/processos.html') 