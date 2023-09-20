from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_cors import CORS, cross_origin
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename


from config import DevEnvConfig

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_object(DevEnvConfig)
db = SQLAlchemy(app)


cors = CORS(support_credentials=True)
cors.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

jwt = JWTManager()
jwt.init_app(app)



# csrf = CSRFProtect(app)

def create_db():
    with app.app_context():
        db.create_all()

from views.admin import *
from views.application import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
