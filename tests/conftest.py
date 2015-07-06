import asyncio
import pytest


@pytest.fixture
def loop():
    '''
    Keep things clean by using a new event loop
    '''
    return asyncio.new_event_loop()


@pytest.fixture
def run(loop):
    '''
    Run a coro until it completes.
    Returns result from coro, if it produces one.
    '''
    def run_in_loop(coro):
        # For more details on what's going on:
        # https://docs.python.org/3/library/asyncio-task.html\
        #       #example-future-with-run-until-complete
        async def capture_return(future):
            ''' Push coro result into future for return '''
            future.set_result(await coro)
        # Kick off the coro, wrapped in the future above
        future = asyncio.Future(loop=loop)
        loop.create_task(capture_return(future))

        # Block until coro completes and dumps return in future
        loop.run_until_complete(future)

        # Hand result back
        return future.result()
    return run_in_loop
