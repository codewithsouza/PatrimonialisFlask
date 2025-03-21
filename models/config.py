# Configurações do banco de dados e JWT
class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://usuario:senha@host:3306/nome_do_banco"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "chave_super_segura"
