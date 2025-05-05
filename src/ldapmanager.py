from ldap3 import Server, Connection, ALL, SUBTREE, MODIFY_ADD
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
                    print(
                        f"Retrying in {self.retry_delay} seconds... (Attempt {attempt}/{self.max_retries})")
                    time.sleep(self.retry_delay)
                else:
                    print("Max retries reached. Unable to connect to LDAP.")
                    raise

    def authentication(self, login_user_name, login_user_pwd):
        user_dn = f'uid={login_user_name},ou=users,{self.base_dn}'

        # Try binding with provided credentials
        user_connection = Connection(
            self.server, user=user_dn, password=login_user_pwd)
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
            attributes=['givenName', 'sn', 'mail',
                        'telephoneNumber', 'departmentNumber']
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

    def search_users(self, searchinput=""):
        if not searchinput:
            search_filter = '(objectClass=inetOrgPerson)'  # Fetch all users if no input is given
        else:
            search_filter = f'(|(givenName=*{searchinput}*)(sn=*{searchinput}*)(uid=*{searchinput}*))'

        self.connection.search(
            search_base=f'ou=users,{self.base_dn}',
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=['givenName', 'sn', 'uid', 'mail', 'telephoneNumber', 'departmentNumber']
        )

        users = []

        for entry in self.connection.entries:
            user = {
                "username": entry.uid.value if 'uid' in entry else '',
                "firstname": entry.givenName.value if 'givenName' in entry else '',
                "lastname": entry.sn.value if 'sn' in entry else '',
                "mail": entry.mail.value if 'mail' in entry else '',
                "phone": entry.telephoneNumber.value if 'telephoneNumber' in entry else '',
                "department": entry.departmentNumber.value if 'departmentNumber' in entry else '',
            }
            users.append(user)

        return users



    def get_all_users(self):
        search_base = self.base_dn
        search_filter = '(objectClass=inetOrgPerson)'
        attributes = ['cn', 'sn', 'mail', 'uid', 'telephoneNumber', 'departmentNumber', 'memberOf']

        self.connection.search(search_base,
                            search_filter,
                            search_scope=SUBTREE,
                            attributes=attributes)

        users = []
        for entry in self.connection.entries:
            username = str(entry.uid.value) if entry.uid else None
            firstname = str(entry.cn.value) if entry.cn else None
            lastname = str(entry.sn.value) if entry.sn else None
            mail = str(entry.mail.value) if entry.mail else None
            phone = str(entry.telephoneNumber.value) if entry.telephoneNumber else None
            department = str(entry.departmentNumber.value) if entry.departmentNumber else None
            groups = entry.memberOf.values if 'memberOf' in entry else []

            user = LdapUser(
                username=username,
                firstname=firstname,
                lastname=lastname,
                mail=mail,
                phone=phone,
                department=department,
                groups=groups
            )
            users.append(user)

        return users


    def _get_next_gid_number(self, start_gid=1000):
        # Search for all existing posixGroups to determine the next available gidNumber
        self.connection.search(
            search_base='ou=groups,' + self.base_dn,
            search_filter='(objectClass=posixGroup)',
            search_scope=SUBTREE,
            attributes=['gidNumber']
        )

        existing_gids = []
        for entry in self.connection.entries:
            if 'gidNumber' in entry:
                existing_gids.append(int(entry.gidNumber.value))

        # Find the next available gidNumber
        next_gid = max(existing_gids, default=start_gid - 1) + 1
        return str(next_gid)

            
    def create_group(self, group_name, group_description=""):
        group_dn = f"cn={group_name},ou=groups,{self.base_dn}"
        
        attributes = {
            'objectClass': ['top', 'posixGroup'],
            'cn': group_name,
            'gidNumber': self._get_next_gid_number(),
            'description': group_description
        }

        try:
            success = self.connection.add(dn=group_dn, attributes=attributes)
            if not success:
                print(f"Failed to create group {group_name}: {self.connection.result}")
            else:
                print(f"Group {group_name} created successfully.")
            return success
        except LDAPException as e:
            print(f"Error creating group {group_name}: {e}")
            return False

    def search_groups(self, searchinput):
        # If searchinput is None or empty, return all groups
        search_filter = '(objectClass=posixGroup)'  # Fetch all groups

        if searchinput:
            # If searchinput is provided, search for matching groups by name or description
            search_filter = f'(|(cn=*{searchinput}*)(description=*{searchinput}*))'

        self.connection.search(
            search_base=f'ou=groups,{self.base_dn}',
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=['cn', 'description']
        )

        groups = []
        for entry in self.connection.entries:
            groupname = entry.cn.value if 'cn' in entry else ""
            description = entry.description.value if 'description' in entry else ""
            groups.append(Group(groupname=groupname, description=description))

        return groups


    
    def add_user_to_group(self, username, groupname):
        group_dn = f"cn={groupname},ou=groups,{self.base_dn}"
        
        try:
            # Use MODIFY_ADD directly from ldap3
            self.connection.modify(
                group_dn,
                {'memberUid': [(MODIFY_ADD, [username])]})  # Correct usage of MODIFY_ADD
            print(f"User {username} added to group {groupname}")
        except LDAPException as e:
            print(f"Error adding user to group: {e}")


