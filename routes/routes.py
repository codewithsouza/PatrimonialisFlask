from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.db import db
from models.notificacao import Notificacao
from datetime import datetime

notificacoes_bp = Blueprint("notificacoes", __name__, url_prefix="/notificacoes")

@notificacoes_bp.route("/listar")
@login_required
def listar():
    eventos = Notificacao.query.filter_by(usuario_id=current_user.id).all()
    return jsonify([e.to_dict() for e in eventos])

@notificacoes_bp.route("/criar", methods=["POST"])
@login_required
def criar():
    data = request.json
    nova = Notificacao(
        usuario_id=current_user.id,
        data=datetime.strptime(data["data"], "%Y-%m-%d").date(),
        tipo=data["tipo"],
        mensagem=data["mensagem"]
    )
    db.session.add(nova)
    db.session.commit()
    return jsonify({"success": True, "id": nova.id})

@notificacoes_bp.route("/remover/<int:id>", methods=["DELETE"])
@login_required
def remover(id):
    notif = Notificacao.query.filter_by(id=id, usuario_id=current_user.id).first()
    if notif:
        db.session.delete(notif)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Notificação não encontrada"}), 404
