from models import User, RedFlagRecord, InterventionRecord, AdminAction,db
from config import app ,db, api
from flask import Flask,jsonify,request,make_response
from flask_restful import Resource 
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import random
import smtplib
from enum import Enum
import cloudinary
# Import the cloudinary.api for managing assets
import cloudinary.api
# Import the cloudinary.uploader for uploading assets
import cloudinary.uploader

cloudinary.config(
    cloud_name="doyuruatj",
    api_key="448636314545994",
    api_secret="nmNAYoDpIsreAAJtXm6Ktem6Qlo",
    secure=True,
)

signup_otp={}


class Login(Resource):
    def post(self):
        username=request.json.get("username")
        password=request.json.get("password")

        user=User.query.filter_by(username=username).first()
        if not user:
            return {"message":"user not found"}, 404
        if not user.authenticate(password):
            return {"message":"Invalid password"}, 401
        # access_token=create_access_token(identity=user.id, additional_claims={"role": user.role.value})

        access_token=create_access_token(identity=user.id)
        return {"access_token":access_token}
    
class Signup(Resource):
    def post(self):
        username=request.json.get("username")
        password=request.json.get("password")
        email=request.json.get("email")

        existing_user=User.query.filter_by(username=username).first()

        if existing_user:
            return {"message":"Username already exists"}
        
        existing_email=User.query.filter_by(email=email).first()

        if existing_email:
            return {"message":"Email already exists"} 
        
        otp=''.join([str(random.randint(0,9))for _ in range (6)])
        signup_otp[email]=otp
        send_otp(email,otp)
        return {"email":email,"message":f"otp sent to your email - {email}"}
def send_otp(email,otp):
    smtp_server = 'smtp.gmail.com'        
    smtp_port = 587
    sender_email = 'bbeatricemwangi@gmail.com'
    sender_password = 'dryq iymj frgs okky'
    subject= 'otp verification'
    body = f"Otp verification for your email is {otp} "
    message = f"subject: {subject}\n\n{body}"
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, message) 

def verify_otp(stored_otp, otp_user):
    return stored_otp==otp_user

class Verify(Resource):
    def post(self):
        email = request.json.get("email") 
        otp_user = request.json.get("otp")
        stored_otp =signup_otp.get(email)

        if stored_otp and verify_otp(stored_otp, otp_user):
            username=request.json.get("username")
            password=request.json.get("password")
            new_user = User(username=username,email=email)
            new_user.password_hash=password
            db.session.add(new_user)
            db.session.commit()

            access_token=create_access_token(identity=new_user.id)
            return {"token":access_token,"message":"User registered successfully" },201
        else:
            return {"error":"401 unauthorised " , "message":"Invalid otp"},401
class checksession(Resource):
    @jwt_required()
    def get(self):
        current_user_id=get_jwt_identity()
        user = User.query.filter_by(id=current_user_id).first()
        if not user:
            return {"error":"user does not exist"},404  
        user_data = {
            "id":user.id,
            "email":user.email,
            "username":user.username

        }
        return make_response(jsonify(user_data),200)

class UserResource(Resource):
    @jwt_required()
    def get(self):
        current_user_id=get_jwt_identity()
        user = User.query.filter_by(id=current_user_id).first()
        if not user:
            return {"error":"user does not exist"},404
        user_data = {
            "id":user.id,
            "email":user.email,
            "username":user.username

        }
        return make_response(jsonify(user_data),200) 

 

api.add_resource(Login,'/login')
api.add_resource(Signup,'/signup')
api.add_resource(Verify,'/verify')       
api.add_resource(UserResource,'/user') 
api.add_resource(checksession,'/checksession')


class RedFlagRecords(Resource):
    def get(self):
        redflag_records=RedFlagRecord.query.all()
        redflag_records_dict=[redflag_record.serialize() for redflag_record in redflag_records ]
        return jsonify(redflag_records_dict)
api.add_resource(RedFlagRecords, '/redflagrecords')
class RedFlagRecordsById(Resource):
    def get(self,id):
        redflag_record=RedFlagRecord.query.get(id)
        if not redflag_record:
            return {'error':'redflag_record not found'}, 404
        return jsonify(redflag_record.serialize())
    
    def patch(self,id):
        data=request.get_json()
        description = data['description']
        latitude = data['latitude']
        longitude = data['longitude']
        redflag_record = RedFlagRecord.query.get(id)
        if not redflag_record:
            return {'error': 'redflag record not found'}, 404
        else:
           redflag_record.description = description
           redflag_record.latitude = latitude
           redflag_record.longitude = longitude
           db.session.commit()

           response = make_response(jsonify(redflag_record.serialize()), 200)
           return response
     
    def delete(self,id):
        redflag_record = RedFlagRecord.query.get(id)
        if not redflag_record:
            return {'error': 'redflag record not found'}, 404

        db.session.delete(redflag_record)
        db.session.commit()

        response = make_response(jsonify({"message": "redflagrecord record deleted successfully"}), 200)
        return response
    def post(self,id):
        data = request.form
        description = data.get('description')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        images = request.files.get('images')
        videos = data.get('videos') 

        if not description or not latitude or not longitude:
            return {'message': 'Description, latitude, and longitude are required fields'}, 400

        # Check if file uploaded and is an image
        if images.filename == '':
            return {'message': 'No image selected for upload'}, 400
        if not allowed_file(images.filename):
            return {'message': 'Invalid file type. Only images are allowed'}, 400

        # Upload image to Cloudinary
        try:
            image_upload_result = cloudinary.uploader.upload(images)
        except Exception as e:
            return {'message': f'Error uploading image: {str(e)}'}, 500


        new_data = RedFlagRecord(
            users_id=id,
            description=description,
            latitude=latitude,
            longitude=longitude,
            images=image_upload_result['secure_url'],
            videos=videos
        )
    
        db.session.add(new_data)
        db.session.commit()
        response=make_response (jsonify(new_data.serialize()), 201)
        return response
    

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

