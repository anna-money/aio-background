import asyncio


class Job:
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
