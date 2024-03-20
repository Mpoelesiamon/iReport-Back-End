from models import User, RedFlagRecord, InterventionRecord, AdminAction,db
from config import app ,db, api
from flask import Flask,jsonify,request,make_response
from flask_restful import Resource 
# from flask_login import UserMixin
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
        current_user_id = get_jwt_identity()
        user = User.query.filter_by(id=current_user_id).first()
        if not user:
            return {"error": "User does not exist"}, 404
        
        user_data = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role  # Include the 'role' field in the response
        }
        
        return make_response(jsonify(user_data), 200)
 

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
    
api.add_resource(RedFlagRecords,'/redflagrecords')   
class RedFlagRecordsById(Resource):
    def get(self,id):
        redflag_record=RedFlagRecord.query.get(id)
        if not redflag_record:
            return {'error':'redflag_record not found'}, 404
        return jsonify(redflag_record.serialize())
    
    def patch(self,id):
        data=request.get_json()
        description = data['description']
        redflag_record = RedFlagRecord.query.get(id)
        if not redflag_record:
            return {'error': 'redflag record not found'}, 404
        else:
           redflag_record.description = description
           db.session.commit()

           response = make_response(jsonify(redflag_record.serialize()), 200)
           return response
     
    def delete(self, id):
        redflag_record = RedFlagRecord.query.get(id)
        if not redflag_record:
                return {'error': 'RedFlagRecord not found'}, 404

    # Delete associated AdminAction records
        admin_actions = AdminAction.query.filter_by(redflagrecords_id=id).all()
        for admin_action in admin_actions:
            db.session.delete(admin_action)

        db.session.delete(redflag_record)
        db.session.commit()

        response = make_response(jsonify({"message": "RedFlagRecord deleted successfully"}), 200)
        return response
api.add_resource(RedFlagRecordsById,'/redflagrecords/<int:id>')   

class RedFlags(Resource):
    @jwt_required()
    def post(self):
        try:
            current_user_id = get_jwt_identity()

            data = request.form
            description = data.get('description')
            images = request.files.get('image')
            videos = request.files.get('videos')

            if not all([description, images, videos]):
                return {'message': 'Description, images, and videos are required fields'}, 400

            # Check file extensions
            allowed_image_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            allowed_video_extensions = {'mp4'}

            if not allowed_file(images.filename, allowed_image_extensions):
                return {'message': 'Invalid image file type. Only png, jpg, jpeg, gif are allowed'}, 400
            if not allowed_file(videos.filename, allowed_video_extensions):
                return {'message': 'Invalid video file type. Only mp4 is allowed'}, 400

            # Upload images and videos to Cloudinary
            image_upload_result = cloudinary.uploader.upload(images, resource_type="image")
            video_upload_result = cloudinary.uploader.upload(videos, resource_type="video")

            # Save data to database
            new_data = RedFlagRecord(
                users_id=current_user_id,
                description=description,
                images=image_upload_result['secure_url'],
                videos=video_upload_result['secure_url']
            )
            db.session.add(new_data)
            db.session.commit()

            return {"message": "Red flag data posted successfully"}, 201
            # return []
        except Exception as e:
            
            return {'message': f'An error occurred: {str(e)}'}, 500

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

api.add_resource(RedFlags, "/redflags")


                      
# api.add_resource(RedFlagRecordsById,'/redflagrecords/<int:id>')

class InterventionRecords(Resource):
    def get(self):
        intervention_records=InterventionRecord.query.all()
        intervention_record_dict=[intervention_record.serialize() for intervention_record in intervention_records]
        return jsonify(intervention_record_dict)
api.add_resource(InterventionRecords, '/interventionrecords')


class Interventions(Resource):
    @jwt_required()
    def post(self):
        try:
            current_user_id = get_jwt_identity()

            data = request.form
            description = data.get('description')
            images = request.files.get('image')
            videos = request.files.get('videos')

            app.logger.info(f"Received request with description: {description}, images: {images}, videos: {videos}")

            if not all([description, images, videos]):
                return {'message': 'Description, images, and videos are required fields'}, 400

            # Check file extensions
            allowed_image_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            allowed_video_extensions = {'mp4'}

            if not allowed_file(images.filename, allowed_image_extensions):
                return {'message': 'Invalid image file type. Only png, jpg, jpeg, gif are allowed'}, 400
            if not allowed_file(videos.filename, allowed_video_extensions):
                return {'message': 'Invalid video file type. Only mp4 is allowed'}, 400

            # Upload images and videos to Cloudinary
            image_upload_result = cloudinary.uploader.upload(images, resource_type="image")
            video_upload_result = cloudinary.uploader.upload(videos, resource_type="video")

            # Save data to database
            new_data = InterventionRecord(
                users_id=current_user_id,
                description=description,
                images=image_upload_result['secure_url'],
                videos=video_upload_result['secure_url']
            )
            db.session.add(new_data)
            db.session.commit()

            return {"message": "Intervention data posted successfully"}, 201
        except Exception as e:
            # Log the full traceback for debugging purposes
            app.logger.error(f"An error occurred: {e}", exc_info=True)
            return {'message': 'An error occurred while processing your request'}, 500

    def allowed_file(filename, allowed_extensions):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions





api.add_resource(Interventions, "/interventions")




class InterventionRecordsById(Resource):
    def get(self, id):
        intervention_record = InterventionRecord.query.get(id)
        if not intervention_record:
            return {'error': 'intervention_record not found'}, 404
        return jsonify(intervention_record.serialize())

    def patch(self,id):
        data=request.get_json()
        description=data['description']
        intervention_record=InterventionRecord.query.get(id)
        if not intervention_record:
            return {'error':'intervention_record not found'},404
        else:
            intervention_record.description=description
            db.session.commit()

        response = make_response(jsonify(intervention_record.serialize()), 200)
        return response

        
    def delete(self, id):
        intervention_record = InterventionRecord.query.get(id)
        if not intervention_record:
                return {'error': 'InterventionRecord not found'}, 404

    # Delete associated AdminAction records
        admin_actions = AdminAction.query.filter_by(interventionrecords_id=id).all()
        for admin_action in admin_actions:
            db.session.delete(admin_action)

        db.session.delete(intervention_record)
        db.session.commit()

        response = make_response(jsonify({"message": "InterventionRecord deleted successfully"}), 200)
        return response



api.add_resource(InterventionRecordsById, '/interventionrecords/<int:id>')
class AdminActions(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        user = User.query.filter_by(id=current_user_id).first()
        
        if not user or user.role != 'admin':
            return {"message":"Unauthorised access"}
            # abort(403, message="Unauthorized access")  # Return forbidden error if user is not an admin
        
        admins = AdminAction.query.all()
        admin_dict = [admin.serialize() for admin in admins]
        intervention_records=InterventionRecord.query.all()
        intervention_record_dict=[intervention_record.serialize() for intervention_record in intervention_records]
        redflag_records=RedFlagRecord.query.all()
        redflag_records_dict=[redflag_record.serialize() for redflag_record in redflag_records ]
        
       
        return jsonify(intervention_record_dict,admin_dict,redflag_records_dict)
api.add_resource(AdminActions, '/adminactions') 

class AdminActionById(Resource):
    def get(self,id):
        admin=AdminAction.query.get(id)
        if not admin:
           return {'error':'admin not found'}, 404
        return jsonify(admin.serialize())
    
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
