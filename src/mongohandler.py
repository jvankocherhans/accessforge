from mongoengine import connect
from model.models import Activity, UserActivityEnum

class MongoHandler:
    """
    MongoHandler executes all MongoDB relevant actions
    """
    def __init__(self, username, password, server, dbname):
        # Connect to the MongoDB server
        self.db = connect(
          db=dbname,  
          username=username,    
          password=password,
          host=server
        )

    def create_activity(self, activity_enum, initiator, details=None):
        """
        @param activity_enum
        @param initiator
        @param details
        
        @return activity
        
        Funktion erstellt basierend auf den Input Parametern eine Aktivität, welche in der MongoDB gespeichert wird.
        """
        
        # Existiert Aktivitätstyp?
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
