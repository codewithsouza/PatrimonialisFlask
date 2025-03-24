import os

class Config:
    # Banco de dados: usa variável de ambiente ou valor padrão
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "FLASK_DATABASE_URL",
        "mysql+pymysql://uaico420_est1114:ghstdrk1566@192.185.211.123:3306/uaico420_est1114"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Chave secreta: segura e aleatória
    SECRET_KEY = os.getenv(
        "FLASK_SECRET_KEY",
        "lv4Jk0WyEUT2_L52ku1s0ExOg1HEXyjW3Rvsc_noaLM4"
    )
