# accordian 0.2.1

[![Build Status]
(https://travis-ci.org/numberoverzero/accordian.svg?branch=master)]
(https://travis-ci.org/numberoverzero/accordian)[![Coverage Status]
(https://coveralls.io/repos/numberoverzero/accordian/badge.png?branch=master)]
(https://coveralls.io/r/numberoverzero/accordian?branch=master)

Downloads https://pypi.python.org/pypi/accordian

Source https://github.com/numberoverzero/accordian

Event dispatch in Python 3.5 using asyncio

# Installation

`pip install accordian`

# Getting Started

```python
import asyncio
import accordian
import random

loop = asyncio.new_event_loop()

dispatch = accordian.Dispatch(loop=loop)
dispatch.register("my_event", ["id", "value"])


@dispatch.on("my_event")
async def handle(id, value):
    sleep = 5.0 * random.random()
    print("Handling `my_event(id={})` in {} seconds.".format(id, sleep))
    await asyncio.sleep(sleep, loop=loop)
    print("`Completed my_event(id={})`!".format(id))


ids = range(4)
values = [random.random() for _ in ids]
for id, value in zip(ids, values):
    params = {"id": id, "value": value}
    dispatch.trigger("my_event", params)

loop.create_task(dispatch.start())
loop.run_until_complete(asyncio.sleep(0.01, loop=loop))
loop.run_until_complete(dispatch.stop())

```

# Contributing
Contributions welcome!  Please make sure `tox` passes (including flake8) before submitting a PR.

### Development
accordian uses `tox`, `pytest` and `flake8`.  To get everything set up:

```
# RECOMMENDED: create a virtualenv with:
#     mkvirtualenv accordian
git clone https://github.com/numberoverzero/accordian.git
pip install tox
tox
```

### TODO

* ?
