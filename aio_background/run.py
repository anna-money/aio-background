import asyncio
import datetime
import logging
import time
from typing import Awaitable, Callable

import croniter  # type: ignore

from .job import Job

logger = logging.getLogger(__package__)


def run(func: Callable[[], Awaitable[None]], *, name: str = "unknown") -> Job:
    def report_completion(t: asyncio.Task[None]) -> None:
        if t.cancelled():
            return

        logger.exception("Job %s has stopped", t.get_name(), exc_info=t.exception())

    task = asyncio.create_task(func(), name=name)
    task.add_done_callback(report_completion)
    return Job(task)


def run_by_cron(
    func: Callable[[], Awaitable[None]],
    spec: str,
    *,
    name: str = "unknown",
    suppress_exception: bool = True,
) -> Job:
    cron = croniter.croniter(expr_format=spec, start_time=datetime.datetime.now(datetime.timezone.utc))

    async def by_cron() -> None:
        for next_start_at in cron:
            await asyncio.sleep(next_start_at - time.time())

            try:
                await func()
            except Exception:
                if not suppress_exception:
                    raise

                logger.exception("Job %s has got unexpected exception", name)

    return run(by_cron, name=name)
