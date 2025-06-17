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
from models.parcelamentos_db import Parcelamento
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
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
    cliente_id = request.args.get("cliente_id", type=int)
    
    clientes = Cliente.query.filter_by(usuario_id=current_user.id, monitoramento=True).all()

    if cliente_id:
        cliente = Cliente.query.filter_by(id=cliente_id, usuario_id=current_user.id).first()
        dividas = Divida.query.filter_by(usuario_id=current_user.id, cliente_id=cliente.id, esfera="Municipal").all()
    else:
        cliente = None
        dividas = Divida.query.filter_by(usuario_id=current_user.id, esfera="Municipal").all()

    total_divida_municipal = sum(d.valor_total for d in dividas)

    # dados para gráficos
    composicao = {}
    pagamentos = {}

    for d in dividas:
        composicao[d.tributo] = composicao.get(d.tributo, 0) + d.valor_total
        ano = str(d.ano)
        pagamentos[ano] = pagamentos.get(ano, 0) + d.valor_total

    return render_template(
        "admin/divida_municipal.html",
        clientes=clientes,
        cliente=cliente,
        dividas=dividas,
        composicao=composicao,
        pagamentos=pagamentos,
        total_divida_municipal=total_divida_municipal
    )




@bp_admin.route('/dividas_federais')
@login_required
def dividas_federais():
    try:
        # Configurando modo de debug (remover em produção)
        debug = request.args.get('debug', 'false').lower() == 'true'
        
        # Obtendo cliente do usuário atual
        cliente = Cliente.query.filter_by(usuario_id=current_user.id).first()
        
        # Log para debug
        logger.info(f"Usuário ID: {current_user.id}, Cliente encontrado: {cliente is not None}")
        
        # Obter tributos selecionados para filtragem
        tributos_selecionados = request.args.getlist('tributo')
        periodo = request.args.get('periodo')
        
        # Consulta base para dívidas federais
        query = Divida.query.filter_by(usuario_id=current_user.id, esfera='Federal')
        
        # Aplicar filtros se existirem
        if tributos_selecionados:
            query = query.filter(Divida.tributo.in_(tributos_selecionados))
        
        # Buscar dívidas com filtros aplicados
        dividas = query.all()
        
        # Log para debug
        logger.info(f"Número de dívidas encontradas: {len(dividas)}")
        
        # Se não houver cliente, retornar template com valores vazios
        if not cliente:
            return render_template('admin/dividas_federais.html',
                                cliente=None,
                                dividas=[],
                                parcelamentos=[],
                                valor_total=0,
                                tributos=[],
                                valores_tributos=[],
                                anos_pagamento=[],
                                valores_pagamento=[],
                                periodo=periodo,
                                debug=debug)
        
        # Buscar parcelamentos
        parcelamentos = Parcelamento.query.filter_by(cliente_id=cliente.id).all()
        
        # Calcular valor total das dívidas
        valor_total = sum(d.valor_total for d in dividas) if dividas else 0
        
        # Obter lista única de tributos para filtros e gráficos
        # Primeiro, obter TODOS os tributos para o filtro
        todos_tributos = [d.tributo for d in Divida.query.filter_by(usuario_id=current_user.id, esfera='Federal').distinct(Divida.tributo)]
        todos_tributos = list(set(todos_tributos))  # Remover duplicatas
        
        # Depois, obter valores para tributos filtrados
        tributos = list({d.tributo for d in dividas})
        valores_tributos = [sum(d.valor_total for d in dividas if d.tributo == tributo) for tributo in tributos]
        
        # Dados para o gráfico de pagamentos
        anos_pagamento = ['2021', '2022', '2023']
        valores_pagamento = [2500, 3900, 5800]  # Exemplo - substituir por dados reais
        
        # Log para debug
        logger.info(f"Tributos: {tributos}")
        logger.info(f"Valores tributos: {valores_tributos}")
        
        return render_template('admin/dividas_federais.html',
                            cliente=cliente,
                            dividas=dividas,
                            parcelamentos=parcelamentos,
                            valor_total=valor_total,
                            tributos=todos_tributos,  # Todos os tributos para filtro
                            valores_tributos=valores_tributos,
                            anos_pagamento=anos_pagamento,
                            valores_pagamento=valores_pagamento,
                            periodo=periodo,
                            debug=debug)
    except Exception as e:
        logger.error(f"Erro ao carregar dividas federais: {str(e)}")
        flash(f"Erro ao carregar dados: {str(e)}", "danger")
        return render_template('admin/dividas_federais.html',
                            cliente=None,
                            dividas=[],
                            parcelamentos=[],
                            valor_total=0,
                            tributos=[],
                            valores_tributos=[],
                            anos_pagamento=[],
                            valores_pagamento=[],
                            debug=True)  # Forçar debug em caso de erro

