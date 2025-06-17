from app import create_app
from models.db import db
from models.usuario import Usuario
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Adiciona a coluna is_admin se ela não existir
    try:
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE cadastro ADD COLUMN is_admin BOOLEAN DEFAULT FALSE'))
            conn.commit()
        print("Coluna is_admin adicionada com sucesso!")
    except Exception as e:
        print(f"Erro ao adicionar coluna: {str(e)}")
        print("A coluna pode já existir ou houve outro erro.")

    # Atualiza usuários existentes para serem admin
    try:
        with db.engine.connect() as conn:
            conn.execute(text('UPDATE cadastro SET is_admin = TRUE'))
            conn.commit()
        print("Usuários atualizados para admin com sucesso!")
    except Exception as e:
        print(f"Erro ao atualizar usuários: {str(e)}")
        db.session.rollback() 