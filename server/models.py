from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import MetaData
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from config import db, bcrypt



class User(db.Model, SerializerMixin):
    __tablename__="user"
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String, nullable=False)
    email=db.Column(db.String, nullable=False)
    _password_hash=db.Column(db.String, nullable=False)
    created_at=db.Column(db.DateTime, default=datetime.utcnow)
    role=db.Column(db.String, nullable=False,default='user')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,onupdate=datetime.utcnow)

    red_flag_records=db.relationship("RedFlagRecord", backref="user")
    intervention_records=db.relationship("InterventionRecord", backref="user")

    def serialize(self):
        return {"id":self.id,"username":self.username,"email":self.email,"password":self.password,  "created_at":self.created_at, "updated_at":self.updated_at} 

    @hybrid_property
    def password_hash(self):
        raise Exception('Password hashes may not be viewed')
    
    @password_hash.setter
    def password_hash(self,password):
        password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))
    @validates('email')
    def validate_email(self, key, email):
        if not email or '@' not in email:
            raise ValueError('Invalid email address format')
        return email

class RedFlagRecord(db.Model, SerializerMixin):
    __tablename__="redflagrecord"
    id=db.Column(db.Integer, primary_key=True)
    users_id=db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    description=db.Column(db.String,nullable=False)
    images=db.Column(db.String,nullable=False) 
    videos=db.Column(db.String,nullable=False)  
    created_at=db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,onupdate=datetime.utcnow)

    # user = db.relationship('User', backref='red_flag_record')

    def serialize(self):
        return {"id":self.id, "description":self.description, "images": self.images, "videos":self.videos, "created_at":self.created_at, "updated_at":self.updated_at}

class InterventionRecord(db.Model, SerializerMixin):
    __tablename__="interventionrecord"
    id=db.Column(db.Integer, primary_key=True)
    users_id=db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    description=db.Column(db.String, nullable=False )
    images=db.Column(db.String, nullable=False)  
    videos=db.Column(db.String, nullable=False)  
    created_at=db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,onupdate=datetime.utcnow)

    # user = db.relationship('User', backref='intervention_record')

    def serialize(self):
        return {"id":self.id, "description":self.description, "images": self.images, "videos":self.videos, "created_at":self.created_at, "updated_at":self.updated_at}

class AdminAction(db.Model, SerializerMixin):
    __tablename__="adminaction"
    id=db.Column(db.Integer, primary_key=True)
    redflagrecords_id=db.Column(db.Integer, db.ForeignKey("redflagrecord.id"),nullable=False)
    interventionrecords_id=db.Column(db.Integer, db.ForeignKey("interventionrecord.id"), nullable=False)
    action_type=db.Column(db.String)
    comments=db.Column(db.String)
    created_at=db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.now(),onupdate=datetime.now())

    redflagrecord= db.relationship('RedFlagRecord', backref="adminaction")
    interventionrecord=db.relationship('InterventionRecord', backref="adminaction")

    def serialize(self):
        return {"id":self.id,"action_type":self.action_type,"comments":self.comments, "created_at":self.created_at, "updated_at":self.updated_at}

    ALLOWED_ACTION_TYPES = ["under investigation", "rejected", "resolved"]

    @validates('action_type')
    def validates(self, key, action_type):
        if action_type not in self.ALLOWED_ACTION_TYPES:
            raise ValueError('Invalid action type. Allowed values are: {}'.format(', '.join(self.ALLOWED_ACTION_TYPES)))
        return action_type
