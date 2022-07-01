import uuid
from typing import Any, AsyncIterator, Callable, Coroutine, Union

import aiohttp.web

from .job import Job

_KEY = f"{__package__}.{uuid.uuid4()}"


def setup_ctx(
    job_or_factory: Union[Job, Callable[[aiohttp.web.Application], Coroutine[Any, Any, Job]]],
    *,
    timeout: float = 0.5,
) -> Callable[[aiohttp.web.Application], AsyncIterator[None]]:
    async def setup(app: aiohttp.web.Application) -> AsyncIterator[None]:
        job = job_or_factory if isinstance(job_or_factory, Job) else await job_or_factory(app)
        if _KEY not in app:
            app[_KEY] = []
        app[_KEY].append(job)
        yield
        await job.close(timeout=timeout)

    return setup


def is_healthy(app: aiohttp.web.Application) -> bool:
    if _KEY not in app:
        return True

    return all(job.is_running for job in app[_KEY])
