FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y \
    libnss-ldap \
    libpam-ldap \
    ldap-utils \
    nscd \
    sudo \
    openssh-server \
    iputils-ping && \
    rm -rf /var/lib/apt/lists/*

COPY configure-ldap.sh /configure-ldap.sh
RUN chmod +x /configure-ldap.sh && /configure-ldap.sh

RUN mkdir /var/run/sshd
EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
