from models import User, RedFlagRecord, InterventionRecord, AdminAction,db
from flask_migrate import Migrate
from flask import Flask,jsonify,request,make_response
from flask_restful import Api,Resource 
from flask_cors import CORS
from datetime import datetime

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ireporter.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
CORS(app)
migrate=Migrate(app,db)
db.init_app(app)
api=Api(app)


if __name__=="__main__":
    app.run(port=5555,debug=True)