import abc
import asyncio


class Job(abc.ABC):
    __slots__ = ()

    @property
    @abc.abstractmethod
    def is_running(self) -> bool: ...

    @abc.abstractmethod
    async def close(self, *, timeout: float = 0.5) -> bool: ...


class SingleTaskJob(Job):
    __slots__ = ("__task",)

    def __init__(self, task: asyncio.Task[None]):
        self.__task = task

    @property
    def is_running(self) -> bool:
        return not self.__task.done()

    async def close(self, *, timeout: float = 0.5) -> bool:
        if self.__task.done():
            return True

        self.__task.cancel()
        await asyncio.wait({self.__task}, timeout=timeout)
        return self.__task.done()


class CombinedJob(Job):
    __slots__ = ("__jobs",)

    def __init__(self, jobs: tuple[Job, ...]):
        self.__jobs = jobs

    @property
    def is_running(self) -> bool:
        return all(job.is_running for job in self.__jobs)

    async def close(self, *, timeout: float = 0.5) -> bool:
        tasks = [asyncio.create_task(job.close(timeout=timeout)) for job in self.__jobs]
        closed = True
        for task in tasks:
            closed &= await task
        return closed
