from models.db import db
from datetime import date

class Notificacao(db.Model):
    __tablename__ = 'notificacoes'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('cadastro.id'), nullable=False)

    data = db.Column(db.Date, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    mensagem = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.Text)
    titulo = db.Column(db.String(255))

    def to_dict(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "data": self.data.strftime("%Y-%m-%d"),
            "tipo": self.tipo,
            "mensagem": self.mensagem,
            "descricao": self.descricao or "",
            "titulo": self.titulo or ""
        }

    def __repr__(self):
        return f"<Notificacao {self.tipo} - {self.mensagem}>"
