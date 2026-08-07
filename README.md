# Themis

## Running the application
```
docker-compose up
```

The stack is built starting from [mu-project](https://github.com/mu-semtech/mu-project).

OpenAPI documentation can be generated using [cl-resources-openapi-generator](https://github.com/mu-semtech/cl-resources-openapi-generator).

## Updating Themis data

### Dataset "Samenstelling Vlaamse Regering"

An interactive mu-script is available to generate migrations based on data-input describing changes in government. Make sure to have [mu-cli](https://github.com/mu-semtech/mu-cli) installed before running.

A dumpfile containing the latest version of the government dataset is used as a source for defaults when running the script. By default the script determines the latest dump-file automatically by running the query at `queries/latest-govt-dataset.sparql` against the project's Virtuoso (the triplestore service must be running for this).

```
mu script project-scripts generate-mandatees
```

Alternatively, the path to a dump-file can be provided explicitly:

```
mu script project-scripts generate-mandatees ./data/files/latest-dataset-example.ttl
```

For mandatees that are renewed within an existing regeringssamenstelling, the script also generates a migration that adds the new mandatees to their kabinet (`org:hasMember`), based on the kabinet membership of the old mandatee in Virtuoso. For mandatees whose kabinet can't be determined automatically (e.g. entirely new ministers), the script prints the information needed to create that migration manually.

#### Validation

The "Samenstelling Vlaamse Regering"-dataset can be [validated](https://www.itb.ec.europa.eu/shacl/any/upload) by means of a [SHACL](https://www.w3.org/TR/shacl/) constraints-file. The constraints-file can be found at `./config/shacl-validator`. 

#### Providing an up-to-date dump

The following script generates an up-to-date dump and a migration that adds new dataset/distribution metadata for it. It requires the stack (at least the `triplestore` service) to be running, since it:
- runs the `CONSTRUCT`-query provided in `queries/construct_samenstelling_vr_dataset.sparql` against the triplestore and saves the result to `data/files/<uuid>.ttl`
- links the new dataset to the previous one (the minister dataset with the most recent `dct:issued` date) via `prov:wasRevisionOf`
```
mu script project-scripts generate-dataset
```
_make sure to stage the dump file in git (contents of `./data/files` are gitignored by default)_
