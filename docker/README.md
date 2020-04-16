Still WIP
### Build image
```shell script
docker build -f docker/Dockerfile --rm -t caplc_api:0.1.0 .
```

### Run server
Make sure env files are ready.
#### Development
```shell script
docker-compose -f docker/docker-compose.development.yml up
```
#### Production
```shell script
docker-compose -f docker/docker-compose.production.yml up
```
