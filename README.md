# Dispatch 0.2.0

[![Build Status]
(https://travis-ci.org/numberoverzero/dispatch.svg?branch=master)]
(https://travis-ci.org/numberoverzero/dispatch)[![Coverage Status]
(https://coveralls.io/repos/numberoverzero/dispatch/badge.png?branch=master)]
(https://coveralls.io/r/numberoverzero/dispatch?branch=master)

Downloads https://pypi.python.org/pypi/dispatch

Source https://github.com/numberoverzero/dispatch

Event dispatch in Python 3.5 using asyncio

# Installation

`pip install dispatch`

# Getting Started

```python
import asyncio
import dispatch
import random

loop = asyncio.new_event_loop()
dispatcher = dispatch.Dispatch(loop=loop)

dispatcher.register("my_event", ["id", "value"])


@dispatcher.on("my_event")
async def handle(id, value):
    sleep = 5.0 * random.random()
    print("Handling `my_event(id={})` in {} seconds.".format(id, sleep))
    await asyncio.sleep(sleep, loop=loop)
    print("`Completed my_event(id={})`!".format(id))


ids = range(4)
values = [random.random() for _ in ids]
for id, value in zip(ids, values):
    params = {"id": id, "value": value}
    dispatcher.trigger("my_event", params)

loop.create_task(dispatcher.start())
loop.run_until_complete(asyncio.sleep(0.01, loop=loop))
loop.run_until_complete(dispatcher.stop())

```

# Contributing
Contributions welcome!  Please make sure `tox` passes (including flake8) before submitting a PR.

### Development
dispatch uses `tox`, `pytest` and `flake8`.  To get everything set up:

```
# RECOMMENDED: create a virtualenv with:
#     mkvirtualenv dispatch
git clone https://github.com/numberoverzero/dispatch.git
pip install tox
tox
```

### TODO

* ?
