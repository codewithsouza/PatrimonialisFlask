from flask import Blueprint, render_template, request, redirect, url_for, send_file, flash, session
import pandas as pd
import os

bp_admin = Blueprint('admin', __name__, url_prefix='/admin')

# ✅ Lista de clientes simulada
clientes = [
    {"id": 1, "nome": "Empresa X", "cnpj": "00.000.000/0001-00", "regime": "Simples Nacional", "divida": "R$ 5.000", "cobranca": "Pendente"},
    {"id": 2, "nome": "Empresa Y", "cnpj": "11.111.111/0001-11", "regime": "Lucro Presumido", "divida": "R$ 12.500", "cobranca": "Pago"},
]

# ✅ Página de Login do Admin
@bp_admin.route('/login', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('password')

        # Simulação de login válido (Substitua por verificação real no banco de dados)
        if email == "admin@email.com" and senha == "admin123":
            session['usuario'] = email  # Salva usuário na sessão
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for('admin.index'))  # 🔹 Agora redireciona para index corretamente
        else:
            flash("Credenciais inválidas!", "danger")

    return render_template('admin/login_admin.html')

# ✅ Página Inicial do Admin (Dashboard)
@bp_admin.route('/')
def index():
    if 'usuario' not in session:  # 🔹 Bloqueia acesso sem login
        flash("Você precisa fazer login primeiro!", "warning")
        return redirect(url_for('admin.login_admin'))

    return render_template('admin/index.html')

# ✅ Logout do Admin
@bp_admin.route('/logout')
def logout_admin():
    session.pop('usuario', None)  # Remove usuário da sessão
    flash("Logout realizado com sucesso!", "info")
    return redirect(url_for('admin.login_admin'))

# ✅ Página de Clientes Cadastrados
@bp_admin.route('/clientes_cadastrados')
def clientes_cadastrados():
    if 'usuario' not in session:  # 🔹 Protege a rota contra acesso não autorizado
        flash("Você precisa fazer login primeiro!", "warning")
        return redirect(url_for('admin.login_admin'))

    return render_template('admin/clientes_cadastrados.html', clientes=clientes)

# ✅ Rota para importar CSV/Excel
@bp_admin.route('/importar', methods=['POST'])
def importar():
    file = request.files.get('file')
    
    if not file:
        flash("Nenhum arquivo foi enviado!", "danger")
        return redirect(url_for('admin.clientes_cadastrados'))

    if not (file.filename.endswith('.xlsx') or file.filename.endswith('.csv')):
        flash("Arquivo inválido! Apenas CSV ou Excel são permitidos.", "danger")
        return redirect(url_for('admin.clientes_cadastrados'))

    try:
        df = pd.read_excel(file) if file.filename.endswith('.xlsx') else pd.read_csv(file)

        # ✅ Converte as colunas para string para evitar erro com valores numéricos
        df = df.astype(str)

        required_columns = {"Nome", "CNPJ", "Regime", "Dívida", "Cobrança"}
        if not required_columns.issubset(df.columns):
            flash("Erro: O arquivo não contém todas as colunas necessárias!", "danger")
            return redirect(url_for('admin.clientes_cadastrados'))

        for _, row in df.iterrows():
            clientes.append({
                "id": len(clientes) + 1,
                "nome": row['Nome'],
                "cnpj": row['CNPJ'],
                "regime": row['Regime'],
                "divida": row['Dívida'],
                "cobranca": row['Cobrança']
            })

        flash("Clientes importados com sucesso!", "success")
    except Exception as e:
        flash(f"Erro ao processar o arquivo: {str(e)}", "danger")

    return redirect(url_for('admin.clientes_cadastrados'))

# ✅ Rota para exportar clientes em CSV
@bp_admin.route('/exportar')
def exportar():
    if not clientes:
        flash("Nenhum cliente para exportar!", "danger")
        return redirect(url_for('admin.clientes_cadastrados'))

    df = pd.DataFrame(clientes)

    os.makedirs("static", exist_ok=True)

    file_path = os.path.join("static", "clientes_export.csv")
    df.to_csv(file_path, index=False)

    flash("Clientes exportados com sucesso!", "success")
    return send_file(file_path, as_attachment=True)
