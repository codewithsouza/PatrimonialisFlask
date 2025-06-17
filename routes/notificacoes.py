from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models.db import db
from datetime import datetime
from models.notificacoes_db import Notificacao
from datetime import date, timedelta


notificacoes_bp = Blueprint('notificacoes', __name__, url_prefix='/notificacoes')

@notificacoes_bp.route('/')
@login_required
def notificacoes_index():
    return render_template('admin/notificacoes.html')

@notificacoes_bp.route('/listar')
@login_required
def listar_notificacoes():
    try:
        eventos = Notificacao.query.filter_by(usuario_id=current_user.id).all()
        resultado = {}
        for e in eventos:
            mes = e.data.strftime("%Y-%m")
            dia = e.data.day
            if mes not in resultado:
                resultado[mes] = {}
            if dia not in resultado[mes]:
                resultado[mes][dia] = []
            resultado[mes][dia].append({
                "id": e.id,
                "texto": f"[{e.tipo}] {e.mensagem} | {e.descricao or ''}"
            })
        return jsonify(resultado)
    except Exception as e:
        print("Erro em listar_notificacoes():", e)
        return jsonify({"erro": str(e)}), 500


@notificacoes_bp.route('/adicionar', methods=['POST'])
@login_required
def adicionar_notificacao():
    dados = request.get_json()
    try:
        if not dados:
            return jsonify({"erro": "Nenhum dado recebido"}), 400

        data_str = dados.get('data')
        tipo = dados.get('tipo')
        mensagem = dados.get('mensagem')
        descricao = dados.get('descricao', '')

        if not all([data_str, tipo, mensagem]):
            return jsonify({"erro": "Campos obrigatórios ausentes"}), 400

        nova = Notificacao(
            mensagem=mensagem,
            descricao=descricao,
            tipo=tipo,
            data=datetime.strptime(data_str, "%Y-%m-%d").date(),
            usuario_id=current_user.id
        )
        db.session.add(nova)
        db.session.commit()
        return jsonify({"status": "ok"})

    except Exception as e:
        db.session.rollback()
        print("Erro ao adicionar notificação:", e)
        return jsonify({"erro": str(e)}), 500



@notificacoes_bp.route('/tem_novas')
@login_required
def tem_novas_notificacoes():
    hoje = date.today()
    sete_dias = hoje + timedelta(days=7)

    existe = db.session.query(Notificacao.id)\
        .filter(Notificacao.usuario_id == current_user.id)\
        .filter(Notificacao.data >= hoje)\
        .filter(Notificacao.data <= sete_dias)\
        .first()

    return jsonify({"nova": existe is not None})


@notificacoes_bp.route('/excluir/<int:id>', methods=['DELETE'])
@login_required
def excluir_notificacao(id):
    try:
        notif = Notificacao.query.filter_by(id=id, usuario_id=current_user.id).first_or_404()
        db.session.delete(notif)
        db.session.commit()
        return jsonify({"status": "ok"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": str(e)}), 500


@notificacoes_bp.route('/editar/<int:id>', methods=['POST'])
@login_required
def editar_notificacao(id):
    dados = request.get_json()
    try:
        notif = Notificacao.query.filter_by(id=id, usuario_id=current_user.id).first_or_404()
        notif.mensagem = dados.get("mensagem", notif.mensagem)
        notif.tipo = dados.get("tipo", notif.tipo)
        notif.descricao = dados.get("descricao", notif.descricao)
        notif.data = datetime.strptime(dados.get("data"), "%Y-%m-%d").date()
        db.session.commit()
        return jsonify({"status": "ok"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": str(e)}), 500
