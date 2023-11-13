# Themis

## Running the application
```
docker-compose up
```

The stack is built starting from [mu-project](https://github.com/mu-semtech/mu-project).

OpenAPI documentation can be generated using [cl-resources-openapi-generator](https://github.com/mu-semtech/cl-resources-openapi-generator).

## Updating Themis data

### Dataset "Samenstelling Vlaamse Regering"

An interactive mu-script is available to generate migrations based on data-input describing changes in government. Make sure to have [mu-cli](https://github.com/mu-semtech/mu-cli) installed before running. Since the script uses a docker image that isn't available in a registry, you need to build the image locally. Do this by running:
```
docker build -t "generate-mandatees-script" ./scripts/generate-mandatees/
```

A dumpfile containing the latest version of the government dataset is used as a source for defaults when running the script. The filename of the latest version of this dump-file can be determined by running the query at `queries/latest-govt-dataset.sparql` on `https://themis.vlaanderen.be/sparql`
```
mu script project-scripts generate-mandatees ./data/files/latest-dataset-example.ttl
```

#### Validation

The "Samenstelling Vlaamse Regering"-dataset can be [validated](https://www.itb.ec.europa.eu/shacl/any/upload) by means of a [SHACL](https://www.w3.org/TR/shacl/) constraints-file. The constraints-file can be found at `./config/shacl-validator`. 

#### Providing an up-to-date dump

- Run the `CONSTRUCT`-query provided in `queries/construct_samenstelling_vr_dataset.sparql`. Select Virtuoso's `Pretty-printed Turtle (slow!)`-option.
- Save the result to `data/files/insert_uuid_here.ttl` (replace the placeholder in the filename by a new uuid)
_make sure to stage the dump file in git (contents of `./data/files` are gitignored by default)_
- Create a migration that adds new dataset/distribution metadata for the file you just generated. This can be done with the following script. _Note that the script will automatically choose the newest ttl-file in `./data/files` as the source file for the distribution_
```
docker build -t "generate-dataset-script" ./scripts/generate-dataset/
mu script project-scripts generate-dataset
```
