from flask_sqlalchemy import SQLAlchemy
from .db import db
from .divida_db import *
from .notificacoes_db import *
from .cliente_db import *

db = SQLAlchemy()