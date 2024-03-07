from models import User, RedFlagRecord, InterventionRecord, AdminAction,db
from config import app ,db, api
from flask import Flask,jsonify,request,make_response
from flask_restful import Resource 
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity





class Login(Resource):
    def post(self):
        username=request.json.get("username")
        password=request.json.get("password")

        user=User.query.filter_by(username=username).first()
        if not user:
            return {"message":"user not found"}
        if not user.authenticate(password):
            return {"message":"Invalid password"}
        access_token=create_access_token(identity=user.id)
        return {"access_token":access_token}

api.add_resource(Login,'/login')
        



if __name__=="__main__":
    app.run(port=5555,debug=True)