import accordian
import asyncio
import pytest


@pytest.fixture
def loop():
    '''
    Keep things clean by using a new event loop
    '''
    loop = asyncio.new_event_loop()
    loop.set_debug(True)
    return loop


@pytest.fixture
def BasicTask():
    ''' Keeps track of start, shutdown calls '''

    class BasicTask(accordian.RestartableTask):
        def __init__(self, *, loop):
            self.calls = []
            super().__init__(loop=loop)

        async def start(self):
            self.calls.append("start")
            await super().start()

        async def _start_shutdown(self):
            self.calls.append("start shutdown")
            await super()._start_shutdown()
            await self._finish_shutdown()

        async def _finish_shutdown(self):
            self.calls.append("finish shutdown")
            await super()._finish_shutdown()
    return BasicTask
