# pylint: disable=redefined-outer-name

from dagster.core.test_utils import instance_for_test, create_run_for_test, environ
from dagster.daemon.monitoring.monitoring_daemon import monitor_starting_run, monitor_started_run
from dagster.daemon import get_default_daemon_logger
from dagster.core.storage.pipeline_run import PipelineRunStatus

from dagster.core.events import DagsterEventType, DagsterEvent
from dagster.core.events.log import EventLogEntry
import logging
import time
from dagster.core.launcher import RunLauncher, CheckRunHealthResult, WorkerStatus
from dagster.serdes import ConfigurableClass
import pytest

import os


class TestRunLauncher(RunLauncher, ConfigurableClass):
    def __init__(self, inst_data=None):
        self._inst_data = inst_data
        super().__init__()

    @property
    def inst_data(self):
        return self._inst_data

    @classmethod
    def config_type(cls):
        return {}

    @staticmethod
    def from_config_value(inst_data, config_value):
        return TestRunLauncher(inst_data=inst_data)

    def launch_run(self, context):
        raise NotImplementedError()

    def join(self, timeout=30):
        pass

    def can_terminate(self, run_id):
        raise NotImplementedError()

    def terminate(self, run_id):
        raise NotImplementedError()

    def supports_check_run_health(self):
        return True

    def check_run_health(self, _run):
        return (
            CheckRunHealthResult(WorkerStatus.RUNNING, "")
            if os.environ.get("DAGSTER_TEST_RUN_HEALTH_CHECK_RESULT") == "healthy"
            else CheckRunHealthResult(WorkerStatus.NOT_FOUND, "")
        )


@pytest.fixture
def instance():
    with instance_for_test(
        overrides={
            "run_launcher": {
                "module": "dagster_tests.daemon_tests.test_monitoring_daemon",
                "class": "TestRunLauncher",
            },
        },
    ) as instance:
        yield instance


@pytest.fixture
def logger():
    return get_default_daemon_logger("MonitoringDaemon")


def report_starting_event(instance, run, timestamp):
    launch_started_event = DagsterEvent(
        event_type_value=DagsterEventType.PIPELINE_STARTING.value,
        pipeline_name=run.pipeline_name,
    )

    event_record = EventLogEntry(
        message="",
        user_message="",
        level=logging.INFO,
        pipeline_name=run.pipeline_name,
        run_id=run.run_id,
        error_info=None,
        timestamp=timestamp,
        dagster_event=launch_started_event,
    )

    instance.handle_new_event(event_record)


def test_monitor_starting(instance, logger):
    run = create_run_for_test(
        instance,
        pipeline_name="foo",
    )
    report_starting_event(instance, run, timestamp=time.time())
    monitor_starting_run(
        instance,
        instance.get_run_by_id(run.run_id),
        logger,
    )
    assert instance.get_run_by_id(run.run_id).status == PipelineRunStatus.STARTING

    run = create_run_for_test(instance, pipeline_name="foo")
    report_starting_event(instance, run, timestamp=time.time() - 1000)

    monitor_starting_run(
        instance,
        instance.get_run_by_id(run.run_id),
        logger,
    )
    assert instance.get_run_by_id(run.run_id).status == PipelineRunStatus.FAILURE


def test_monitor_started(instance, logger):
    with environ({"DAGSTER_TEST_RUN_HEALTH_CHECK_RESULT": "healthy"}):
        run = create_run_for_test(instance, pipeline_name="foo", status=PipelineRunStatus.STARTED)
        monitor_started_run(instance, run, logger)
        assert instance.get_run_by_id(run.run_id).status == PipelineRunStatus.STARTED

    monitor_started_run(instance, run, logger)
    assert instance.get_run_by_id(run.run_id).status == PipelineRunStatus.FAILURE
