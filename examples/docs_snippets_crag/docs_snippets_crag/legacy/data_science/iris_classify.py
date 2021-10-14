import dagstermill as dm
from dagster import fs_io_manager, job, local_file_manager
from dagster.utils import script_relative_path

k_means_iris = dm.define_dagstermill_op("k_means_iris", script_relative_path("iris-kmeans.ipynb"))


@job(resource_defs={"io_manager": fs_io_manager, "file_manager": local_file_manager})
def iris_classify():
    k_means_iris()
