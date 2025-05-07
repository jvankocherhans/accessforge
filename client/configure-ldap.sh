#!/bin/bash

set -e

# Use environment variables or defaults
LDAP_URI=${LDAP_URI:-ldap://ldap:389}
BASE_DN=${LDAP_BASE_DN:-dc=castle,dc=com}
BIND_DN=${LDAP_BIND_DN:-cn=admin,dc=castle,dc=com}
BIND_PW=${LDAP_BIND_PW:-Adminadmin1}
ALLOWED_GROUP=${LDAP_ALLOWED_GROUP:-sshusers}

echo "ldap-auth-config ldap-auth-config/ldapns/ldap-server string $LDAP_URI" | debconf-set-selections
echo "ldap-auth-config ldap-auth-config/ldapns/base-dn string $BASE_DN" | debconf-set-selections
echo "ldap-auth-config ldap-auth-config/dbrootlogin boolean true" | debconf-set-selections
echo "ldap-auth-config ldap-auth-config/rootbinddn string $BIND_DN" | debconf-set-selections
echo "$BIND_PW" > /etc/ldap.secret
chmod 600 /etc/ldap.secret

# Update /etc/ldap.conf
cat <<EOF > /etc/ldap.conf
host ${LDAP_URI#ldap://}
base $BASE_DN
binddn $BIND_DN
bindpw $BIND_PW
ldap_version 3
pam_password md5
EOF

# Update /etc/nsswitch.conf
sed -i 's/^passwd:.*/passwd:         files ldap/' /etc/nsswitch.conf
sed -i 's/^group:.*/group:          files ldap/' /etc/nsswitch.conf
sed -i 's/^shadow:.*/shadow:         files ldap/' /etc/nsswitch.conf

# PAM config for SSH login
echo "session required pam_mkhomedir.so skel=/etc/skel/ umask=0022" >> /etc/pam.d/common-session

# Allow only specific group
echo "AllowGroups $ALLOWED_GROUP" >> /etc/ssh/sshd_config

# Start name service cache daemon (optional)
service nscd restart
