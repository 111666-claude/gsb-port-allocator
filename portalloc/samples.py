"""固定场景，用来复现题面里的锚点。"""

import json
import os
import tempfile

from . import core


def _line(obj):
    print(json.dumps(obj, ensure_ascii=False))


def _tmp():
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    return path


def _alloc(state, owner, key, counter):
    return core.alloc(state, owner, key, counter)


def run(name):
    if name == "range":
        state = core.new_state([[8000, 8002]], 10)
        counter = core.Counter()
        ports = [_alloc(state, "b", "k%d" % i, counter) for i in range(1, 5)]
        _line({"ports": ports})
        return 0
    if name == "reuse":
        state = core.new_state([[8000, 8002]], 5)
        counter = core.Counter()
        p1 = core.alloc(state, "a", "k1", counter)
        core.free(state, p1)
        p2 = core.alloc(state, "a", "k2", counter)
        _line({"ports": [p1, p2]})
        return 0
    if name == "dupkey":
        state = core.new_state([[8000, 8002]], 5)
        counter = core.Counter()
        p1 = core.alloc(state, "a", "k1", counter)
        p2 = core.alloc(state, "a", "k1", counter)
        _line({"ports": [p1, p2], "owner_used": state["by_owner"].get("a", 0)})
        return 0
    if name == "quota":
        state = core.new_state([[9000, 9009]], 2)
        counter = core.Counter()
        results = [_alloc(state, "a", "k%d" % i, counter) for i in range(1, 4)]
        _line({"results": results})
        return 0
    if name == "work":
        state = core.new_state([[10000, 12999]], 5000)
        counter = core.Counter()
        for i in range(2000):
            core.alloc(state, "svc", "k%04d" % i, counter)
        _line({"allocs": 2000, "scanned": counter.scanned})
        return 0
    raise SystemExit("未知场景：" + name)
