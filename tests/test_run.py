import asyncio

import aio_background


async def test_should_stop(caplog):
    async def run() -> None:
        await asyncio.sleep(100500)

    token = aio_background.run(run, name="job")
    assert token.is_running

    await asyncio.sleep(0.5)

    assert await token.close()
    assert not token.is_running


async def test_should_not_stop(caplog):
    async def run() -> None:
        for x in range(3):
            try:
                await asyncio.sleep(0.5)
            except asyncio.CancelledError:
                pass

    token = aio_background.run(run, name="broken cancellation")
    assert token.is_running

    await asyncio.sleep(0.5)

    assert not await token.close(timeout=0.5)
    assert token.is_running

    assert await token.close(timeout=1)
    assert not token.is_running


async def test_should_close_failed(caplog):
    async def run() -> None:
        raise RuntimeError("Failed")

    token = aio_background.run(run, name="failed")
    assert token.is_running

    await asyncio.sleep(0.5)

    assert not token.is_running

    assert await token.close()
    assert not token.is_running

    assert ["Job failed has unexpectedly stopped"] == [c.message for c in caplog.records if c.name == "aio_background"]


async def test_should_close_completed(caplog):
    async def run() -> None:
        return

    token = aio_background.run(run, name="completed")
    assert token.is_running

    await asyncio.sleep(0.5)

    assert not token.is_running

    assert await token.close()
    assert not token.is_running

    assert ["Job completed has unexpectedly stopped"] == [
        c.message for c in caplog.records if c.name == "aio_background"
    ]
