# Pin to a specific minor version for reproducibility
FROM odoo:18.0

USER root

# Combine update, install, and cleanup into a single RUN layer
# Add --no-install-recommends to potentially reduce size
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-dejavu \
    gsfonts \
    # t1-xfree86-nonfree seems unavailable in newer Debian/Ubuntu, check if needed or find alternative
    # libfreetype6-dev is likely already a dependency of Odoo or its base image
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Ensure correct permissions if needed after package installation
# RUN chown -R odoo:odoo /var/lib/odoo # Example if permissions needed adjustment

USER odoo

