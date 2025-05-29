FROM odoo:18

USER root

RUN apt-get update && apt-get install -y \
    fonts-dejavu \
    gsfonts \
    t1-xfree86-nonfree \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

USER odoo
