# Run host-inventry with RBAC
## Start Host-Inventory and Insights RBAC Containers
1. Copy doc/sample.env to .env
    ```bash
    PROMETHEUS_MULTIPROC_DIR=/tmp
    APP_NAME="inventory"
    INVENTORY_DB_USER="insights"
    INVENTORY_DB_PASS="insights"
    INVENTORY_DB_HOST="localhost"
    INVENTORY_DB_NAME="insights"
    INVENTORY_DB_POOL_TIMEOUT="5"
    INVENTORY_DB_POOL_SIZE="5"
    INVENTORY_DB_SSL_MODE=""
    INVENTORY_DB_SSL_CERT=""
    BYPASS_RBAC="false"
    # PUT UNLEASH_TOKEN HERE
    UNLEASH_CACHE_DIR=./.unleash
    UNLEASH_URL="http://localhost:4242/api"
    BYPASS_UNLEASH=true
    BYPASS_XJOIN=true

    # from rbac .env file
    API_PATH_PREFIX=/api/rbac

    DEVELOPMENT=True
    DJANGO_DEBUG=True
    # LDFLAGS="-L/opt/homebrew/opt/openssl@3/lib"
    # CPPFLAGS="-I/opt/homebrew/opt/openssl@3/include"
    BYPASS_BOP_VERIFICATION=True
    AUTHENTICATE_WITH_ORG_ID=True
    V2_APIS_ENABLED=True
    READ_ONLY_API_MODE=False
    PERMISSION_SEEDING_ENABLED=True
    ROLE_SEEDING_ENABLED=True
    GROUP_SEEDING_ENABLED=True
    V2_BOOTSTRAP_TENANT=True
    ```
2. pipenv install --dev
3. podman network create hbi-rbac-network
4. podman-compose -f dev.yml up # dev.yml containers rbc's containers' definitions.
    ```bash
    $ watch 'podman ps -a'
    $ podman ps -a
    CONTAINER ID  IMAGE                                        COMMAND               CREATED         STATUS                     PORTS                                                                     NAMES
    e726c0123f5c  docker.io/library/postgres:latest            postgres              41 minutes ago  Up 38 minutes (healthy)    0.0.0.0:5432->5432/tcp                                                    hbi-rbac-db
    31957958369f  docker.io/confluentinc/cp-zookeeper:latest   /etc/confluent/do...  40 minutes ago  Up 38 minutes              2181/tcp, 2888/tcp, 3888/tcp                                              zookeeper
    dafb90022206  quay.io/prometheus/pushgateway:latest                              39 minutes ago  Up 38 minutes              0.0.0.0:9091->9091/tcp                                                    prometheus_gateway
    ee7fad3edaf0  docker.io/minio/minio:latest                 server --address ...  39 minutes ago  Up 38 minutes              0.0.0.0:9099->9099/tcp, 0.0.0.0:9991->9991/tcp, 9000/tcp                  minio
    de40fd63da73  docker.io/library/redis:5.0.4                redis-server          39 minutes ago  Up 38 minutes (healthy)    0.0.0.0:6379->6379/tcp                                                    rbac_redis
    b7b1ba78e313  quay.io/cloudservices/export-service:latest  /bin/sh -c export...  39 minutes ago  Up 38 minutes              0.0.0.0:8001->8001/tcp, 0.0.0.0:9090->9090/tcp, 0.0.0.0:10010->10010/tcp  export-service
    b1d9449cb5d2  docker.io/confluentinc/cp-kafka:latest       /etc/confluent/do...  39 minutes ago  Up 38 minutes              0.0.0.0:9092->9092/tcp, 0.0.0.0:29092->29092/tcp                          kafka
    e805c8ffff85  quay.io/cloudservices/unleash-server:4.21.0  node index.js         38 minutes ago  Up 38 minutes              0.0.0.0:4242->4242/tcp                                                    unleash
    c8398cc99ff3  docker.io/minio/mc:latest                                          38 minutes ago  Exited (0) 38 minutes ago                                                                            s3-createbucket
    368e805e1c87  quay.io/cloudservices/rbac:140ec51                                 38 minutes ago  Up 38 minutes (healthy)    8080/tcp                                                                  rbac_worker
    41ea00dc372d  quay.io/cloudservices/rbac:140ec51                                 38 minutes ago  Up 38 minutes (healthy)    8080/tcp                                                                  rbac_scheduler
    7c60928c263b  quay.io/cloudservices/rbac:140ec51                                 38 minutes ago  Created                    0.0.0.0:9080->8080/tcp                                                    rbac_server
    d2de9cb9b9a1  quay.io/podman/hello:latest                  /usr/local/bin/po...  38 minutes ago  Created                                                                                              wait_for_app

    ```
