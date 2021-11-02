# Themis

## Running the application
```
docker-compose up
```

The stack is built starting from [mu-project](https://github.com/mu-semtech/mu-project).

OpenAPI documentation can be generated using [cl-resources-openapi-generator](https://github.com/mu-semtech/cl-resources-openapi-generator).

## SHACL Validation

The "Samenstelling Vlaamse Regering"-dataset can be [validated](https://www.itb.ec.europa.eu/shacl/any/upload) by means of a [SHACL](https://www.w3.org/TR/shacl/) constraints-file. The constraints-file can be found at `./config/shacl-validator`. The "Samenstelling Vlaamse Regering"-dataset can be found at `data/files/73089dee-7f76-42ba-9b06-556ff2bc5816.ttl`.

