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
def dispatch(loop):
    return accordian.Dispatch(loop=loop)


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
            await self._complete_shutdown()

        async def _complete_shutdown(self):
            self.calls.append("complete shutdown")
            await super()._complete_shutdown()
    return BasicTask
