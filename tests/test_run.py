import asyncio

import aio_background


async def test_should_stop(caplog):
    async def run() -> None:
        await asyncio.sleep(100500)

    token = aio_background.run(run)
    assert token.is_running

    await asyncio.sleep(0.5)

    assert await token.close()
    assert not token.is_running


async def test_should_not_stop(caplog):
    async def run() -> None:
        while True:
            try:
                await asyncio.sleep(100500)
            except asyncio.CancelledError:
                pass

    token = aio_background.run(run)
    assert token.is_running

    await asyncio.sleep(0.5)

    assert not await token.close(timeout=1)
    assert token.is_running


async def test_should_close_failed(caplog):
    async def run() -> None:
        raise RuntimeError("Failed")

    token = aio_background.run(run)
    assert token.is_running

    await asyncio.sleep(0.5)

    assert not token.is_running

    assert await token.close()
    assert not token.is_running

    assert ["Job unknown has stopped"] == [c.message for c in caplog.records if c.name == "aio_background"]


async def test_should_close_completed(caplog):
    async def run() -> None:
        return

    token = aio_background.run(run)
    assert token.is_running

    await asyncio.sleep(0.5)

    assert not token.is_running

    assert await token.close()
    assert not token.is_running

    assert ["Job unknown has stopped"] == [c.message for c in caplog.records if c.name == "aio_background"]
