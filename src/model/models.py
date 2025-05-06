from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from model.ACCESS import ACCESS
from mongoengine import Document, StringField, DateTimeField, DictField
from enum import Enum
import datetime

class UserActivityEnum(Enum):
    LOGIN = "Login"
    LOGOUT = "Logout"
    ASSIGN = "Assign"
    CREATE_GROUP = "Create group"
    ORDER_GROUP = "Order group"
    CANCEL_GROUP = "Cancel group"
    DELETE_GROUP = "Delete group"

class Activity(Document):
    activity = StringField(required=True, choices=[e.value for e in UserActivityEnum])  # Restrict to Enum values
    initiator = StringField(required=True, max_length=20)
    datetime = DateTimeField(default=datetime.datetime.now)
    details = DictField()

class LdapLoginUser(UserMixin):
    def __init__(self, username, access):
        self.id = username
        self.username = username
        self.access = access

    def is_admin(self):
        return self.access == ACCESS['admin']

    def allowed(self, access_level):
        return self.access >= access_level

class LdapUser():
    def __init__(self, username, firstname, lastname, mail, phone, department, groups):
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.mail = mail
        self.phone = phone
        self.department = department
        self.groups = groups
      
class Group():
    def __init__(self, gid, groupname, description):
        self.gid = gid
        self.groupname = groupname
        self.description = description