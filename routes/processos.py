from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models.db import db
from models.processos import Processo
from datetime import date

# Criando o Blueprint
bp_processos = Blueprint('processos', __name__, url_prefix='/processos')

# -------------------- LISTAR TODOS OS PROCESSOS --------------------
@bp_processos.route('/')
@login_required
def listar_processos():
    processos = Processo.query.all()  # Futuramente podemos filtrar pelo current_user se precisar
    return render_template('admin/processos.html', processos=processos)

# -------------------- DETALHAR UM PROCESSO --------------------
@bp_processos.route('/<int:id>')
@login_required
def detalhar_processo(id):
    processo = Processo.query.get_or_404(id)
    return render_template('admin/detalhar_processo.html', processo=processo)

# -------------------- FILTRAR PROCESSOS --------------------
@bp_processos.route('/filtro')
@login_required
def filtrar_processos():
    esfera = request.args.get('esfera', None)
    status = request.args.get('status', None)
    vara = request.args.get('vara', None)

    query = Processo.query

    if esfera:
        query = query.filter_by(esfera=esfera)
    if status:
        query = query.filter_by(status=status)
    if vara:
        query = query.filter_by(vara=vara)

    processos = query.all()

    return render_template('admin/processos.html', processos=processos)

# -------------------- API - GRÁFICO DE STATUS --------------------
@bp_processos.route('/api/status_processos')
@login_required
def api_status_processos():
    status_contagem = db.session.query(
        Processo.status,
        db.func.count(Processo.id)
    ).group_by(Processo.status).all()

    return jsonify({
        "labels": [s[0] for s in status_contagem],
        "valores": [s[1] for s in status_contagem]
    })
