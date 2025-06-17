from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from models.db import db
from models.divida_db import Divida
from models.clientes_db import Cliente

bp_dividas = Blueprint('dividas', __name__, url_prefix='/dividas')

@bp_dividas.route('/federal')
@login_required
def divida_federal():
    dividas = Divida.query.filter_by(usuario_id=current_user.id, esfera='Federal').all()
    return render_template('admin/divida_federal.html', dividas=dividas)

@bp_dividas.route('/estadual')
@login_required
def divida_estadual():
    dividas = Divida.query.filter_by(usuario_id=current_user.id, esfera='Estadual').all()
    return render_template('admin/divida_estadual.html', dividas=dividas)

@bp_dividas.route('/municipal')
@login_required
def divida_municipal():
    dividas = Divida.query.filter_by(usuario_id=current_user.id, esfera='Municipal').all()
    return render_template('admin/divida_municipal.html', dividas=dividas)