@bp_admin.route('/gerar_guia/<int:divida_id>')
@login_required
def gerar_guia(divida_id):
    # Implementação para gerar guia de pagamento
    # Exemplo simples:
    divida = Divida.query.get_or_404(divida_id)
    
    # Verificar se a dívida pertence ao usuário
    if divida.usuario_id != current_user.id:
        flash("Você não tem permissão para acessar essa dívida.", "danger")
        return redirect(url_for('bp_admin.dividas_federais'))
    
    # Lógica para gerar a guia PDF aqui
    flash(f"Guia de pagamento para dívida {divida_id} gerada com sucesso!", "success")
    return redirect(url_for('bp_admin.dividas_federais'))


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
    page = request.args.get('page', 1, type=int)
    empresa = request.args.get('empresa', 'todos')
    status = request.args.get('status', 'todos')
    vara = request.args.get('vara', 'todos')
    esfera = request.args.get('esfera', 'todas')

    # Buscar apenas clientes monitorados do usuário logado
    clientes_monitoramento = Cliente.query.filter_by(monitoramento=1, usuario_id=current_user.id).all()
    empresas = [cliente.nome for cliente in clientes_monitoramento]

    # Montar consulta de processos
    query = Processo.query

    if empresa != 'todos':
        query = query.filter_by(empresa=empresa)
    if status != 'todos':
        query = query.filter_by(status=status)
    if vara != 'todos':
        query = query.filter_by(vara=vara)
    if esfera != 'todas':
        query = query.filter_by(esfera=esfera)

    processos = query.paginate(page=page, per_page=10)

    # Dados para os gráficos
    grafico_status_labels = ['Ativos', 'Suspensos', 'Encerrados']
    grafico_status_valores = [
        len([p for p in processos.items if p.status == 'ativo']),
        len([p for p in processos.items if p.status == 'suspenso']),
        len([p for p in processos.items if p.status == 'encerrado'])
    ]

    grafico_responsavel_labels = list(set([p.responsavel for p in processos.items if p.responsavel]))
    grafico_responsavel_valores = [sum(1 for p in processos.items if p.responsavel == label) for label in grafico_responsavel_labels]

    valor_total = sum([p.valor or 0 for p in processos.items])
    ativos = sum(1 for p in processos.items if p.status == 'ativo')

    # Buscar varas únicas para o filtro
    varas = db.session.query(Processo.vara).distinct().all()
    varas = [v[0] for v in varas if v[0]]

    return render_template('admin/cobranca_judicial.html',
        empresas=empresas,
        empresa_selecionada=empresa,
        status=status,
        vara=vara,
        esfera=esfera,
        processos=processos,
        grafico_status_labels=grafico_status_labels,
        grafico_status_valores=grafico_status_valores,
        grafico_responsavel_labels=grafico_responsavel_labels,
        grafico_responsavel_valores=grafico_responsavel_valores,
        valor_total=valor_total,
        ativos=ativos,
        hoje=date.today(),
        varas=varas
    )

@bp_admin.route("/adicionar_debito", methods=["POST"])
@login_required
def adicionar_debito():
    try:
        dados = request.get_json()

        cliente_id = int(dados.get("cliente_id"))  # vem do formulário oculto

        cliente = Cliente.query.filter_by(id=cliente_id, usuario_id=current_user.id).first()
        if not cliente:
            return jsonify({"mensagem": "Cliente não encontrado para este usuário."}), 400

        novo_debito = Divida(
            tributo=dados.get("tributo"),
            municipio=dados.get("municipio"),
            ano=int(dados.get("ano")),
            status=dados.get("status"),
            valor_total=float(dados.get("valor")),
            pa=dados.get("pa"),
            esfera='Municipal',  # ← Aqui está a mudança
            cliente_id=cliente.id,
            usuario_id=current_user.id
)


        db.session.add(novo_debito)
        db.session.commit()
        return jsonify({"mensagem": "Débito adicionado com sucesso"}), 200

    except Exception as e:
        return jsonify({"mensagem": f"Erro ao salvar o débito: {str(e)}"}), 500

@bp_admin.route("/api/tributos_por_cidade")
@login_required
def tributos_por_cidade():
    cidade = request.args.get("cidade")
    if not cidade:
        return jsonify([])

    resultados = db.session.execute(
        db.select(func.distinct(TributoMunicipal.tributo)).where(TributoMunicipal.cidade == cidade)
    ).scalars().all()

    return jsonify(resultados)

@bp_admin.route('/api/tributos_por_municipio')
@login_required
def tributos_por_municipio():
    municipio = request.args.get('municipio')

    if not municipio:
        return jsonify([])

    resultados = db.session.execute(
        "SELECT tributo FROM tributos_municipais WHERE municipio = :municipio",
        {"municipio": municipio}
    ).fetchall()

    tributos = [r[0] for r in resultados]
    return jsonify(tributos)


