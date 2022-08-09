import asyncio
import datetime
import logging
import random
import time
from typing import Any, Callable, Coroutine

import croniter

from .job import CombinedJob, Job, SingleTaskJob

logger = logging.getLogger(__package__)


def run(func: Callable[[], Coroutine[Any, Any, None]], *, name: str = "unknown") -> Job:
    def report_if_not_cancelled(t: asyncio.Task[None]) -> None:
        if t.cancelled():
            return

        logger.exception("Job %s has unexpectedly stopped", name, exc_info=t.exception())

    task = asyncio.create_task(func(), name=f"{__package__}.{name}")
    task.add_done_callback(report_if_not_cancelled)
    return SingleTaskJob(task)


def run_by_cron(
    func: Callable[[], Coroutine[Any, Any, None]],
    *,
    cron_expr: str,
    name: str = "unknown",
    suppress_exception: bool = True,
) -> Job:
    cron = croniter.croniter(expr_format=cron_expr, start_time=datetime.datetime.now(datetime.timezone.utc))

    async def by_cron() -> None:
        attempt = 0
        for next_start_at in cron:
            await asyncio.sleep(next_start_at - time.time())

            try:
                # to have independent async context per run
                # to protect from misuse of contextvars
                await asyncio.create_task(func(), name=f"{__package__}.{name}.{attempt}")
            except Exception:
                if not suppress_exception:
                    raise

                logger.exception("Job %s has got unexpected exception", name)

            attempt += 1

    return run(by_cron, name=name)


def run_periodically(
    func: Callable[[], Coroutine[Any, Any, None]],
    *,
    period: float,
    name: str = "unknown",
    suppress_exception: bool = True,
) -> Job:
    if period <= 0:
        raise RuntimeError("Period should be positive")

    async def periodically() -> None:
        # to de-synchronize jobs started at the same time
        await asyncio.sleep(period * random.random())

        attempt = 0
        while True:
            try:
                # to have independent async context per run
                # to protect from misuse of contextvars
                await asyncio.create_task(func(), name=f"{__package__}.{name}.{attempt}")
            except Exception:
                if not suppress_exception:
                    raise

                logger.exception("Job %s has got unexpected exception", name)

            attempt += 1

            await asyncio.sleep(period)

    return run(periodically, name=name)


def combine(*jobs: Job) -> Job:
    return CombinedJob(jobs)
