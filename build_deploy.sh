#!/bin/bash

set -exv

IMAGE="quay.io/thearifismail/host-inventory"
IMAGE_TAG=$(git rev-parse --short=7 HEAD)
SMOKE_TEST_TAG="latest"

# docker login -u="thearifismail+cache_robot_account" -p="2XXNOHGKNVUHARIAYJNUDNMGFZV67RBVUXB1GMK56UVMN0X3T34SJTZHOR9DVX9C" quay.io
QUAY_USER="thearifismail"
QUAY_TOKEN="insights"

if [[ -z "$QUAY_USER" || -z "$QUAY_TOKEN" ]]; then
    echo "QUAY_USER and QUAY_TOKEN must be set"
    exit 1
fi


AUTH_CONF_DIR="$(pwd)/.docker"
mkdir -p $AUTH_CONF_DIR
export REGISTRY_AUTH_FILE="$AUTH_CONF_DIR/auth.json"

docker login -u="$QUAY_USER" -p="$QUAY_TOKEN" quay.io
# docker login -u="$RH_REGISTRY_USER" -p="$RH_REGISTRY_TOKEN" registry.redhat.io
docker build -f Dockerfile -t "${IMAGE}:${IMAGE_TAG}" .
docker push "${IMAGE}:${IMAGE_TAG}"