@bp_admin.route("/adicionar_debito_estadual", methods=["POST"])
@login_required
def adicionar_debito_estadual():
    try:
        data = request.get_json()

        cliente_id = int(data.get("cliente_id"))
        cliente = Cliente.query.filter_by(id=cliente_id, usuario_id=current_user.id).first()
        if not cliente:
            return jsonify({"mensagem": "Cliente não encontrado para este usuário."}), 400

        novo_debito = Divida(
            tributo=data.get("tributo"),
            municipio=data.get("estado"),
            ano=int(data.get("ano")),
            status=data.get("status"),
            valor_total=float(data.get("valor")),
            pa=data.get("pa"),
            esfera='Estadual',
            cliente_id=cliente.id,
            usuario_id=current_user.id
        )

        db.session.add(novo_debito)
        db.session.commit()
        return jsonify({"mensagem": "Débito estadual adicionado com sucesso!"}), 200

    except Exception as e:
        return jsonify({"mensagem": f"Erro ao salvar o débito: {str(e)}"}), 500

@bp_admin.route('/divida_estadual')
@login_required
def divida_estadual():
    cliente_id = request.args.get("cliente_id", type=int)

    clientes = Cliente.query.filter_by(usuario_id=current_user.id, monitoramento=True).all()

    if cliente_id:
        cliente = Cliente.query.filter_by(id=cliente_id, usuario_id=current_user.id).first()
        dividas = Divida.query.filter_by(usuario_id=current_user.id, cliente_id=cliente.id, esfera="Estadual").all()
    else:
        cliente = None
        dividas = Divida.query.filter_by(usuario_id=current_user.id, esfera="Estadual").all()

    total_divida_estadual = sum(d.valor_total for d in dividas)

    composicao = {}
    pagamentos = {}

    for d in dividas:
        composicao[d.tributo] = composicao.get(d.tributo, 0) + d.valor_total
        ano = str(d.ano)
        pagamentos[ano] = pagamentos.get(ano, 0) + d.valor_total

    return render_template(
        "admin/divida_estadual.html",
        clientes=clientes,
        cliente=cliente,
        dividas=dividas,
        composicao=composicao,
        pagamentos=pagamentos,
        total_divida_estadual=total_divida_estadual
    )

@bp_admin.route('/api/divida_empresa')
@login_required
def divida_empresa():
    empresa = request.args.get('empresa')
    if not empresa or empresa == 'todos':
        return jsonify({
            'valor_total': 0,
            'ativos': 0,
            'status': {'Ativos': 0, 'Suspensos': 0, 'Encerrados': 0},
            'responsavel': {}
        })

    # Buscar processos da empresa
    processos = Processo.query.filter_by(empresa=empresa).all()
    
    # Calcular totais
    valor_total = sum(p.valor or 0 for p in processos)
    ativos = sum(1 for p in processos if p.status == 'ativo')
    
    # Dados para gráfico de status
    status = {
        'Ativos': sum(1 for p in processos if p.status == 'ativo'),
        'Suspensos': sum(1 for p in processos if p.status == 'suspenso'),
        'Encerrados': sum(1 for p in processos if p.status == 'encerrado')
    }
    
    # Dados para gráfico de responsável
    responsavel = {}
    for p in processos:
        if p.responsavel:
            responsavel[p.responsavel] = responsavel.get(p.responsavel, 0) + 1

    return jsonify({
        'valor_total': valor_total,
        'ativos': ativos,
        'status': status,
        'responsavel': responsavel
    })

@bp_admin.route('/api/processos')
@login_required
def api_processos():
    page = request.args.get('page', 1, type=int)
    empresa = request.args.get('empresa', 'todos')
    status = request.args.get('status', 'todos')
    vara = request.args.get('vara', 'todos')
    esfera = request.args.get('esfera', 'todas')

    # Montar consulta de processos
    query = Processo.query.filter_by(usuario_id=current_user.id)

    if empresa != 'todos':
        query = query.filter_by(empresa=empresa)
    if status != 'todos':
        query = query.filter_by(status=status)
    if vara != 'todos':
        query = query.filter_by(vara=vara)
    if esfera != 'todas':
        query = query.filter_by(esfera=esfera)

    processos = query.paginate(page=page, per_page=10)

    # Formatar dados para JSON
    processos_data = []
    for p in processos.items:
        prazo_proximo = False
        if p.prazos:
            prazo_proximo = p.prazos <= date.today() + timedelta(days=7)

        processos_data.append({
            'numero': p.numero,
            'empresa': p.empresa,
            'vara': p.vara,
            'valor': p.valor or 0,
            'status': p.status,
            'garantia': p.garantia or '-',
            'prazos': p.prazos.strftime('%d/%m/%Y') if p.prazos else '-',
            'prazo_proximo': prazo_proximo
        })

    return jsonify({
        'processos': processos_data,
        'total': processos.total,
        'pages': processos.pages,
        'current_page': processos.page,
        'has_next': processos.has_next,
        'has_prev': processos.has_prev
    })