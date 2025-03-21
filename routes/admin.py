from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file, Response, jsonify
import pandas as pd
import io
import os
from models.db import db  
from models.clientes_db import Cliente  

bp_admin = Blueprint('admin', __name__, url_prefix='/admin')

# 📌 Página principal
@bp_admin.route('/')
def index():
    if 'usuario' not in session:
        flash("Você precisa fazer login primeiro!", "warning")
        return redirect(url_for('admin.login_admin'))
    
    total = Cliente.query.count()
    return render_template('admin/index.html', total_clientes=total)

# 🔑 Login do admin
@bp_admin.route('/login', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('password')

        if email == "admin@email.com" and senha == "1234":
            session['usuario'] = email
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for('admin.index'))
        else:
            flash("Credenciais inválidas!", "danger")

    return render_template('admin/login_admin.html')

# 🚪 Logout
@bp_admin.route('/logout')
def logout_admin():
    session.pop('usuario', None)
    flash("Logout realizado com sucesso!", "info")
    return redirect(url_for('admin.login_admin'))

# 📄 Lista de clientes cadastrados
@bp_admin.route('/clientes_cadastrados')
def clientes_cadastrados():
    if 'usuario' not in session:
        flash("Você precisa fazer login primeiro!", "warning")
        return redirect(url_for('admin.login_admin'))

    clientes = Cliente.query.all()
    return render_template('admin/clientes_cadastrados.html', clientes=clientes)

# ➕ Adicionar cliente no banco
@bp_admin.route('/adicionar_cliente', methods=['POST'])
def adicionar_cliente():
    data = request.get_json()  # Lê o corpo como JSON

    nome = data.get('nome')
    cnpj = data.get('cnpj')
    regime = data.get('regime')
    divida = float(data.get('divida', 0))
    contrato = data.get('contrato')
    segmento = data.get('segmento', '')

    # 🔹 Agora 'nome', 'cnpj' etc. virão do JSON enviado pelo fetch
    if not nome or not cnpj:
        return jsonify({"message": "Nome e CNPJ são obrigatórios!"}), 400

    cliente_existente = Cliente.query.filter_by(cnpj=cnpj).first()
    if cliente_existente:
        return jsonify({"message": "Erro: Já existe um cliente com esse CNPJ!"}), 400

    novo_cliente = Cliente(
        nome=nome,
        cnpj=cnpj,
        regime=regime,
        divida=divida,
        contrato=contrato,
        segmento=segmento
    )

    try:
        db.session.add(novo_cliente)
        db.session.commit()
        return jsonify({"message": "Cliente cadastrado com sucesso!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erro ao cadastrar cliente: {str(e)}"}), 500

# ❌ Excluir Cliente
@bp_admin.route('/excluir_cliente/<int:id>', methods=['POST'])
def excluir_cliente(id):
    cliente = Cliente.query.get(id)
    if cliente:
        db.session.delete(cliente)
        db.session.commit()
        flash("Cliente excluído com sucesso!", "success")
    else:
        flash("Erro: Cliente não encontrado!", "danger")

    return redirect(url_for('admin.clientes_cadastrados'))

# 📤 Exportar clientes para CSV
@bp_admin.route('/exportar')
def exportar():
    clientes = Cliente.query.all()
    if not clientes:
        flash("Nenhum cliente para exportar!", "danger")
        return redirect(url_for('admin.clientes_cadastrados'))

    df = pd.DataFrame([{
        "ID": c.id,
        "Nome": c.nome,
        "CNPJ": c.cnpj,
        "Regime": c.regime,
        "Dívida": c.divida,
        "Contrato": c.contrato,
        "Segmento": c.segmento
    } for c in clientes])

    os.makedirs("static", exist_ok=True)
    file_path = os.path.join("static", "clientes_export.csv")
    df.to_csv(file_path, index=False)

    flash("Clientes exportados com sucesso!", "success")
    return send_file(file_path, as_attachment=True)

# 📥 Importar clientes de CSV/Excel
@bp_admin.route('/importar', methods=['POST'])
def importar():
    file = request.files.get('file')

    if not file:
        flash("Nenhum arquivo foi enviado!", "danger")
        return redirect(url_for('admin.clientes_cadastrados'))

    # Lógica para ler CSV/Excel...
    # Exemplo rápido:
    # df = pd.read_excel(file) if file.filename.endswith('.xlsx') else pd.read_csv(file)
    # ...
    # db.session.add(...)
    # db.session.commit()

    flash("Importação realizada com sucesso!", "success")
    return redirect(url_for('admin.clientes_cadastrados'))