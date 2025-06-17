from flask import Blueprint, render_template, request, redirect, url_for

bp_clientes = Blueprint('cliente', __name__, url_prefix='/cliente')

@bp_clientes.route('/cadastro')
def cadastro():
    return render_template('cliente/cliente_cadastro.html')
