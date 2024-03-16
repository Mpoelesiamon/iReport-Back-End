from models import User, RedFlagRecord, InterventionRecord, AdminAction, db
from app import app
from datetime import datetime
import random
def seed_data():
    # Add Users
    with app.app_context():
        User.query.delete()
        RedFlagRecord.query.delete()
        InterventionRecord.query.delete()
        AdminAction.query.delete()


        user1 = User(username='user1', email='user1@example.com',role='admin')
        user1.password_hash = "password"
        user2 = User(username='user2', email='user2@example.com',role='user')
        user2.password_hash = "password"

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        # Add RedFlagRecords
        red_flag_record1 = RedFlagRecord(
            users_id=user1.id,
            description='Corruption incident',
            latitude=123.456,
            longitude=-78.910,
            images="one",
            videos="one",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(red_flag_record1)
        db.session.commit()

        # Add InterventionRecords
        intervention_record1 = InterventionRecord(
            users_id=user2.id,
            description='Request for road repair',
            latitude=98.765,
            longitude=-43.210,
            images="one",
            videos="one",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(intervention_record1)
        db.session.commit()

        # Add AdminActions
        admin_action1 = AdminAction(redflagrecords_id=red_flag_record1.id, interventionrecords_id=intervention_record1.id, action_type='under investigation', comments="none")
        db.session.add(admin_action1)
        db.session.commit()
        print("completed seed")
        

if __name__ == '__main__':

    seed_data()