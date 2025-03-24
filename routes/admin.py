from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import login_required, current_user
import pandas as pd
import os
from datetime import datetime
from models.db import db
from models.clientes_db import Cliente

bp_admin = Blueprint('admin', __name__, url_prefix='/admin')

# Página principal
@bp_admin.route('/')
@login_required
def index():
    total = Cliente.query.filter_by(usuario_id=current_user.id).count()
    return render_template('admin/index.html', total_clientes=total)

# Lista de clientes cadastrados
@bp_admin.route('/clientes_cadastrados')
@login_required
def clientes_cadastrados():
    clientes = Cliente.query.filter_by(usuario_id=current_user.id).all()
    return render_template('admin/clientes_cadastrados.html', clientes=clientes)

# Adicionar cliente no banco
@bp_admin.route('/adicionar_cliente', methods=['POST'])
@login_required
def adicionar_cliente():
    data = request.get_json()

    nome = data.get('nome')
    cnpj = data.get('cnpj')
    regime = data.get('regime')
    try:
        divida = float(data.get('divida', 0))
    except (ValueError, TypeError):
        divida = 0
    contrato = data.get('contrato')
    segmento = data.get('segmento', '')
    logradouro = data.get('logradouro')
    numero = data.get('numero')
    bairro = data.get('bairro')
    municipio = data.get('municipio')
    email = data.get('email')
    telefone = data.get('telefone')
    cep = data.get('cep')

    monitoramento_valor = data.get('monitoramento')
    monitoramento = True if monitoramento_valor in [True, "on", "true", "True", "1"] else False
    data_monitoramento_str = data.get('data_monitoramento')
    data_monitoramento = datetime.strptime(data_monitoramento_str, "%Y-%m-%d").date() if data_monitoramento_str else None
    situacao_fiscal = data.get('situacao_fiscal')
    observacoes = data.get('observacoes')

    if not nome or not cnpj:
        return jsonify({"message": "Nome e CNPJ são obrigatórios!"}), 400

    if Cliente.query.filter_by(cnpj=cnpj, usuario_id=current_user.id).first():
        return jsonify({"message": "Erro: Já existe um cliente com esse CNPJ!"}), 400

    novo_cliente = Cliente(
        nome=nome,
        cnpj=cnpj,
        regime=regime,
        divida=divida,
        contrato=contrato,
        segmento=segmento,
        logradouro=logradouro,
        numero=numero,
        bairro=bairro,
        municipio=municipio,
        email=email,
        telefone=telefone,
        cep=cep,
        monitoramento=monitoramento,
        data_monitoramento=data_monitoramento,
        situacao_fiscal=situacao_fiscal,
        observacoes=observacoes,
        usuario_id=current_user.id
    )

    try:
        db.session.add(novo_cliente)
        db.session.commit()
        return jsonify({"message": "Cliente cadastrado com sucesso!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erro ao cadastrar cliente: {str(e)}"}), 500

# Excluir Cliente
@bp_admin.route('/excluir_cliente/<int:id>', methods=['POST'])
@login_required
def excluir_cliente(id):
    cliente = Cliente.query.filter_by(id=id, usuario_id=current_user.id).first()
    if cliente:
        db.session.delete(cliente)
        db.session.commit()
        flash("Cliente excluído com sucesso!", "success")
        return jsonify({"success": True, "message": "Cliente excluído com sucesso!"})
    else:
        flash("Erro: Cliente não encontrado!", "danger")
        return jsonify({"success": False, "message": "Cliente não encontrado!"}), 404

# Exportar clientes para CSV
@bp_admin.route('/exportar')
@login_required
def exportar():
    clientes = Cliente.query.filter_by(usuario_id=current_user.id).all()
    if not clientes:
        flash("Nenhum cliente para exportar!", "danger")
        return redirect(url_for('admin.clientes_cadastrados'))

    df = pd.DataFrame([{
        "ID": c.id,
        "Nome": c.nome,
        "CNPJ": c.cnpj,
        "Regime": c.regime,
        "Dívida": c.divida,
        "Contrato": c.contrato,
        "Segmento": c.segmento
    } for c in clientes])

    os.makedirs("static", exist_ok=True)
    file_path = os.path.join("static", "clientes_export.csv")
    df.to_csv(file_path, index=False)

    flash("Clientes exportados com sucesso!", "success")
    return send_file(file_path, as_attachment=True)

# Importar clientes de CSV/Excel (não implementado ainda)
@bp_admin.route('/importar', methods=['POST'])
@login_required
def importar():
    file = request.files.get('file')
    if not file:
        flash("Nenhum arquivo foi enviado!", "danger")
        return redirect(url_for('admin.clientes_cadastrados'))

    # Lógica de importação a ser implementada futuramente
    flash("Importação realizada com sucesso!", "success")
    return redirect(url_for('admin.clientes_cadastrados'))

# Editar cliente
@bp_admin.route('/editar_cliente/<int:id>', methods=['POST'])
@login_required
def editar_cliente(id):
    data = request.get_json()
    cliente = Cliente.query.filter_by(id=id, usuario_id=current_user.id).first()

    if not cliente:
        return jsonify({'success': False, 'message': 'Cliente não encontrado.'}), 404

    cliente.nome = data.get('nome', cliente.nome)
    cliente.cnpj = data.get('cnpj', cliente.cnpj)
    cliente.regime = data.get('regime', cliente.regime)
    try:
        cliente.divida = float(data.get('divida', cliente.divida))
    except (ValueError, TypeError):
        pass
    cliente.contrato = data.get('contrato', cliente.contrato)
    cliente.segmento = data.get('segmento', cliente.segmento)
    cliente.logradouro = data.get('logradouro', cliente.logradouro)
    cliente.numero = data.get('numero', cliente.numero)
    cliente.bairro = data.get('bairro', cliente.bairro)
    cliente.municipio = data.get('municipio', cliente.municipio)
    cliente.email = data.get('email', cliente.email)
    cliente.telefone = data.get('telefone', cliente.telefone)
    cliente.cep = data.get('cep', cliente.cep)

    monitoramento_valor = data.get('monitoramento')
    cliente.monitoramento = True if monitoramento_valor in [True, "on", "true", "True", "1"] else False
    data_monitoramento_str = data.get('data_monitoramento')
    cliente.data_monitoramento = datetime.strptime(data_monitoramento_str, "%Y-%m-%d").date() if data_monitoramento_str else None
    cliente.situacao_fiscal = data.get('situacao_fiscal', cliente.situacao_fiscal)
    cliente.observacoes = data.get('observacoes', cliente.observacoes)

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Cliente atualizado com sucesso.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao atualizar o cliente: {str(e)}'}), 500
