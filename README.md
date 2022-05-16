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

## Modifying data

### Dataset "Samenstelling Vlaamse Regering"

#### Validation

The "Samenstelling Vlaamse Regering"-dataset can be [validated](https://www.itb.ec.europa.eu/shacl/any/upload) by means of a [SHACL](https://www.w3.org/TR/shacl/) constraints-file. The constraints-file can be found at `./config/shacl-validator`. The dataset itself can be found at `data/files/73089dee-7f76-42ba-9b06-556ff2bc5816.ttl`.

#### Providing an up-to-date dump

- Run the `CONSTRUCT`-query provided in `queries/construct_samenstelling_vr_dataset.sparql`. Select Virtuoso's `Pretty-printed Turtle (slow!)`-option.
- Save the result in `data/files/73089dee-7f76-42ba-9b06-556ff2bc5816.ttl`.
- Update the metadata of the distribution and related entities (modification dates, byte-sizes). See `queries/samenstelling_vr_dataset_meta_update.sparql` for an example.
