from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import MetaData
from datetime import datetime

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db=SQLAlchemy(metadata=metadata)

class User(db.Model, SerializerMixin):
    __tablename__="user"
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String, nullable=False)
    email=db.Column(db.String, nullable=False)
    password=db.Column(db.String, nullable=False)
    created_at=db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,onupdate=datetime.utcnow)

    red_flag_records=db.relationship("RedFlagRecord", backref="user")
    intervention_records=db.relationship("InterventionRecord", backref="user")

    def serialize(self):
        return {"id":self.id,"username":self.username,"email":self.email,"password":self.password,  "created_at":self.created_at, "updated_at":self.updated_at} 
class RedFlagRecord(db.Model, SerializerMixin):
    __tablename__="redflagrecord"
    id=db.Column(db.Integer, primary_key=True)
    users_id=db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    description=db.Column(db.String)
    latitude=db.Column(db.Float)
    longitude=db.Column(db.Float)
    images=db.Column(db.String) 
    videos=db.Column(db.String)  
    created_at=db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,onupdate=datetime.utcnow)

    # user = db.relationship('User', backref='red_flag_record')

    def serialize(self):
        return {"id":self.id, "description":self.description, "latitude":self.latitude, "longitude":self.longitude, "images": self.images, "videos":self.videos, "created_at":self.created_at, "updated_at":self.updated_at}

class InterventionRecord(db.Model, SerializerMixin):
    __tablename__="interventionrecord"
    id=db.Column(db.Integer, primary_key=True)
    users_id=db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    description=db.Column(db.String)
    latitude=db.Column(db.Float)
    longitude=db.Column(db.Float)
    images=db.Column(db.String)  
    videos=db.Column(db.String)  
    created_at=db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,onupdate=datetime.utcnow)

    # user = db.relationship('User', backref='intervention_record')

    def serialize(self):
        return {"id":self.id, "description":self.description, "latitude":self.latitude, "longitude":self.longitude, "images": self.images, "videos":self.videos, "created_at":self.created_at, "updated_at":self.updated_at}

class AdminAction(db.Model, SerializerMixin):
    __tablename__="adminaction"
    id=db.Column(db.Integer, primary_key=True)
    redflagrecords_id=db.Column(db.Integer, db.ForeignKey("redflagrecord.id"), nullable=False)
    interventionrecords_id=db.Column(db.Integer, db.ForeignKey("interventionrecord.id"), nullable=False)
    action_type=db.Column(db.String)
    comments=db.Column(db.String)
    created_at=db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,onupdate=datetime.utcnow)

    redflagrecord= db.relationship('RedFlagRecord', backref="adminaction")
    interventionrecord=db.relationship('InterventionRecord', backref="adminaction")

    def serialize(self):
        return {"id":self.id,"action_type":self.action_type,"comments":self.comments, "created_at":self.created_at, "updated_at":self.updated_at}

@validates('action_type')
def validates(self,key,action_type):
    action_type=["under investigation","rejected","resolved"]
    if not action_type:
        raise ValueError('user must specify action_type')
    return action_type