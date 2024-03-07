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

# API Routes

# Get all red flag records
@app.route('/api/red_flags', methods=['GET'])
def get_red_flags():
    red_flags = RedFlagRecord.query.all()
    return jsonify([record.serialize() for record in red_flags])

# Get a specific red flag record by ID
@app.route('/api/red_flags/<int:redflag_id>', methods=['GET'])
def get_red_flag(redflag_id):
    redflag_record = RedFlagRecord.query.get(redflag_id)
    if redflag_record:
        return jsonify(redflag_record.serialize()), 200
    else:
        return jsonify({'message': 'RedFlag Record not found'}), 404

# Create a new red flag record
@app.route('/api/red_flags', methods=['POST'])
def create_red_flag():
    data = request.json
    description = data.get('description')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    images = data.get('images')
    videos = data.get('videos')
    if not description or not latitude or not longitude:
        return jsonify({'message': 'Description, latitude, and longitude are required fields'}), 400
    new_red_flag = RedFlagRecord(
        description=description,
        latitude=latitude,
        longitude=longitude,
        images=images,
        videos=videos
    )
    db.session.add(new_red_flag)
    db.session.commit()
    return jsonify({'message': 'RedFlag Record created successfully', 'id': new_red_flag.id}), 201

# Update an existing red flag record
@app.route('/api/red_flags/<int:redflag_id>', methods=['PUT'])
def update_red_flag(redflag_id):
    redflag_record = RedFlagRecord.query.get(redflag_id)
    if not redflag_record:
        return jsonify({'message': 'RedFlag Record not found'}), 404
    data = request.json
    description = data.get('description')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    images = data.get('images')
    videos = data.get('videos')
    if description:
        redflag_record.description = description
    if latitude:
        redflag_record.latitude = latitude
    if longitude:
        redflag_record.longitude = longitude
    if images:
        redflag_record.images = images
    if videos:
        redflag_record.videos = videos
    db.session.commit()
    return jsonify({'message': 'RedFlag Record updated successfully'}), 200

# Delete a red flag record
@app.route('/api/red_flags/<int:redflag_id>', methods=['DELETE'])
def delete_red_flag(redflag_id):
    redflag_record = RedFlagRecord.query.get(redflag_id)
    if not redflag_record:
        return jsonify({'message': 'RedFlag Record not found'}), 404
    db.session.delete(redflag_record)
    db.session.commit()
    return jsonify({'message': 'RedFlag Record deleted successfully'}), 200

class InterventionRecords(Resource):
    def get(self):
        intervention_records=InterventionRecord.query.all()
        intervention_record_dict=[intervention_record.serialize() for intervention_record in intervention_records]
        return jsonify(intervention_record_dict)
api.add_resource(InterventionRecords, '/interventionrecords')
from flask import jsonify

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
    
    def put(self,id):
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
