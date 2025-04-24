from models.db import db

class Cliente(db.Model):
    __tablename__ = 'clientes'  # ou o nome que você estiver usando

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cnpj = db.Column(db.String(20), nullable=False, unique=False)
    regime = db.Column(db.String(50))
    divida = db.Column(db.Float)
    contrato = db.Column(db.String(100))
    segmento = db.Column(db.String(100))
    logradouro = db.Column(db.String(100))
    numero = db.Column(db.String(20))
    bairro = db.Column(db.String(100))
    municipio = db.Column(db.String(100))
    email = db.Column(db.String(100))
    telefone = db.Column(db.String(20))
    cep = db.Column(db.String(20))
    monitoramento = db.Column(db.Boolean, default=False)
    data_monitoramento = db.Column(db.Date)
    situacao_fiscal = db.Column(db.String(200))
    observacoes = db.Column(db.Text)

    # FK e relacionamento com Usuario
    usuario_id = db.Column(db.Integer, db.ForeignKey('cadastro.id'), nullable=False)
    usuario = db.relationship('Usuario', backref=db.backref('clientes', lazy=True))



