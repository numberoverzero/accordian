import asyncio
import dispatch
import logging

logging.basicConfig(level=logging.DEBUG)

loop = asyncio.new_event_loop()
event = "my_event"
params = ["func", "args"]

dispatch = dispatch.Dispatch(loop)
dispatch.register(event, params)


def ncid():
    _cid = 0
    while True:
        yield _cid
        _cid += 1
cid = ncid()


def create_tasks():
    n = 4
    while n > 0:
        dispatch.trigger(event, {"func": "f", "args": int(n)})
        n -= 1


@dispatch.on(event)
async def coro_handle(func, args):
    id = next(cid)
    print(" "*id + "{}: coro sleeping {} sec".format(id, args))
    await asyncio.sleep(args, loop=loop)
    print(" "*id + "{}: coro complete".format(id))


async def stop_loop():
    await asyncio.sleep(2.5, loop=loop)
    print("Try to stop")
    await dispatch.stop()
    print("Stop successful")


async def single_dispatch_run():
    create_tasks()
    await dispatch.start()
    await stop_loop()

# Make sure we can restart
print("\nFirst run")
loop.run_until_complete(single_dispatch_run())
print("\nSecond run")
loop.run_until_complete(single_dispatch_run())
print("Test complete")
