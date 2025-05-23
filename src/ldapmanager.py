from ldap3 import Server, Connection, ALL, SUBTREE, MODIFY_ADD, MODIFY_DELETE
from ldap3.core.exceptions import LDAPException, LDAPBindError
from model.ACCESS import *
from model.models import *

from model.ACCESS import ACCESS
from model.models import LdapLoginUser, LdapUser

import time


class LDAPManager():
    """
    LDAPManager Object executres all ldap relevant actions
    """
    def __init__(self, ldap_server, base_dn, ldap_conn_user_name, ldap_conn_user_pwd, max_retries=10, retry_delay=5):
        self.ldap_server = ldap_server
        self.base_dn = base_dn
        self.ldap_conn_user_name = ldap_conn_user_name
        self.ldap_conn_user_pwd = ldap_conn_user_pwd
        self.user = f'cn={self.ldap_conn_user_name},{self.base_dn}'
        self.max_retries = max_retries  # Max number of retries
        self.retry_delay = retry_delay  # Delay between retries in seconds

        self.users_dn = 'ou=users,' + self.base_dn
        self.groups_dn = 'ou=groups,' + self.base_dn
        
        self.__setup_connection()

    def __setup_connection(self):
        """
        Tries setting up a connection with the given ldap server. If at first not successful -> retry
        """
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
        """
        @param login_user_name: The username (uid) to authenticate.
        @param login_user_pwd: The password of the user.

        @return: LdapLoginUser object if authentication is successful, otherwise None.

        Authenticates a user against the LDAP server and returns their access level.
        """
        user_dn = f'uid={login_user_name},{self.users_dn}'

        user_connection = Connection(
            self.server, user=user_dn, password=login_user_pwd)
        if not user_connection.bind():
            return None 

        # Standard userrole
        access = ACCESS["user"]

        self.connection.search(
            search_base=self.groups_dn,
            search_filter=f'(memberUid={login_user_name})',
            search_scope=SUBTREE,
            attributes=['cn']
        )

        # check if user is administrator / is in "af admins" group
        for entry in self.connection.entries:
            group = entry.cn.value
            if group == 'af admins':
                access = ACCESS["admin"]
                break

        return LdapLoginUser(username=login_user_name, access=access)

    def get_user(self, username):
        """
        @param username: The LDAP username (uid) of the user.

        @return: LdapUser object containing user details and group memberships.

        Fetches detailed information about a specific LDAP user.
        """
        self.connection.search(
            search_base=self.users_dn,
            search_filter=f'(uid={username})',
            search_scope=SUBTREE,
            attributes=['givenName', 'sn', 'mail',
                        'telephoneNumber', 'departmentNumber']
        )

        # retrieves user values
        entry = self.connection.entries[0] if self.connection.entries else None
        firstname = entry.givenName.value if entry and 'givenName' in entry else ""
        lastname = entry.sn.value if entry and 'sn' in entry else ""
        mail = entry.mail.value if entry and 'mail' in entry else ""
        phone = entry.telephoneNumber.value if entry and 'telephoneNumber' in entry else ""
        department = entry.departmentNumber.value if entry and 'departmentNumber' in entry else ""
        groups = []

        # searches for groups user is member of
        self.connection.search(
            search_base=self.groups_dn,
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
        """
        @param searchinput: Optional search string for name or uid. If empty, all users are returned.

        @return: List of user dictionaries matching the search criteria.

        Searches for users based on partial name or uid.
        """
        if not searchinput:
            # Fetch all users if no input is given
            search_filter = '(objectClass=inetOrgPerson)'
        else:
            # seraches in givenName, sn and uid
            search_filter = f'(|(givenName=*{searchinput}*)(sn=*{searchinput}*)(uid=*{searchinput}*))'

        self.connection.search(
            search_base=self.users_dn,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=['givenName', 'sn', 'uid', 'mail',
                        'telephoneNumber', 'departmentNumber']
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
        """
        @return: List of LdapUser objects for all users in the LDAP directory.

        Retrieves all users with their attributes and group memberships.
        """
        search_base = self.base_dn
        search_filter = '(objectClass=inetOrgPerson)'
        attributes = ['cn', 'sn', 'mail', 'uid',
                      'telephoneNumber', 'departmentNumber', 'memberOf']

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
            phone = str(
                entry.telephoneNumber.value) if entry.telephoneNumber else None
            department = str(
                entry.departmentNumber.value) if entry.departmentNumber else None
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
        """
        @param start_gid: The starting GID to use if no groups are found.

        @return: The next available GID number as a string.

        Finds the next free gidNumber for a new group.
        """
        self.connection.search(
            search_base=self.groups_dn,
            search_filter='(objectClass=posixGroup)',
            search_scope=SUBTREE,
            attributes=['gidNumber']
        )

        existing_gids = []
        for entry in self.connection.entries:
            if 'gidNumber' in entry:
                existing_gids.append(int(entry.gidNumber.value))

        next_gid = max(existing_gids, default=start_gid - 1) + 1
        return str(next_gid)

    def create_group(self, group_name, group_description=""):
        """
        @param group_name: Name of the new group.
        @param group_description: Optional description of the group.

        @return: True if the group was created successfully, False otherwise.

        Creates a new posixGroup in LDAP.
        """
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
                print(
                    f"Failed to create group {group_name}: {self.connection.result}")
            else:
                print(f"Group {group_name} created successfully.")
            return success
        except LDAPException as e:
            print(f"Error creating group {group_name}: {e}")
            return False

    def get_group(self, group_name):
        """
        @param group_name: Name (cn) of the group.

        @return: Dictionary with group attributes if found, None otherwise.

        Retrieves information about a specific group from LDAP.
        """
        search_base = self.groups_dn
        search_filter = f"(cn={group_name})"
        attributes = ['cn', 'gidNumber', 'description']

        try:
            self.connection.search(
                search_base=search_base,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=attributes
            )

            if self.connection.entries:
                entry = self.connection.entries[0]
                print(f"Group {group_name} found:")
                print(f"Distinguished Name (DN): {entry.entry_dn}")
                print(f"Group Name: {entry.cn.value}")
                print(
                    f"GID Number: {entry.gidNumber.value if 'gidNumber' in entry else ''}")
                print(
                    f"Description: {entry.description.value if 'description' in entry else ''}")

                return {
                    "cn": entry.cn.value,
                    "gidNumber": entry.gidNumber.value if 'gidNumber' in entry else '',
                    "description": entry.description.value if 'description' in entry else ''
                }
            else:
                print(f"Group {group_name} not found.")
                return None
        except LDAPException as e:
            print(f"Error retrieving group {group_name}: {e}")
            return None

    def search_groups(self, searchinput):
        """
        @param searchinput: Partial name or description to search for.

        @return: List of Group objects matching the search.

        Searches LDAP for groups matching the given input.
        """
        search_filter = '(objectClass=posixGroup)'

        if searchinput:
            search_filter = f'(|(cn=*{searchinput}*)(description=*{searchinput}*))'

        self.connection.search(
            search_base=self.groups_dn,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=['gidNumber', 'cn', 'description']
        )

        groups = []
        for entry in self.connection.entries:
            gidNumber = entry.gidNumber.value if 'gidNumber' in entry else ""
            groupname = entry.cn.value if 'cn' in entry else ""
            description = entry.description.value if 'description' in entry else ""
            groups.append(
                Group(gid=gidNumber, groupname=groupname, description=description))

        return groups

    def add_user_to_group(self, username, group):
        """
        @param username: The username to add.
        @param group: Dictionary with at least the 'groupname' key.

        Adds a user to a specified group using memberUid.
        """
        group_dn = f"cn={group['groupname']},ou=groups,{self.base_dn}"

        try:
            self.connection.modify(
                group_dn,
                {
                    'memberUid': [(MODIFY_ADD, [username])]
                }
            )
            print(
                f"User {username} added to group with name {group['groupname']}")
        except LDAPException as e:
            print(f"Error adding user to group: {e}")

    def cancel_group(self, username, group):
        """
        @param username: The username to remove.
        @param group: Name of the group (cn).

        Removes a user from a group in LDAP.
        """
        # Format the group DN using the group name
        group_dn = f"cn={group},ou=groups,{self.base_dn}"

        try:
            self.connection.modify(
                group_dn,
                {
                    'memberUid': [(MODIFY_DELETE, [username])]
                }
            )
            print(f"User {username} removed from group with name {group}")
        except LDAPException as e:
            print(f"Error removing user from group: {e}")

    def delete_group(self, groupname):
        """
        @param groupname: Name of the group (cn) to delete.

        Deletes the specified group from LDAP.
        """
        group_dn = f"cn={groupname},ou=groups,{self.base_dn}"

        try:
            self.connection.delete(group_dn)
            print(f"Group {groupname} has been deleted successfully.")
        except LDAPException as e:
            print(f"Error deleting group: {e}")
