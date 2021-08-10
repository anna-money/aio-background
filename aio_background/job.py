import abc
import asyncio
from typing import Collection


class Job(abc.ABC):
    __slots__ = ()

    @property
    @abc.abstractmethod
    def is_running(self) -> bool:
        ...

    @abc.abstractmethod
    async def close(self, *, timeout: float = 0.5) -> bool:
        ...


class SingleTaskJob(Job):
    __slots__ = ("_task",)

    def __init__(self, task: asyncio.Task[None]):
        self._task = task

    @property
    def is_running(self) -> bool:
        return not self._task.done()

    async def close(self, *, timeout: float = 0.5) -> bool:
        if self._task.done():
            return True

        self._task.cancel()
        await asyncio.wait({self._task}, timeout=timeout)
        return self._task.done()


class CombinedJob(Job):
    __slots__ = ("_jobs",)

    def __init__(self, jobs: Collection[Job]):
        self._jobs = jobs

    @property
    def is_running(self) -> bool:
        return all(job.is_running for job in self._jobs)

    async def close(self, *, timeout: float = 0.5) -> bool:
        tasks = [asyncio.create_task(job.close(timeout=timeout)) for job in self._jobs]
        closed = True
        for task in tasks:
            closed &= await task
        return closed
