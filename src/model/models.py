from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from model.ACCESS import ACCESS

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
    def __init__(self, groupname, description):
        self.groupname = groupname
        self.description = description