import asyncio
import inspect
MISSING = object()
__all__ = ["RestartableTask", "Dispatch", "EventHandler"]
__version__ = "0.3.0"


class Event:
    """ Two-part event, can be started and completed. """
    def __init__(self, *, loop):
        self._start = asyncio.Event(loop=loop)
        self._complete = asyncio.Event(loop=loop)

    @property
    def started(self):  # pragma: no cover
        return self._start.is_set()

    @property
    def completed(self):  # pragma: no cover
        return self._complete.is_set()

    def start(self):
        self._start.set()

    def complete(self):
        self._complete.set()

    def clear(self):
        self._start.clear()
        self._complete.clear()

    async def wait(self):
        await self._start.wait()
        await self._complete.wait()


class RestartableTask:
    def __init__(self, *, loop):
        """
        RestartableTasks should call `await self._complete_shutdown()` when
        they have safely ended any running coroutines.
        """
        self.loop = loop
        self.running = False
        self._shutdown = Event(loop=self.loop)

    async def start(self):
        if self.running:
            return

        self.running = True
        self._shutdown.clear()
        self.loop.create_task(self._task())

    async def stop(self):
        if not self.running:
            return
        self.running = False

        # Kick off the shutdown process
        self._shutdown.start()
        await self._start_shutdown()

        # Wait for the _task and/or shutdown logic to gracefully shut down.
        await self._shutdown.wait()

    async def _task(self):
        pass

    async def _start_shutdown(self):
        pass

    async def _complete_shutdown(self):
        self._shutdown.complete()


class Dispatch(RestartableTask):
    """ Dispatch unpacked **kwargs to callbacks when events occur """
    def __init__(self, *, loop):
        super().__init__(loop=loop)
        self._handlers = {}
        self._queue = asyncio.Queue(loop=self.loop)
        self._resume_processing = asyncio.Event(loop=self.loop)

    def on(self, event):
        """
        Returns a wrapper for the given event.

        Usage:

            @dispatch.on("my_event")
            def handle_my_event(foo, bar, baz):
                ...

        """
        handler = self._handlers.get(event, None)
        if not handler:
            raise ValueError("Unknown event '{}'".format(event))
        return handler.register

    def register(self, event, keys):
        """
        Register a new event with available keys.
        Raises ValueError when the event has already been registered.

        Usage:

            dispatch.register("my_event", ["foo", "bar", "baz"])

        """
        if self.running:
            raise RuntimeError("Can't register while running")
        handler = self._handlers.get(event, None)
        if handler is not None:
            raise ValueError("Event {} already registered".format(event))
        self._handlers[event] = EventHandler(event, keys, loop=self.loop)

    def unregister(self, event):
        """
        Remove all registered handlers for an event.
        Silent return when event was not registered.

        Usage:

            dispatch.unregister("my_event")
            dispatch.unregister("my_event")  # no-op

        """
        if self.running:
            raise RuntimeError("Can't unregister while running")
        self._handlers.pop(event, None)

    async def trigger(self, event, kwargs):
        """ Enqueue an event for processing """
        await self._queue.put((event, kwargs))
        self._resume_processing.set()

    @property
    def events(self):
        """ Number of events currently enqueued """
        return self._queue.qsize()

    def clear(self):
        """ Clear any enqueued events """
        while self.events:
            self._queue.get_nowait()

    async def _task(self):
        """ Main queue processor """

        if self._handlers.values():
            start_tasks = [h.start() for h in self._handlers.values()]
            await asyncio.wait(start_tasks, loop=self.loop)

        while self.running:
            if self.events:
                event, kwargs = await self._queue.get()
                handler = self._handlers.get(event, None)
                if handler:
                    handler(kwargs)
            else:
                # Resume on either the next `trigger` call or a `stop`
                await self._resume_processing.wait()
                self._resume_processing.clear()

        # Give all the handlers a chance to complete their pending tasks
        tasks = [handler.stop() for handler in self._handlers.values()]
        if tasks:
            await asyncio.wait(tasks, loop=self.loop)

        # Let the shutdown process continue
        await self._complete_shutdown()

    async def _start_shutdown(self):
        # The processor is waiting, resume so it can exit cleanly
        self._resume_processing.set()
        await super()._start_shutdown()


class EventHandler(RestartableTask):

    def __init__(self, event, keys, *, loop):
        super().__init__(loop=loop)
        self.event = event
        self.keys = keys
        self._callbacks = []
        self._tasks = {}

    def __call__(self, kwargs):
        # Don't handle the call if we're shutting down
        if not self.running:
            raise RuntimeError(
                "EventHandler must be running to delegate events")

        filtered_kwargs = {}
        for key in self.keys:
            value = kwargs.get(key, MISSING)
            if value is not MISSING:
                filtered_kwargs[key] = value

        for callback in self._callbacks:
            task = self.loop.create_task(callback(filtered_kwargs))
            self._tasks[id(task)] = task
            task.add_done_callback(self._task_done)

    def _task_done(self, task):
        """
        When a callback is complete, remove it from the active task set.

        Don't raise if the task has already been removed
        """
        self._tasks.pop(id(task), None)

    def register(self, callback):
        wrapped = callback
        if not inspect.iscoroutinefunction(wrapped):
            wrapped = asyncio.coroutine(wrapped)
        self._callbacks.append(wrapped)
        # Always return the decorated function unchanged
        return callback

    async def _start_shutdown(self):
        # Give all active tasks a chance to complete
        active_tasks = list(self._tasks.values())
        if active_tasks:
            await asyncio.wait(active_tasks, loop=self.loop)
        await self._complete_shutdown()
