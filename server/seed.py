from models import User, RedFlagRecord, InterventionRecord, AdminAction, db
from app import app
from datetime import datetime

def seed_data():
    # Add Users
    with app.app_context():
        user1 = User(username='user1', email='user1@example.com', password='abcde')
        user2 = User(username='user2', email='user2@example.com', password='abcde')

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        # Add RedFlagRecords
        red_flag_record1 = RedFlagRecord(users_id=user1.id, description='Corruption incident', latitude=123.456, longitude=-78.910, images="one", videos="one")
        db.session.add(red_flag_record1)
        db.session.commit()

        # Add InterventionRecords
        intervention_record1 = InterventionRecord(users_id=user2.id, description='Request for road repair', latitude=98.765, longitude=-43.210, images="one", videos="one")
        db.session.add(intervention_record1)
        db.session.commit()

        # Add AdminActions
        admin_action1 = AdminAction(redflagrecords_id=red_flag_record1.id, interventionrecords_id=intervention_record1.id, action_type='under investigation')
        db.session.add(admin_action1)
        db.session.commit()


if __name__ == '__main__':
    seed_data()

# with app.app_context():
#     users_data=[
#         {"username":"Beatrice","email":"beatrice@gmail.com","password":"abcde"},
#         {"username":"Abdi","email":"abdi@gmail.com","password":"fghij"},
#         {"username":"Kennedy","email":"kennedy@gmail.com","password":"lmnop"},
#         {"username":"Lesi","email":"lesi@gmail.com","password":"abce"}
#     ]
#     for user_data in users_data:
#         user=User(**user_data)
#         db.session.add(user)
#     db.session.commit() 
