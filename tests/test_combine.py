import asyncio

import aio_background


async def test_combine() -> None:
    async def long_job() -> None:
        await asyncio.sleep(100500)

    job = aio_background.combine(
        aio_background.run(long_job),
        aio_background.run(long_job),
    )
    await asyncio.sleep(0.5)
    assert await job.close()
    assert not job.is_running
