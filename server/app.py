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
        data = request.json
        description = data.get('description')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        images = data.get('images')
        videos = data.get('videos') 

        if not description or not latitude or not longitude:
            return {'message': 'Description, latitude, and longitude are required fields'}, 400

       

        new_data = RedFlagRecord(
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


api.add_resource(InterventionRecordsById, '/interventionrecords/<int:id>')




if __name__ == "__main__":
    app.run(port=5555, debug=True)
