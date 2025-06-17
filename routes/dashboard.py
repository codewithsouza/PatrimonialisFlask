# Rotas do dashboard e integração com Power BI

from flask import Blueprint, render_template

bp_admin = Blueprint('admin', __name__, url_prefix='/admin')

@bp_admin.route('/dashboard')
def dashboard():
    return render_template('admin/dashboard.html')
