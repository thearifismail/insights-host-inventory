FROM registry.access.redhat.com/ubi8-minimal

USER root

# use general package name instead of a specific one,
# like "postgresql-10.15-1.module+el8.3.0+8944+1ca16b1f.x86_64",
# so future security fixes are autamatically picked up.
RUN microdnf install -y python38
RUN microdnf install -y postgresql
RUN microdnf -y upgrade

RUN pip3 install --user --upgrade pip
RUN pip3 install --user pipenv

USER 1001

WORKDIR /opt/app-root/src
COPY . .

# RUN pip install --upgrade pip && \
#     pip install pipenv && \
#     pipenv install --system --dev

RUN pipenv install --system --dev

CMD bash -c 'make upgrade_db && make run_inv_mq_service'
