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
from models.processos import Processo




bp_admin = Blueprint('admin', __name__, url_prefix='/admin')

# --------------------- ROTAS DE DASHBOARD ---------------------
@bp_admin.route('/')
@login_required
def index():
    total_clientes = Cliente.query.filter_by(usuario_id=current_user.id).count()
    total_divida = db.session.query(func.sum(Cliente.divida)).filter_by(usuario_id=current_user.id).scalar() or 0
    processos_ativos = Cliente.query.filter_by(usuario_id=current_user.id, monitoramento=True).count()

    hoje = date.today()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    fim_semana = inicio_semana + timedelta(days=6)

    eventos_semana = Notificacao.query.filter(
        Notificacao.usuario_id == current_user.id,
        Notificacao.data.between(inicio_semana, fim_semana)
    ).count()

    return render_template(
        'admin/index.html',
        total_clientes=total_clientes,
        total_divida=total_divida,
        processos_ativos=processos_ativos,
        eventos_semana=eventos_semana
    )

# --------------------- ROTAS DE CLIENTES ---------------------
@bp_admin.route('/clientes_cadastrados')
@login_required
def clientes_cadastrados():
    pagina = request.args.get("page", 1, type=int)
    por_pagina = 15

    query = Cliente.query.filter_by(usuario_id=current_user.id)
    total = query.count()

    clientes = query.order_by(Cliente.id)\
        .offset((pagina - 1) * por_pagina)\
        .limit(por_pagina)\
        .all()

    total_paginas = (total + por_pagina - 1) // por_pagina

    return render_template('admin/clientes_cadastrados.html',
                           clientes=clientes,
                           page=pagina,
                           total_paginas=total_paginas)

# --------------------- ROTAS DE DÍVIDAS ---------------------
@bp_admin.route('/divida_ativa')
@login_required
def divida_ativa():
    clientes = Cliente.query.filter_by(usuario_id=current_user.id, monitoramento=True).all()
    dividas = Divida.query.filter_by(usuario_id=current_user.id).all()

    total_dividas = sum(c.divida or 0 for c in clientes)
    total_pago = sum(d.valor_pago or 0 for d in dividas)
    total_baixadas = sum(
        d.valor_pago for d in dividas if d.cliente and d.cliente.divida is not None and d.valor_pago == d.cliente.divida
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

@bp_admin.route('/divida_municipal')
@login_required
def divida_municipal():
    return render_template('admin/divida_municipal.html')

@bp_admin.route('/divida_estadual')
@login_required
def divida_estadual():
    return render_template('admin/divida_estadual.html')

@bp_admin.route('/divida_federal')
@login_required
def divida_federal():
    return render_template('admin/divida_federal.html')

# --------------------- OUTRAS PÁGINAS ---------------------
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
@bp_admin.route('admin/cobranca_judicial')


# --------------------- API - GRÁFICO DINÂMICO ---------------------
@bp_admin.route('/api/grafico_dividas')
@login_required
def grafico_dividas():
    dados = db.session.query(
        Cliente.regime,
        func.sum(Cliente.divida)
    ).filter_by(usuario_id=current_user.id).group_by(Cliente.regime).all()

    return jsonify({
        "labels": [r[0] for r in dados],
        "valores": [float(r[1]) for r in dados]
    })

# --------------------- AÇÕES DE CLIENTES ---------------------
@bp_admin.route('/adicionar_cliente', methods=['POST'])
@login_required
def adicionar_cliente():
    data = request.get_json()
    try:
        monitoramento = bool(data.get('monitoramento')) and str(data.get('monitoramento')).lower() in ["true", "1", "on"]

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
            monitoramento=monitoramento,
            data_monitoramento=datetime.strptime(data.get('data_monitoramento'), "%Y-%m-%d").date()
                if data.get('data_monitoramento') else None,
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
        return jsonify({
            "message": "Cliente cadastrado com sucesso!",
            "id": novo_cliente.id
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erro ao cadastrar cliente: {str(e)}"}), 500

@bp_admin.route('/excluir_cliente/<int:id>', methods=['POST'])
@login_required
def excluir_cliente(id):
    cliente = Cliente.query.filter_by(id=id, usuario_id=current_user.id).first()
    if not cliente:
        return jsonify({'message': 'Cliente não encontrado!'}), 404

    try:
        db.session.delete(cliente)
        db.session.commit()
        return jsonify({'message': 'Cliente excluído com sucesso!', 'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao excluir cliente: {str(e)}'}), 500

# --------------------- IMPORTAÇÃO / EXPORTAÇÃO ---------------------
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
    file_name = f"clientes_export_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    file_path = os.path.join("static", file_name)
    df.to_csv(file_path, index=False)

    flash("Clientes exportados com sucesso!", "success")
    return send_file(file_path, as_attachment=True)


@bp_admin.route('/cobranca_judicial')
@login_required
def cobranca_judicial():
    from datetime import date, timedelta
    hoje = date.today()

    # Coleta dos filtros da URL
    empresa = request.args.get('empresa', 'todos')
    status = request.args.get('status', 'todos')
    vara = request.args.get('vara', 'todos')
    esfera = request.args.get('esfera', 'todas')

    # Início da query base
    query = Processo.query

    # Aplicação dos filtros
    if empresa != 'todos':
        query = query.filter_by(empresa=empresa)
    if status != 'todos':
        query = query.filter_by(status=status)
    if vara != 'todos':
        query = query.filter_by(vara=vara)
    if esfera != 'todas':
        query = query.filter_by(esfera=esfera)

    # Obtenção dos dados filtrados
    processos = query.all()

    # Valores totais
    valor_total = sum(p.valor or 0 for p in processos)
    ativos = sum(1 for p in processos if p.status and p.status.lower() == "ativo")

    # Filtros dinâmicos para os selects
    todas_empresas = sorted(set(p.empresa for p in Processo.query.with_entities(Processo.empresa).distinct()))
    todas_varas = sorted(set(p.vara for p in Processo.query.with_entities(Processo.vara).distinct()))

    # Dados dos gráficos
    status_map = {'ativo': 0, 'suspenso': 0, 'encerrado': 0}
    responsaveis_map = {}

    for p in processos:
        status_key = (p.status or '').lower()
        if status_key in status_map:
            status_map[status_key] += 1

        if p.responsavel:
            responsaveis_map[p.responsavel] = responsaveis_map.get(p.responsavel, 0) + 1

    # Dados para os gráficos
    grafico_status_labels = list(status_map.keys())
    grafico_status_valores = list(status_map.values())
    grafico_responsavel_labels = list(responsaveis_map.keys())
    grafico_responsavel_valores = list(responsaveis_map.values())

    return render_template(
        "admin/cobranca_judicial.html",
        processos=processos,
        valor_total=valor_total,
        ativos=ativos,
        hoje=hoje,
        empresas=todas_empresas,
        varas=todas_varas,
        empresa_selecionada=empresa,
        status=status,
        vara=vara,
        esfera=esfera,
        grafico_status_labels=grafico_status_labels,
        grafico_status_valores=grafico_status_valores,
        grafico_responsavel_labels=grafico_responsavel_labels,
        grafico_responsavel_valores=grafico_responsavel_valores
    )




@bp_admin.route("/gerar_guia/<pa_id>")
def gerar_guia(pa_id):
    # lógica para gerar e retornar o PDF
    return send_file(f"guias/{pa_id}.pdf", as_attachment=True)
