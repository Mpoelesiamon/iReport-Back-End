from flask import Flask 
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_restful import Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import  timedelta
from flask_jwt_extended import  JWTManager

db = SQLAlchemy()
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///ireporter.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config["JWT_SECRET_KEY"] = "please-remember-to-change-me"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)

migrate=Migrate(app,db)
db.init_app(app)
CORS(app)
bcrypt=Bcrypt(app)
api = Api(app)

















