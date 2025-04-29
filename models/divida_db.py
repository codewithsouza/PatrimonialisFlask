from models.db import db
from sqlalchemy.orm import relationship
from datetime import datetime, date

class Divida(db.Model):
    __tablename__ = 'dividas'

    id = db.Column(db.Integer, primary_key=True)
    
    # Informações financeiras
    valor_principal = db.Column(db.Numeric(12, 2), default=0)
    multa = db.Column(db.Numeric(12, 2), default=0)
    juros = db.Column(db.Numeric(12, 2), default=0)
    valor_pago = db.Column(db.Numeric(12, 2), default=0)
    valor_total = db.Column(db.Numeric(12, 2), default=0)  # Valor da dívida calculado (pode preencher no momento do cadastro)

    # Datas importantes
    data_apuracao = db.Column(db.Date)  # Quando foi gerada
    data_vencimento = db.Column(db.Date)  # Quando vence
    data_pagamento = db.Column(db.Date, default=date.today)  # Quando foi paga (se foi)

    # Identificações
    esfera = db.Column(db.String(20))  # 'Federal', 'Estadual', 'Municipal'
    tributo = db.Column(db.String(100))  # IRPJ, ICMS, ISS, etc.
    origem = db.Column(db.String(100))  # Ex: Auto de infração, confissão de dívida etc.
    numero_processo = db.Column(db.String(100))  # Número do processo administrativo (se tiver)

    # Status
    status = db.Column(db.String(50))  # Ex: Ativo, Parcelado, Suspenso, Baixado

    # Observações gerais
    observacoes = db.Column(db.Text)

    # Controle de relacionamento
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('cadastro.id'), nullable=False)

    # Relacionamentos ORM
    cliente = relationship("Cliente", backref="dividas")
    usuario = relationship("Usuario", backref="dividas")

    # Controle de atualização
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Divida {self.id} - {self.esfera} - {self.tributo} - Cliente {self.cliente_id}>"
