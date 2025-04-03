# routes/notificacoes.py
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models.db import db
from models.notificacao import Notificacao
from datetime import datetime

notificacoes_bp = Blueprint('notificacoes', __name__, url_prefix='/notificacoes')

@notificacoes_bp.route('/')
@login_required
def notificacoes():
    return render_template('admin/notificacoes.html')

@notificacoes_bp.route('/listar', methods=['GET'])
@login_required
def listar_notificacoes():
    notificacoes = Notificacao.query.filter_by(usuario_id=current_user.id).all()
    eventos = {}
    for n in notificacoes:
        key = n.data.strftime('%Y-%m')
        dia = n.data.day
        if key not in eventos:
            eventos[key] = {}
        if dia not in eventos[key]:
            eventos[key][dia] = []
        eventos[key][dia].append(f"[{n.tipo}] {n.mensagem}")
    return jsonify(eventos)

@notificacoes_bp.route('/adicionar', methods=['POST'])
@login_required
def adicionar_notificacao():
    data = request.json.get('data')
    tipo = request.json.get('tipo')
    mensagem = request.json.get('mensagem')

    if not data or not tipo or not mensagem:
        return jsonify({'erro': 'Dados incompletos'}), 400

    try:
        data_formatada = datetime.strptime(data, "%Y-%m-%d").date()
        nova = Notificacao(
            usuario_id=current_user.id,
            data=data_formatada,
            tipo=tipo,
            mensagem=mensagem
        )
        db.session.add(nova)
        db.session.commit()
        return jsonify({'mensagem': 'Notificação salva com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500
