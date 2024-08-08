# How to Test Cache in Host Inventory
Used local flow to test MQ caching and check System based API query for cached data.
Add the following the the compose file:
```yaml
    redis:
      image: redis:latest
      restart: always
      ports:
        - "6379:6379"
      volumes:
        - ./cache:/root/redis
      environment:
        - REDIS_PORT=6379
        - REDIS_DATABASES=2
```
Add the following to the environment:
```bash
INVENTORY_API_CACHE_TIMEOUT_SECONDS=30
INVENTORY_API_CACHE_TYPE="RedisCache"
IS_INSIGHTS_CLIENT="True"
```
You must also enable the `hbi.api.use-cached-insights-client-system` feature flag in Unleash.

Run the following to populate the Cache:
``bash
make run_inv_mq_service
```
And in another terminal
```bash
make run_inv_mq_service_test_producer
```
This will make a system with an insights_id value that will be stored in the cache.

Review the created redis key:
```bash
podman exec -it insights-host-inventory-redis-1 redis-cli keys "*"
```
Next launch the web server:
```bash
curl --location 'http://localhost:8080/api/inventory/v1/hosts?insights_id=56f6c4fc-250f-4b01-8255-6719b2e88eb4' \
--header 'x-rh-identity: eyJpZGVudGl0eSI6ewogICAgIm9yZ19pZCI6ICI1ODk0MzAwIiwKICAgICJ0eXBlIjogIlN5c3RlbSIsCiAgICAiYXV0aF90eXBlIjogImNlcnQtYXV0aCIsCiAgICAic3lzdGVtIjogeyJjbiI6ICIxYjM2YjIwZi03ZmEwLTQ0NTQtYTZkMi0wMDgyOTRlMDYzNzgiLCAiY2VydF90eXBlIjogInN5c3RlbSJ9LAogICAgImludGVybmFsIjogeyJhdXRoX3RpbWUiOiA2MzAwfQp9fQ=='
```
You should see the response from the cache, with a log entry that the feature flag had been applied.
Next test cache deletion via curl or Postman (update the bios_uuid to a valid value for an existing system) when a change occurs to the system:
```bash
curl --location 'http://localhost:8080/api/inventory/v1/hosts/checkin' \
--header 'x-rh-identity: eyJpZGVudGl0eSI6eyJvcmdfaWQiOiI1ODk0MzAwIiwidHlwZSI6IlVzZXIiLCJhdXRoX3R5cGUiOiJiYXNpYy1hdXRoIiwidXNlciI6eyJ1c2VyX2lkIjogNzE0LCAidXNlcm5hbWUiOiJ0dXNlckByZWRoYXQuY29tIiwiZW1haWwiOiJ0dXNlckByZWRoYXQuY29tIiwiZmlyc3RfbmFtZSI6InRlc3QiLCJsYXN0X25hbWUiOiJ1c2VyIiwiaXNfYWN0aXZlIjp0cnVlLCJpc19vcmdfYWRtaW4iOmZhbHNlLCJpc19pbnRlcm5hbCI6dHJ1ZSwibG9jYWxlIjoiZW5fVVMifX19' \
--header 'Content-Type: application/json' \
--data '{"bios_uuid": "58563b5f-5004-4e0a-a8cb-1bc757c60eb4"}'
```
Review the existing redis keys:
```bash
docker exec -it insights-host-inventory-redis-1 redis-cli keys "*"
```
The key should have been deleted.
