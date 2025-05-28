FROM odoo:18

# Install any additional dependencies here
# For example, to install Python packages, you can use:
# RUN pip install <package_name>

# Copy custom addons if any
COPY ./addons /mnt/extra-addons

# Set the working directory
WORKDIR /var/lib/odoo

# Expose the Odoo port
EXPOSE 8069

# Command to run Odoo
CMD ["odoo", "--config", "/etc/odoo/odoo.conf"]