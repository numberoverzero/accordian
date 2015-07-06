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

print("\nTest async_util.Value")
signal = dispatch.Value(loop=loop, value=False)


async def iterate_values(values, fut):
    for value in values:
        signal.value = value
        print("Set signal to {}".format(value))
        await asyncio.sleep(0.5, loop=loop)
    fut.set_result(True)


async def print_when(value):
    print("Waiting for signal to reach {}".format(value))
    await signal.wait_for(value)
    print("Signal reached desired value {}".format(value))

complete = asyncio.Future(loop=loop)
loop.create_task(print_when("foo"))
loop.create_task(print_when(3))
loop.create_task(iterate_values([1, 2, 3, "foo", 4], complete))
loop.run_until_complete(complete)
print("Test complete")
