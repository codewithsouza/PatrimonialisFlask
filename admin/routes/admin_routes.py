from flask import render_template, request, redirect, url_for, flash, send_file, jsonify
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
from models.parcelamentos_db import Parcelamento
import logging
from . import admin_bp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------- ROTAS DE DASHBOARD ---------------------
@admin_bp.route('/')
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
@admin_bp.route('/clientes_cadastrados')
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

@admin_bp.route('/importar', methods=['POST'])
@login_required
def importar():
    if 'file' not in request.files:
        flash('Nenhum arquivo selecionado', 'error')
        return redirect(url_for('admin.clientes_cadastrados'))
    
    file = request.files['file']
    if file.filename == '':
        flash('Nenhum arquivo selecionado', 'error')
        return redirect(url_for('admin.clientes_cadastrados'))

    if file and file.filename.endswith(('.xlsx', '.csv')):
        try:
            if file.filename.endswith('.xlsx'):
                df = pd.read_excel(file)
            else:
                df = pd.read_csv(file)

            for _, row in df.iterrows():
                cliente = Cliente(
                    nome=row['nome'],
                    cnpj=row['cnpj'],
                    regime=row['regime'],
                    divida=float(row['divida']),
                    contrato=row['contrato'],
                    segmento=row['segmento'],
                    logradouro=row.get('logradouro', ''),
                    numero=row.get('numero', ''),
                    bairro=row.get('bairro', ''),
                    municipio=row.get('municipio', ''),
                    email=row.get('email', ''),
                    telefone=row.get('telefone', ''),
                    cep=row.get('cep', ''),
                    usuario_id=current_user.id
                )
                db.session.add(cliente)

            db.session.commit()
            flash('Arquivo importado com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao importar arquivo: {str(e)}', 'error')
    else:
        flash('Formato de arquivo inválido. Use .xlsx ou .csv', 'error')

    return redirect(url_for('admin.clientes_cadastrados'))

