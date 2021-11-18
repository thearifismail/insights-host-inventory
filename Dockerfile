FROM registry.access.redhat.com/ubi8/python-38:1-74

USER root

RUN dnf module install -y postgresql:13

# remove packages not used by host-inventory to avoid security vulnerabilityes
RUN dnf remove -y npm

# upgrade security patches and cleanup any clutter left behind.
RUN dnf upgrade -y --security
RUN dnf clean all -y

USER 1001

WORKDIR /opt/app-root/src
COPY . .

RUN pip install --upgrade pip && \
    pip install pipenv && \
    pipenv install --system --dev

CMD bash -c 'make upgrade_db && make run_inv_mq_service'
