# config.py
import os
from dotenv import load_dotenv

# Carrega variáveis do .env (caso ainda não esteja carregado)
load_dotenv()

class Config:
    # 🔐 Segurança
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "lv4Jk0WyEUT2_L52ku1s0ExOg1HEXyjW3Rvsc_noaLM4")

    # 🔗 Banco de Dados
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "FLASK_DATABASE_URL",
        "mysql+pymysql://uaico420_est1114:ghstdrk1566@192.185.211.123:3306/uaico420_est1114"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 🔒 Segurança extra de cookies
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # Coloque True se usar HTTPS (produção)

    # 🔧 Debug controlado por variável
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    SESSION_COOKIE_SECURE = True  # só com HTTPS
    WTF_CSRF_ENABLED = True       # se for usar Flask-WTF futuramente
