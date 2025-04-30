from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3.core.exceptions import LDAPException, LDAPBindError

class LDAPManager():
  def __init__(self, ):
    self.ldap_server = f"ldap://localhost:389"
    self.root_dn = "dc=castle,dc=com"
    self.ldap_user_name = 'admin'
    self.ldap_password = 'Adminadmin1'
    self.user = f'cn=admin,dc=castle,dc=com'

    self.server = Server(self.ldap_server, get_info=ALL)

    self.connection = Connection(self.server,
                            user=self.user,
                            password=self.ldap_password,
                            auto_bind=True)

  def setup_connection():
    pass


  def get_users(self):
      search_base = self.root_dn
      search_filter = '(objectClass=inetOrgPerson)'
      attributes = ['cn', 'sn', 'mail', 'uid']

      self.connection.search(search_base,
                              search_filter,
                              search_scope=SUBTREE,
                              attributes=attributes)

      users = []
      for entry in self.connection.entries:
          users.append(entry.entry_to_json())
      print(users)
      return users