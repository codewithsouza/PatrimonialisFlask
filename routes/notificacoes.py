from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models.db import db
from models.notificacoes_db import Evento
from datetime import datetime

notificacoes_bp = Blueprint('notificacoes', __name__, url_prefix='/notificacoes')

@notificacoes_bp.route('/')
@login_required
def notificacoes_index():
    return render_template('admin/notificacoes.html')

@notificacoes_bp.route('/listar')
@login_required
def listar_notificacoes():
    try:
        eventos = Evento.query.filter_by(usuario_id=current_user.id).all()
        resultado = {}
        for e in eventos:
            mes = e.data_evento.strftime("%Y-%m")
            dia = e.data_evento.day
            if mes not in resultado:
                resultado[mes] = {}
            if dia not in resultado[mes]:
                resultado[mes][dia] = []
            # Formato que o JS espera: [tipo] titulo | descricao
            resultado[mes][dia].append(f"[{e.tipo}] {e.titulo} | {e.descricao or ''}")
        return jsonify(resultado)
    except Exception as e:
        print("Erro em listar_notificacoes():", e)
        return jsonify({"erro": str(e)}), 500

@notificacoes_bp.route('/adicionar', methods=['POST'])
@login_required
def adicionar_notificacao():
    dados = request.get_json()
    try:
        nova = Evento(
            titulo=dados.get('mensagem'),  # mensagem → titulo
            descricao=dados.get('descricao'),  # ← adicione se estiver usando
            tipo=dados.get('tipo'),
            data_evento=datetime.strptime(dados.get('data'), "%Y-%m-%d").date(),
            usuario_id=current_user.id
        )
        db.session.add(nova)
        db.session.commit()
        return jsonify({"status": "ok"})
    except Exception as e:
        db.session.rollback()
        print("Erro ao adicionar notificação:", e)
        return jsonify({"erro": str(e)}), 500