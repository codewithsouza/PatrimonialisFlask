from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from models.db import db

class Usuario(UserMixin, db.Model):
    __tablename__ = 'cadastro'  # nome da tabela no banco

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)
