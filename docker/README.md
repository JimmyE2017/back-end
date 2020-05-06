Docker
===

# Build image
```bash
docker build -f docker/Dockerfile --rm -t caplc/api:0.1.0 .
```
# Run Dev env
build à la volé

```bash
docker-compose -f docker/docker-compose.yml up
```