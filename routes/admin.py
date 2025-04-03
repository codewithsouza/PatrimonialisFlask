from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import login_required, current_user
import pandas as pd
import os
from datetime import datetime, date, timedelta
from models.db import db
from models.clientes_db import Cliente
from models.divida_db import Divida
from models.notificacao import Notificacao
from sqlalchemy.sql import func

bp_admin = Blueprint('admin', __name__, url_prefix='/admin')

# ROTAS DE PÁGINAS BÁSICAS
@bp_admin.route('/')
@login_required
def index():
    total = Cliente.query.filter_by(usuario_id=current_user.id).count()

    hoje = date.today()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    fim_semana = inicio_semana + timedelta(days=6)

    eventos_semana = Notificacao.query.filter(
        Notificacao.usuario_id == current_user.id,
        Notificacao.data.between(inicio_semana, fim_semana)
    ).count()

    return render_template('admin/index.html', total_clientes=total, eventos_semana=eventos_semana)

@bp_admin.route('/clientes_cadastrados')
@login_required
def clientes_cadastrados():
    clientes = Cliente.query.filter_by(usuario_id=current_user.id).all()
    return render_template('admin/clientes_cadastrados.html', clientes=clientes)

@bp_admin.route('/divida_ativa')
@login_required
def divida_ativa():
    # Apenas clientes com monitoramento ativo
    clientes = Cliente.query.filter_by(usuario_id=current_user.id, monitoramento=True).all()

    # Dívidas associadas ao usuário logado
    dividas = Divida.query.filter_by(usuario_id=current_user.id).all()

    total_dividas = sum(c.divida or 0 for c in clientes)
    total_pago = sum(d.valor_pago or 0 for d in dividas)
    total_baixadas = sum(
        d.valor_pago for d in dividas if d.cliente.divida is not None and d.valor_pago == d.cliente.divida
    )

    data_atualizacao = datetime.now().strftime('%d/%m/%Y %H:%M')

    return render_template(
        'admin/divida_ativa.html',
        clientes=clientes,
        dividas=dividas,
        total_dividas=total_dividas,
        total_pago=total_pago,
        total_baixadas=total_baixadas,
        data_atualizacao=data_atualizacao
    )


@bp_admin.route('/notificacoes')
@login_required
def notificacoes():
    eventos = []
    return render_template('admin/notificacoes.html', eventos=eventos)

@bp_admin.route('/estatisticas')
@login_required
def estatisticas():
    return render_template('admin/estatisticas.html')

@bp_admin.route('/configuracoes')
@login_required
def configuracoes():
    return render_template('admin/configuracoes.html')

@bp_admin.route('/suporte')
@login_required
def suporte():
    return render_template('admin/suporte.html')

@bp_admin.route('/financeiro')
@login_required
def financeiro():
    return render_template('admin/financeiro.html')

@bp_admin.route('/contratos')
@login_required
def contratos():
    return render_template('admin/contratos.html')


# CLIENTE - ADICIONAR
@bp_admin.route('/adicionar_cliente', methods=['POST'])
@login_required
def adicionar_cliente():
    data = request.get_json()
    try:
        novo_cliente = Cliente(
            nome=data.get('nome') or '',
            cnpj=data.get('cnpj') or '',
            regime=data.get('regime') or '',
            divida=float(str(data.get('divida') or '0').replace(',', '.')),
            contrato=data.get('contrato') or '',
            segmento=data.get('segmento') or '',
            logradouro=data.get('logradouro') or '',
            numero=data.get('numero') or '',
            bairro=data.get('bairro') or '',
            municipio=data.get('municipio') or '',
            email=data.get('email') or '',
            telefone=data.get('telefone') or '',
            cep=data.get('cep') or '',
            monitoramento=str(data.get('monitoramento')).lower() in ["true", "1", "on"],
            data_monitoramento=datetime.strptime(data.get('data_monitoramento'), "%Y-%m-%d").date() if data.get('data_monitoramento') else None,
            situacao_fiscal=data.get('situacao_fiscal') or '',
            observacoes=data.get('observacoes') or '',
            usuario_id=current_user.id
        )
    except Exception as e:
        return jsonify({"message": f"Erro no processamento dos dados: {str(e)}"}), 400

    if not novo_cliente.nome or not novo_cliente.cnpj:
        return jsonify({"message": "Nome e CNPJ são obrigatórios!"}), 400

    if Cliente.query.filter_by(cnpj=novo_cliente.cnpj, usuario_id=current_user.id).first():
        return jsonify({"message": "Erro: Já existe um cliente com esse CNPJ!"}), 400

    try:
        db.session.add(novo_cliente)
        db.session.commit()
        return jsonify({"message": "Cliente cadastrado com sucesso!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erro ao cadastrar cliente: {str(e)}"}), 500


# IMPORTAÇÃO (AINDA NÃO IMPLEMENTADA)
@bp_admin.route('/importar', methods=['POST'])
@login_required
def importar():
    file = request.files.get('file')
    if not file:
        flash("Nenhum arquivo foi enviado!", "danger")
        return redirect(url_for('admin.clientes_cadastrados'))

    flash("Importação recebida, mas ainda não implementada.", "info")
    return redirect(url_for('admin.clientes_cadastrados'))



@bp_admin.route('/exportar')
@login_required
def exportar():
    clientes = Cliente.query.filter_by(usuario_id=current_user.id).all()
    if not clientes:
        flash("Nenhum cliente para exportar!", "warning")
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
