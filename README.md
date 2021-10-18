# example-mongo-web-api
Example for using a web REST API to access a mongodb database

## Setup local env

One-time setup of a virtualenv using `./setupenv.sh`.

Then, load the env using `. env/bin/activate`.

## Run server

`python server.py`, which should start a local server listening on port 8080.

You'll also need a mongodb for local testing.  Recommendation is:

```
docker run --rm -it --networking=host mongo:3
```

## Example adding new info

A REST API can be used simply:

```
curl -XPOST -H "Authorization: bearer $(python create_token.py)" \
     -d '{"id": 1, "result": 12345}' http://localhost:8080/api/test
```

## Docker container

A `Dockerfile` is already provided.