api.add_resource(RedFlagRecordsById,'/redflagrecords/<int:id>')

class InterventionRecords(Resource):
    def get(self):
        intervention_records=InterventionRecord.query.all()
        intervention_record_dict=[intervention_record.serialize() for intervention_record in intervention_records]
        return jsonify(intervention_record_dict)
api.add_resource(InterventionRecords, '/interventionrecords')


class InterventionRecordsById(Resource):
    def get(self, id):
        intervention_record = InterventionRecord.query.get(id)
        if not intervention_record:
            return {'error': 'intervention_record not found'}, 404
        return jsonify(intervention_record.serialize())

    def post(self,id):
        data = request.json
        description = data.get('description')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        images = data.get('images')
        videos = data.get('videos') 

        if not description or not latitude or not longitude:
            return {'message': 'Description, latitude, and longitude are required fields'}, 400

       

        new_data = InterventionRecord(
            users_id=id,
            description=description,
            latitude=latitude,
            longitude=longitude,
            images=images,
            videos=videos
        )
    
        db.session.add(new_data)
        db.session.commit()
        response=make_response (jsonify(new_data.serialize()), 201)
        return response
    
    def patch(self,id):
        data = request.get_json()
        description = data['description']
        latitude = data['latitude']
        longitude = data['longitude']
        intervention_record = InterventionRecord.query.get(id)
        if not intervention_record:
            return {'error': 'Intervention record not found'}, 404
        else:
           intervention_record.description = description
           intervention_record.latitude = latitude
           intervention_record.longitude = longitude
           db.session.commit()

           response = make_response(jsonify(intervention_record.serialize()), 200)
           return response
        
    def delete(self,id):

        intervention_record = InterventionRecord.query.get(id)
        if not intervention_record:
            return {'error': 'Intervention record not found'}, 404

        db.session.delete(intervention_record)
        db.session.commit()

        response = make_response(jsonify({"message": "Intervention record deleted successfully"}), 200)
        return response


api.add_resource(InterventionRecordsById, '/interventionrecords/<int>')
class AdminActions(Resource):
    def get(self):
        admins=AdminAction.query.all()
        admin_dict=[admin.serialize() for admin in admins]
        return jsonify(admin_dict)
api.add_resource(AdminActions, '/adminactions') 

class AdminActionById(Resource):
    def get(self,id):
        admin=AdminAction.query.get(id)
        if not admin:
           return {'error':'admin not found'}, 404
        return jsonify(admin.serialize())
    @jwt_required
    def post(self,id):
        data = request.get_json()
        # redflagrecords_id = data.get('redflagrecords_id')
        # interventionrecords_id = data.get('interventionrecords_id')
        action_type = data.get('action_type')
        comments = data.get('comments')
    
        if not action_type or not comments:
            return {'error': 'the action_type, and comments are required fields'}, 400
        
        new_data = AdminAction(
            redflagrecords_id= id,
            interventionrecords_id=id,
            action_type=action_type,
            comments=comments
    )
    
        db.session.add(new_data)
        db.session.commit() 
    
        response = make_response(jsonify(new_data.serialize()), 201)
        return response
    def patch(self,id):
        data=request.get_json()
        action_type = data.get('action_type')
        comments = data.get('comments')
        admin=AdminAction.query.get(id)

        if not action_type or not comments:
            return {'error': 'the action_type, and comments are required fields'}, 400
        else:
            admin.action_type=action_type
            admin.comments=comments
            db.session.commit()
            response=make_response (jsonify(admin.serialize()), 200)
            return response
    
    def delete(self,id):
        admin=AdminAction.query.get(id)
        if not admin:
            return {'error':'admin not found'}, 400
        db.session.delete(admin)
        db.session.commit()
        response=make_response(jsonify({'message':'admin record deleted successfully'}), 200)
        return response



api.add_resource(AdminActionById, '/adminactions/<int:id>')







if __name__ == "__main__":
    app.run(port=5555, debug=True)
