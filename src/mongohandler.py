from mongoengine import connect
from model.models import Activity, UserActivityEnum

class MongoHandler:
    def __init__(self, username, password, server, dbname):
        # Connect to the MongoDB server
        self.db = connect(
          db=dbname,  
          username=username,    
          password=password,
          host=server
        )

    def create_activity(self, activity_enum, initiator, details=None):
        # Make sure activity_enum is one of the allowed values in UserActivityEnum
        if activity_enum.value not in [e.value for e in UserActivityEnum]:
            raise ValueError(f"Invalid activity name: {activity_enum.value}. Must be one of {', '.join([e.value for e in UserActivityEnum])}")

        activity = Activity(
            activity=activity_enum.value,
            initiator=initiator,
            details=details or {}
        )

        activity.save()
        print(f"Activity '{activity_enum.value}' created and saved successfully!")
        return activity