## Populate Host-Inventory DataBase
5. make upgade_db
## Populate Insights-RBAC Database
6. Clone https://github.com/RedHatInsights/insights-rbac for populating the RBAC DB and DB migrations
7  Run `pipenv install --dev` and `pipenv shell`
8. Run `make run-migrations`
7. make serve PORT=8111
9. Verify roles have been created, run `curl http://localhost:8111/api/rbac/v1/roles/ | jq`.  Should see roles like:
    ```bash
        {
        "uuid": "30e0ea32-eb60-4a34-aeee-ac373405a39f",
        "name": "Inventory Groups Administrator",
        "display_name": "Workspace Administrator",
        "description": "Be able to read and edit Workspace data.",
        "created": "2025-03-20T21:17:29.360572Z",
        "modified": "2025-03-20T21:17:29.360899Z",
        "policyCount": 1,
        "accessCount": 2,
        "applications": [
            "inventory"
        ],
        "system": true,
        "platform_default": false,
        "admin_default": true,
        "external_role_id": null,
        "external_tenant": null
        },
        {
        "uuid": "e7761e9c-ad25-42ba-9773-017b05bcbba1",
        "name": "Inventory Hosts Administrator Local Test",
        "display_name": "Inventory Hosts Administrator Local Test",
        "description": "Be able to read and edit Inventory Hosts data. Just for local testing.",
        "created": "2025-03-20T21:17:29.358127Z",
        "modified": "2025-03-20T21:17:29.358205Z",
        "policyCount": 2,
        "accessCount": 2,
        "applications": [
            "inventory"
        ],
        "system": true,
        "platform_default": true,
        "admin_default": true,
        "external_role_id": null,
        "external_tenant": null
        },
    ```

## Create Hosts and Groups
10. In `host-inventory`, create some hosts and groups
11. To verify hosts and groups, hit  http://localhost:8080/api/inventory/v1/hosts
11. Verify in RBAC that workspaces have been created hit http://localhost:8111/api/rbac/v2/workspaces/
    ```json
    {
        "meta": {
            "count": 5,
            "limit": 10,
            "offset": 0
        },
        "links": {
            "first": "/api/rbac/v2/workspaces/?limit=10&offset=0",
            "next": null,
            "previous": null,
            "last": "/api/rbac/v2/workspaces/?limit=10&offset=0"
        },
        "data": [
            {
                "name": "Default Workspace",
                "id": "0195b570-c5b1-7511-bdaa-289f667e4b8b",
                "parent_id": "0195b570-c5b0-78c3-b5d0-3ec96969a95b",
                "description": null,
                "created": "2025-03-20T21:23:41.617084Z",
                "modified": "2025-03-20T21:23:41.674166Z",
                "type": "default"
            },
            {
                "name": "Root Workspace",
                "id": "0195b570-c5b0-78c3-b5d0-3ec96969a95b",
                "parent_id": null,
                "description": null,
                "created": "2025-03-20T21:23:41.617056Z",
                "modified": "2025-03-20T21:23:41.669060Z",
                "type": "root"
            },
            {
                "name": "second_group",
                "id": "0195b948-a6a2-72c3-83a1-b53d78aac740",
                "parent_id": "0195b570-c5b1-7511-bdaa-289f667e4b8b",
                "description": "second_group group",
                "created": "2025-03-21T15:18:21.090810Z",
                "modified": "2025-03-21T15:18:21.099042Z",
                "type": "standard"
            },
            {
                "name": "second_group",
                "id": "0195b944-2c87-7050-9352-cd07b819d8ea",
                "parent_id": "0195b570-c5b1-7511-bdaa-289f667e4b8b",
                "description": "second_group group",
                "created": "2025-03-21T15:13:27.687171Z",
                "modified": "2025-03-21T15:13:27.694823Z",
                "type": "standard"
            },
            {
                "name": "third_group",
                "id": "0195b984-a071-78e3-af37-7316ccf37b21",
                "parent_id": "0195b570-c5b1-7511-bdaa-289f667e4b8b",
                "description": "third_group group",
                "created": "2025-03-21T16:23:51.665957Z",
                "modified": "2025-03-21T16:23:51.671898Z",
                "type": "standard"
            }
        ]
    }
    ```
