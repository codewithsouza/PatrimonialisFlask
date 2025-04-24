from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db
from models.cliente import Cliente

cliente_bp = Blueprint('cliente', __name__)

@cliente_bp.route('/')
def home():
    clientes = Cliente.query.all()
    return render_template('index.html', clientes=clientes)

@cliente_bp.route('/create', methods=['POST'])
def create():
    if request.method == 'POST':
        nome = request.form['nome']
        cnpj = request.form['cnpj']
        regime = request.form['regime']
        divida = float(request.form['divida'])
        contrato = request.form['contrato']
        segmento = request.form['segmento']
        
        cliente = Cliente(nome, cnpj, regime, divida, contrato, segmento)
        db.session.add(cliente)
        db.session.commit()
        
        flash('Cliente adicionado com sucesso!')
        return redirect(url_for('cliente.home'))

@cliente_bp.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    cliente = Cliente.query.get_or_404(id)
    
    if request.method == 'POST':
        cliente.nome = request.form['nome']
        cliente.cnpj = request.form['cnpj']
        cliente.regime = request.form['regime']
        cliente.divida = float(request.form['divida'])
        cliente.contrato = request.form['contrato']
        cliente.segmento = request.form['segmento']
        
        db.session.commit()
        flash('Cliente atualizado com sucesso!')
        return redirect(url_for('cliente.home'))
    
    return render_template('update.html', cliente=cliente)

@cliente_bp.route('/delete/<int:id>')
def delete(id):
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()
    
    flash('Cliente excluído com sucesso!')
    return redirect(url_for('cliente.home'))