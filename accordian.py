import asyncio
from typing import Callable, List, Optional, Set

__all__ = ["Namespace", "Signal", "signal"]
__version__ = "0.4.0"


class Signal:
    def __init__(self, name: str = None) -> None:
        self.name: Optional[str] = name
        self.receivers: List[Callable] = []

    def connect(self, fn: Callable) -> Callable:
        if not asyncio.iscoroutinefunction(fn):
            raise ValueError(f"Signal.connect requires a coroutine function but got {fn}")
        if fn not in self.receivers:
            self.receivers.append(fn)
        return fn

    def send(self, *recv_args, **recv_kwargs) -> Set[asyncio.Task]:
        tasks = set()
        for recv in self.receivers:
            coro = recv(*recv_args, **recv_kwargs)
            task = asyncio.create_task(coro)
            tasks.add(task)
        return tasks

    async def join(self, *args, **kwargs) -> List:
        tasks = self.send(*args, **kwargs)
        if not tasks:
            return []
        done, pending = await asyncio.wait(tasks)
        return [o.result() for o in done]


class Namespace:
    def __init__(self) -> None:
        self.signals = {}

    def signal(self, name: str = None) -> Signal:
        s = self.signals.get(name)
        if not s:
            s = self.signals[name] = Signal(name=name)
        return s


_global = Namespace()
signal = _global.signal
