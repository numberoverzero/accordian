import asyncio
import dispatch
import logging

logging.basicConfig(level=logging.DEBUG)

loop = asyncio.new_event_loop()
event = "my_event"
params = ["func", "args"]

dispatcher = dispatch.Dispatch(loop)
dispatcher.register(event, params)


def ncid():
    _cid = 0
    while True:
        yield _cid
        _cid += 1
cid = ncid()


def create_tasks():
    n = 2.0
    while n > 0:
        dispatcher.trigger(event, {"func": "f", "args": n})
        n -= 0.5


@dispatcher.on(event)
async def coro_handle(func, args):
    id = next(cid)
    space = int(2*id)
    print(" " * space + "{}: coro sleeping {} sec".format(id, args))
    await asyncio.sleep(args, loop=loop)
    print(" " * space + "{}: coro complete".format(id))


async def stop_loop():
    await asyncio.sleep(0.6, loop=loop)
    print("Try to stop")
    await dispatcher.stop()
    print("Stop successful")


async def single_dispatch_run():
    create_tasks()
    await dispatcher.start()
    await stop_loop()

print("\nTest dispatch.Dispatch")
# Make sure we can restart
print("\nFirst run")
loop.run_until_complete(single_dispatch_run())
print("\nSecond run")
loop.run_until_complete(single_dispatch_run())
print("Test complete")
