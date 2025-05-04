from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3.core.exceptions import LDAPException, LDAPBindError
from model.ACCESS import *
from model.models import *

from model.ACCESS import ACCESS
from model.models import LdapLoginUser, LdapUser

import time

class LDAPManager():
  def __init__(self, ldap_server, base_dn, ldap_conn_user_name, ldap_conn_user_pwd, max_retries=10, retry_delay=5):
    self.ldap_server = ldap_server
    self.base_dn = base_dn
    self.ldap_conn_user_name = ldap_conn_user_name
    self.ldap_conn_user_pwd = ldap_conn_user_pwd
    self.user = f'cn={self.ldap_conn_user_name},{self.base_dn}'
    self.max_retries = max_retries  # Max number of retries
    self.retry_delay = retry_delay  # Delay between retries in seconds

    self.__setup_connection()

  def __setup_connection(self):
    attempt = 0
    while attempt < self.max_retries:
        try:
            # Attempt to set up the LDAP connection
            self.server = Server(self.ldap_server, get_info=ALL)
            self.connection = Connection(
                self.server,
                user=self.user,
                password=self.ldap_conn_user_pwd,
                auto_bind=True
            )
            print("LDAP connection established.")
            break  # If successful, exit the loop
        except LDAPBindError as e:
            print(f"LDAP bind error: {e}")
            raise
        except LDAPException as e:
            print(f"LDAP exception: {e}")
            attempt += 1
            if attempt < self.max_retries:
                print(f"Retrying in {self.retry_delay} seconds... (Attempt {attempt}/{self.max_retries})")
                time.sleep(self.retry_delay)
            else:
                print("Max retries reached. Unable to connect to LDAP.")
                raise
  
  def authentication(self, login_user_name, login_user_pwd):
    user_dn = f'uid={login_user_name},ou=users,{self.base_dn}'

    # Try binding with provided credentials
    user_connection = Connection(self.server, user=user_dn, password=login_user_pwd)
    if not user_connection.bind():
        return None  # Failed authentication

    # Re-bind as admin to search group membership
    self.__setup_connection()

    # Setze einen Standardwert für access
    access = ACCESS["user"]

    self.connection.search(
        search_base='ou=groups,' + self.base_dn,
        search_filter=f'(memberUid={login_user_name})',
        search_scope=SUBTREE,
        attributes=['cn']
    )
    
    for entry in self.connection.entries:
        group = entry.cn.value
        print(group)
        if group == 'af admins':
            access = ACCESS["admin"]
            break

    return LdapLoginUser(username=login_user_name, access=access)

  
  def get_user(self, username):
    self.connection.search(
        search_base='ou=users,' + self.base_dn,
        search_filter=f'(uid={username})',
        search_scope=SUBTREE,
        attributes=['givenName', 'sn', 'mail', 'telephoneNumber', 'departmentNumber']
    )

    entry = self.connection.entries[0] if self.connection.entries else None
    firstname = entry.givenName.value if entry and 'givenName' in entry else ""
    lastname = entry.sn.value if entry and 'sn' in entry else ""
    mail = entry.mail.value if entry and 'mail' in entry else ""
    phone = entry.telephoneNumber.value if entry and 'telephoneNumber' in entry else ""
    department = entry.departmentNumber.value if entry and 'departmentNumber' in entry else ""
    groups = []

    self.connection.search(
        search_base='ou=groups,' + self.base_dn,
        search_filter=f'(memberUid={username})',
        search_scope=SUBTREE,
        attributes=['cn']
    )

    for entry in self.connection.entries:
        group = entry.cn.value
        groups.append(group)

    return LdapUser(
        username=username,
        firstname=firstname,
        lastname=lastname,
        mail=mail,
        phone=phone,
        department=department,
        groups=groups,
    )

  def search_users(self, searchinput):
    # Create the search filter to search in 'givenName', 'sn', or 'uid'
    search_filter = f'(|(givenName=*{searchinput}*)(sn=*{searchinput}*)(uid=*{searchinput}*))'

    # Perform the search in the 'ou=users' organizational unit
    self.connection.search(
        search_base=f'ou=users,{self.base_dn}',
        search_filter=search_filter,
        search_scope=SUBTREE,
        attributes=['givenName', 'sn', 'uid', 'mail', 'telephoneNumber', 'departmentNumber']
    )

    users = []

    # Loop through the search results and collect the user data
    for entry in self.connection.entries:
        # Access the attributes directly from the entry
        
        user = LdapUser(
          username=entry.uid.value if 'uid' in entry else '',
          firstname=entry.givenName.value if 'givenName' in entry else '',
          lastname=entry.sn.value if 'sn' in entry else '',
          mail=entry.mail.value if 'mail' in entry else '',
          phone=entry.telephoneNumber.value if 'telephoneNumber' in entry else '',
          department=entry.departmentNumber.value if 'departmentNumber' in entry else '',
          groups=[]
          )
        
        # Append the user dictionary to the users list
        users.append(user)

    # Return the list of users (JSON response in Flask)
    return users

  def get_users(self):
      search_base = self.base_dn
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