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

if __name__ == "__main__":
    app.run(port=5555, debug=True)