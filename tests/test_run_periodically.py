import asyncio
import logging

import aio_background

logger = logging.getLogger(__name__)


async def test_periodically():
    class Task:
        def __init__(self):
            self.runs_count = 0

        async def run(self) -> None:
            self.runs_count += 1

    task = Task()
    token = aio_background.run_periodically(task.run, 0.9, name="by_cron")

    await asyncio.sleep(5)

    assert await token.close()
    assert task.runs_count == 5