@admin_bp.route('/exportar')
@login_required
def exportar():
    try:
        clientes = Cliente.query.filter_by(usuario_id=current_user.id).all()
        
        # Criar DataFrame
        data = []
        for cliente in clientes:
            data.append({
                'nome': cliente.nome,
                'cnpj': cliente.cnpj,
                'regime': cliente.regime,
                'divida': cliente.divida,
                'contrato': cliente.contrato,
                'segmento': cliente.segmento,
                'logradouro': cliente.logradouro,
                'numero': cliente.numero,
                'bairro': cliente.bairro,
                'municipio': cliente.municipio,
                'email': cliente.email,
                'telefone': cliente.telefone,
                'cep': cliente.cep
            })
        
        df = pd.DataFrame(data)
        
        # Criar arquivo Excel
        output = 'clientes_exportados.xlsx'
        df.to_excel(output, index=False)
        
        # Enviar arquivo
        return send_file(
            output,
            as_attachment=True,
            download_name='clientes_exportados.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        flash(f'Erro ao exportar dados: {str(e)}', 'error')
        return redirect(url_for('admin.clientes_cadastrados'))

# --------------------- ROTAS DE DÍVIDAS ---------------------
@admin_bp.route('/divida_ativa')
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

# --------------------- ROTAS DE COBRANÇA JUDICIAL ---------------------
@admin_bp.route('/cobranca_judicial')
@login_required
def cobranca_judicial():
    processos = Processo.query.join(Cliente).filter(Cliente.usuario_id == current_user.id).all()
    return render_template('admin/cobranca_judicial.html', processos=processos)

# --------------------- ROTAS DE SUPORTE ---------------------
@admin_bp.route('/suporte')
@login_required
def suporte():
    return render_template('admin/suporte.html')

# --------------------- ROTAS DE FINANCEIRO ---------------------
@admin_bp.route('/financeiro')
@login_required
def financeiro():
    parcelamentos = Parcelamento.query.filter_by(usuario_id=current_user.id).all()
    return render_template('admin/financeiro.html', parcelamentos=parcelamentos)

# --------------------- ROTAS DE CONTRATOS ---------------------
@admin_bp.route('/contratos')
@login_required
def contratos():
    return render_template('admin/contratos.html')

# --------------------- ROTAS DE CONFIGURAÇÕES ---------------------
@admin_bp.route('/configuracoes')
@login_required
def configuracoes():
    return render_template('admin/configuracoes.html')

@admin_bp.route('/adicionar_cliente', methods=['GET', 'POST'])
@login_required
def adicionar_cliente():
    if request.method == 'POST':
        nome = request.form.get('nome')
        cnpj = request.form.get('cnpj')
        regime = request.form.get('regime')
        contrato = request.form.get('contrato')
        segmento = request.form.get('segmento')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        cliente = Cliente(
            nome=nome,
            cnpj=cnpj,
            regime=regime,
            contrato=contrato,
            segmento=segmento,
            email=email,
            telefone=telefone,
            usuario_id=current_user.id
        )
        db.session.add(cliente)
        db.session.commit()
        flash('Cliente adicionado com sucesso!', 'success')
        return redirect(url_for('admin.clientes_cadastrados'))
    return render_template('admin/adicionar_cliente.html')

@admin_bp.route('/dividas_federais')
@login_required
def dividas_federais():
    # Buscar dívidas federais do usuário logado
    dividas = Divida.query.filter_by(usuario_id=current_user.id, esfera='Federal').all()
    clientes = Cliente.query.filter_by(usuario_id=current_user.id, monitoramento=True).all()
    cliente = clientes[0] if clientes else None
    valor_total = sum([float(d.valor_total or 0) for d in dividas])
    tributos = list(set([d.tributo for d in dividas]))
    valores_tributos = [sum([float(d.valor_total or 0) for d in dividas if d.tributo == t]) for t in tributos]
    anos_pagamento = list(set([d.ano for d in dividas if d.ano]))
    valores_pagamento = [sum([float(d.valor_pago or 0) for d in dividas if d.ano == a]) for a in anos_pagamento]
    periodo = None
    debug = False
    return render_template('admin/dividas_federais.html',
        dividas=dividas,
        cliente=cliente,
        valor_total=valor_total,
        tributos=tributos,
        valores_tributos=valores_tributos,
        anos_pagamento=anos_pagamento,
        valores_pagamento=valores_pagamento,
        periodo=periodo,
        debug=debug
    )

@admin_bp.route('/divida_estadual')
@login_required
def divida_estadual():
    dividas = Divida.query.filter_by(usuario_id=current_user.id, esfera='Estadual').all()
    clientes = Cliente.query.filter_by(usuario_id=current_user.id, monitoramento=True).all()
    cliente = clientes[0] if clientes else None
    total_divida_estadual = sum([float(d.valor_total or 0) for d in dividas])
    tributos = list(set([d.tributo for d in dividas]))
    valores_tributos = [sum([float(d.valor_total or 0) for d in dividas if d.tributo == t]) for t in tributos]
    anos_pagamento = list(set([d.ano for d in dividas if d.ano]))
    valores_pagamento = [sum([float(d.valor_pago or 0) for d in dividas if d.ano == a]) for a in anos_pagamento]
    periodo = None
    # Composição e pagamentos para os gráficos
    composicao = {t: float(sum([d.valor_total or 0 for d in dividas if d.tributo == t])) for t in tributos}
    pagamentos = {str(a): float(sum([d.valor_pago or 0 for d in dividas if d.ano == a])) for a in anos_pagamento}
    return render_template('admin/divida_estadual.html',
        dividas=dividas,
        clientes=clientes,
        cliente=cliente,
        total_divida_estadual=total_divida_estadual,
        tributos=tributos,
        valores_tributos=valores_tributos,
        anos_pagamento=anos_pagamento,
        valores_pagamento=valores_pagamento,
        periodo=periodo,
        composicao=composicao,
        pagamentos=pagamentos
    )

@admin_bp.route('/divida_municipal')
@login_required
def divida_municipal():
    dividas = Divida.query.filter_by(usuario_id=current_user.id, esfera='Municipal').all()
    clientes = Cliente.query.filter_by(usuario_id=current_user.id, monitoramento=True).all()
    cliente = clientes[0] if clientes else None
    total_divida_municipal = sum([float(d.valor_total or 0) for d in dividas])
    tributos = list(set([d.tributo for d in dividas]))
    valores_tributos = [sum([float(d.valor_total or 0) for d in dividas if d.tributo == t]) for t in tributos]
    anos_pagamento = list(set([d.ano for d in dividas if d.ano]))
    valores_pagamento = [sum([float(d.valor_pago or 0) for d in dividas if d.ano == a]) for a in anos_pagamento]
    periodo = None
    composicao = {t: float(sum([d.valor_total or 0 for d in dividas if d.tributo == t])) for t in tributos}
    pagamentos = {str(a): float(sum([d.valor_pago or 0 for d in dividas if d.ano == a])) for a in anos_pagamento}
    return render_template('admin/divida_municipal.html',
        dividas=dividas,
        clientes=clientes,
        cliente=cliente,
        total_divida_municipal=total_divida_municipal,
        tributos=tributos,
        valores_tributos=valores_tributos,
        anos_pagamento=anos_pagamento,
        valores_pagamento=valores_pagamento,
        periodo=periodo,
        composicao=composicao,
        pagamentos=pagamentos
    )

# ... (outras rotas do admin serão movidas aqui) 