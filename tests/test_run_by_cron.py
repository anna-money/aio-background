import asyncio
import logging

import aio_background

logger = logging.getLogger(__name__)


async def test_by_cron():
    class Task:
        def __init__(self):
            self.runs_count = 0

        async def run(self) -> None:
            self.runs_count += 1

    task = Task()
    token = aio_background.run_by_cron(task.run, cron_expr="* * * * * *", name="by_cron")

    await asyncio.sleep(5)

    assert await token.close()
    assert task.runs_count == 5
