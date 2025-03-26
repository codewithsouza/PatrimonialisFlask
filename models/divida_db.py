from models.db import db


class Divida(db.Model):
    __tablename__ = 'dividas'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    valor_pago = db.Column(db.Float, nullable=False)
    observacoes = db.Column(db.String(255))
    
    # Relacionamento com Cliente
    cliente = db.relationship('Cliente', backref='dividas', lazy=True)
    
    # Relacionamento com Usuario
    usuario_id = db.Column(db.Integer, db.ForeignKey('cadastro.id'), nullable=False)  # Relacionamento com o modelo 'Usuario'
    usuario = db.relationship('Usuario', backref='dividas', lazy=True)
