from models.db import db

class Cliente(db.Model):
    __tablename__ = "cliente"
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cnpj = db.Column(db.String(18), nullable=False)
    regime = db.Column(db.String(50), nullable=False)
    divida = db.Column(db.Float, nullable=False)
    contrato = db.Column(db.String(100), nullable=False)
    segmento = db.Column(db.String(100), nullable=False)
    
    def __init__(self, nome, cnpj, regime, divida, contrato, segmento):
        self.nome = nome
        self.cnpj = cnpj
        self.regime = regime
        self.divida = divida
        self.contrato = contrato
        self.segmento = segmento
