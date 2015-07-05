import asyncio
import dispatch

loop = asyncio.new_event_loop()
event = "command"
params = ["func", "args"]

dispatch = dispatch.Dispatch(loop)
dispatch.register(event, params)


def ncid():
    _cid = 0
    while True:
        yield _cid
        _cid += 1
cid = ncid()


@dispatch.on("command")
async def coro_handle(func, args):
    id = next(cid)
    print(" "*id + "{}: coro sleeping {} sec".format(id, args))
    await asyncio.sleep(args, loop=loop)
    print(" "*id + "{}: coro complete".format(id))

n = 4
while n > 0:
    dispatch.trigger("command", {"func": "f", "args": int(n)})
    n -= 1


async def stop_loop():
    await asyncio.sleep(2.5, loop=loop)
    print("Try to stop")
    await dispatch.stop()
    print("Stop successful")


dispatch.start()
loop.run_until_complete(stop_loop())
