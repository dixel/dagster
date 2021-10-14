import dagstermill as dm
from dagster import Field, InputDefinition, Int, fs_io_manager, job
from dagster.utils import script_relative_path
from docs_snippets_crag.legacy.data_science.download_file import download_file

k_means_iris = dm.define_dagstermill_op(
    "k_means_iris",
    script_relative_path("iris-kmeans_2.ipynb"),
    input_defs=[InputDefinition("path", str, description="Local path to the Iris dataset")],
    config_schema=Field(
        Int, default_value=3, is_required=False, description="The number of clusters to find"
    ),
)


@job(resource_defs={"io_manager": fs_io_manager})
def iris_classify():
    k_means_iris(download_file())
