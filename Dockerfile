FROM registry.access.redhat.com/ubi8-minimal

USER root

# use general package name instead of a specific one,
# like "postgresql-10.15-1.module+el8.3.0+8944+1ca16b1f.x86_64",
# so future security fixes are autamatically picked up.
RUN microdnf install -y python38
RUN microdnf install -y postgresql
RUN microdnf install -y which
RUN microdnf -y upgrade


RUN chown -R 1001:0 /usr/local/lib

# RUN chmod a+r /usr/local/lib/python3.8
# RUN chmod a+w /usr/local/lib/python3.8
# USER 1001

# RUN pwd

# WORKDIR /opt/app-root/src
# COPY . .

# RUN pwd

# RUN pip3 install --user --upgrade pip
# RUN pip3 install --user pipenv
# RUN pipenv install --system --dev

# RUN pipenv install --system --dev

# CMD bash -c 'make upgrade_db && make run_inv_mq_service'
RUN echo "Done building image!!!"

