from models.db import db
from flask_login import UserMixin
from datetime import date

class Notificacao(db.Model):
    __tablename__ = 'notificacoes'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # Lembrete, Alerta, Reunião
    mensagem = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "data": self.data.strftime("%Y-%m-%d"),
            "tipo": self.tipo,
            "mensagem": self.mensagem
        }
