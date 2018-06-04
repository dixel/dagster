# Dagster

Dagster is an opinionated pipeline runner.

## Technical principles (Placeholder)

1.  Data pipelines should be organized into a logical DAG (directed, acyclic graph) of data computations. We call these data computations "solids".
2.  A solid is, at its core, a function, with semantics and abstractions designed for data computations in pipelines. As a function, it can be parameterized, allowing for its use in a variety of contexts (unit testing, local development, sampling, staging, production, etc).
3.  Code in data pipelines should be under test, and thus solids are designed to be independently testable.
4.  Data in data pipelines should also be under test. Data/pipeling testing is explicitly supported in a solid See https://medium.com/@expectgreatdata/down-with-pipeline-debt-introducing-great-expectations-862ddc46782a
5.  Gradual/Optional typing
6.  Metadata

## Local development setup

1. Create and activate virtualenv

```
python3 -m venv dagsterenv
source dagsterenv/bin/activate
```

2. Install dagster locally

```
pip install -e ./dagster
```

## Running pipelines

Ok, that was pretty confusing. So I guess inputs define input_sources arguments.

```
./bin/dagster pipeline pandas_hello_world execute --input num_csv.path=pandas_hello_world/num.csv
```
