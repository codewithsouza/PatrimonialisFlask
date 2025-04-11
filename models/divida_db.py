from models.db import db
from sqlalchemy.orm import relationship
from datetime import datetime

class Divida(db.Model):
    __tablename__ = 'dividas'

    id = db.Column(db.Integer, primary_key=True)
    valor_pago = db.Column(db.Float, default=0.0)
    data_pagamento = db.Column(db.Date, default=datetime.utcnow)
    
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('cadastro.id'), nullable=False)

    cliente = relationship("Cliente", backref="dividas")

    def __repr__(self):
        return f"<Divida Cliente {self.cliente_id} - Valor Pago: {self.valor_pago}>"
