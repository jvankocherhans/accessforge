FROM osixia/openldap:1.5.0

WORKDIR /

# Copy the entrypoint script
COPY scripts/init.sh /init.sh
RUN chmod +x /init.sh

# Use the custom entrypoint init-Script
# RUN /init.sh