from datetime import datetime
from models.db import db

class Evento(db.Model):
    __tablename__ = 'eventos'

    id = db.Column(db.Integer, primary_key=True)
    mensagem = db.Column(db.String(150), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    data_evento = db.Column(db.Date, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('cadastro.id'), nullable=False)



    def __repr__(self):
        return f"<Evento {self.titulo} ({self.tipo}) em {self.data_evento}>"
