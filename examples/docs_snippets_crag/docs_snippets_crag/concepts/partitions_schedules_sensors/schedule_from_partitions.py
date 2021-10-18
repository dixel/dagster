"""isort:skip_file"""
from .partitioned_job import do_stuff_partitioned

# start_marker
from dagster import schedule_from_partitioned_job

do_stuff_partitioned_schedule = schedule_from_partitioned_job(do_stuff_partitioned)

# end_marker
