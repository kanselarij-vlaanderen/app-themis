# Themis

## Running the application
```
docker-compose up
```

The stack is built starting from [mu-project](https://github.com/mu-semtech/mu-project).

OpenAPI documentation can be generated using [cl-resources-openapi-generator](https://github.com/mu-semtech/cl-resources-openapi-generator).

## Updating Themis data

An interactive mu-script is available to generate migrations based on data-input describing changes in government. Make sure to have [mu-cli](https://github.com/mu-semtech/mu-cli) installed before running.

```
docker build -t "generate-mandatees-script" ./scripts/generate-mandatees/
mu script project-scripts generate-mandatees
```