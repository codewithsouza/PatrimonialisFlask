from models.db import db
from models.usuario import Usuario
from models.clientes_db import Cliente
from models.divida_db import Divida

class Negociacao(db.Model):
    __tablename__ = 'negociacoes'  # Nome da tabela no banco de dados

    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(100), nullable=False)  # Descrição da negociação
    status = db.Column(db.String(50), default='Pendente')  # Status da negociação: 'Pendente' ou 'Finalizada'

    # Relacionamento com o usuário
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)  # Chave estrangeira para o usuário
    usuario = db.relationship('Usuario', backref=db.backref('negociacoes', lazy=True))  # Relacionamento de volta com o usuário

    # Outros campos necessários
    valor_negociado = db.Column(db.Float)  # Valor negociado
    tipo = db.Column(db.String(50))  # Tipo da negociação (Ex: Venda, Compra)
    parcelas = db.Column(db.Integer)  # Número de parcelas
    data_negociacao = db.Column(db.DateTime, default=db.func.current_timestamp())  # Data da negociação

    # Relacionamento com a tabela Divida
    divida_id = db.Column(db.Integer, db.ForeignKey('dividas.id'))  # Chave estrangeira para a tabela Dividas
    divida = db.relationship('Divida', backref=db.backref('negociacoes', lazy=True))  # Relacionamento com a dívida
    
    # Relacionamento com a tabela Cliente
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))  # Chave estrangeira para a tabela Clientes
    cliente = db.relationship('Cliente', backref=db.backref('negociacoes', lazy=True))  # Relacionamento com o cliente

    def __repr__(self):
        return f'<Negociacao {self.id}, {self.descricao}, {self.status}>'
