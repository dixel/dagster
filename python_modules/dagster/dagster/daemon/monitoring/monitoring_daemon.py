from dagster.core.storage.pipeline_run import (
    PipelineRunStatus,
    PipelineRunsFilter,
    IN_PROGRESS_RUN_STATUSES,
)
from dagster import check, DagsterInstance
from dagster.core.launcher import WorkerStatus
import time


LAUNCH_TIMEOUT_SECONDS = 60


def monitor_starting_run(instance: DagsterInstance, run, logger):
    check.invariant(run.status == PipelineRunStatus.STARTING)
    run_stats = instance.get_run_stats(run.run_id)

    check.invariant(
        run_stats.launch_time is not None, "Pipeline in status STARTING doesn't have a launch time."
    )
    if time.time() - run_stats.launch_time >= LAUNCH_TIMEOUT_SECONDS:
        msg = (
            f"Run {run.run_id} has been running for {time.time() - run_stats.launch_time} seconds, "
            f"which is longer than the timeout of {LAUNCH_TIMEOUT_SECONDS} seconds to start. "
            f"Marking run {run.run_id} failed"
        )
        logger.info(msg)
        instance.report_run_failed(run, msg)


def monitor_started_run(instance, run, logger):
    check.invariant(run.status == PipelineRunStatus.STARTED)
    check_health_result = instance.run_launcher.check_run_health(run)
    if check_health_result.status != WorkerStatus.RUNNING:
        # final check to avoid a race condition where the run just finished
        if instance.get_run_by_id(run.run_id).status == PipelineRunStatus.STARTED:
            msg = (
                f"Run worker for {run.run_id} failed its health check."
                f"Marking run {run.run_id} failed. Run worker status is {check_health_result}"
            )
            logger.info(msg)
            instance.report_run_failed(run, msg)


def execute_monitoring_iteration(instance, _workspace, logger, _debug_crash_flags=None):
    check.invariant(
        instance.run_launcher.supports_check_run_health, "Must use a supported run launcher"
    )

    # TODO: consider limiting number of runs to fetch
    runs = instance.get_runs(filters=PipelineRunsFilter(statuses=IN_PROGRESS_RUN_STATUSES))

    logger.info(f"Collected {len(runs)} runs for monitoring")

    for run in runs:
        logger.info(f"Checking run {run.run_id}")

        if run.status == PipelineRunStatus.STARTING:
            monitor_starting_run(instance, run, logger)
        elif run.status == PipelineRunStatus.STARTED:
            monitor_started_run(instance, run, logger)
        elif run.status == PipelineRunStatus.CANCELING:
            pass
        else:
            check.invariant(False, f"Unexpected run status: {run.status}")
        yield
