from models.db import db
from datetime import datetime

class Parcelamento(db.Model):
    __tablename__ = 'parcelamentos'

    id = db.Column(db.Integer, primary_key=True)
    
    empresa_id = db.Column(db.Integer, nullable=False)  # Opcional se quiser controlar a empresa do cliente
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    
    tributo = db.Column(db.String(100), nullable=False)
    parcelas = db.Column(db.Integer, nullable=False)
    valor_parcela = db.Column(db.Numeric(12,2), nullable=False)
    valor_total = db.Column(db.Numeric(12,2), nullable=False)
    
    data_inicio = db.Column(db.Date, default=datetime.utcnow)
    status_parcelamento = db.Column(db.String(50), default='Ativo')  # Ex: Ativo, Quitado, Rescindido
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamento ORM
    cliente = db.relationship('Cliente', backref=db.backref('parcelamentos', lazy=True))

    def __repr__(self):
        return f"<Parcelamento {self.id} - {self.tributo} - Cliente {self.cliente_id}>"
