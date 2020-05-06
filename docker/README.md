Docker
===

# Build image
```bash
docker build -f docker/Dockerfile --rm -t 2tons/api:0.1.0 .
```
# Run Dev env
build à la volé

```bash
docker-compose -f docker/docker-compose.yml up
```