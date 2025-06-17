from models.db import db
from datetime import datetime

class Processo(db.Model):
    __tablename__ = 'processos'

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), nullable=False)
    empresa = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    valor = db.Column(db.Float, default=0.0)
    prazos = db.Column(db.Text)
    garantia = db.Column(db.String(100))
    vara = db.Column(db.String(100))
    responsavel = db.Column(db.String(100))
    esfera = db.Column(db.String(20))  # Exemplo: 'federal', 'estadual', 'municipal'

    tipo_processo = db.Column(db.String(50))  # Exemplo: Execução Fiscal, Embargos
    risco_classificacao = db.Column(db.String(20))  # Exemplo: Baixo, Médio, Alto, Crítico

    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    cliente = db.relationship('Cliente', backref=db.backref('processos', lazy=True))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Processo {self.numero} - {self.status}>"
