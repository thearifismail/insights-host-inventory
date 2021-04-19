#!/bin/bash

# TAG=`cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 7 | head -n 1`
# TAG=$(python -c "import random, string; x = ''.join(random.choices(string.ascii_letters + string.digits, k=7)); print(x)")
# TAG=$(python ./tag.py)

set -x

TAG="7p7Gk9P"
IMAGE="127.0.0.1:5000/host-inventory"

# docker build -t quay.io/thearifismail/cachet-updater:latest ./cachet-tools

docker build -t $IMAGE:$TAG -f Dockerfile .
docker tag $IMAGE:$TAG `minikube ip`:5000/host-inventory:$TAG

# docker push $IMAGE:$TAG `minikube ip`:5000/host-inventory:$TAG --tls-verify=false

# docker push $IMAGE:$TAG `minikube ip`:5000/host-inventory:$TAG
docker push `minikube ip`:5000/host-inventory:$TAG

bonfire deploy --namespace hbi -p host-inventory/host-inventory/IMAGE_TAG=$TAG host-inventory -i $IMAGE=$TAG

echo $TAG
