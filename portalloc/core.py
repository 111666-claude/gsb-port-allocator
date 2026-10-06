"""端口台账的核心操作。"""

import json


class Counter:
    """记录分配过程中做过的比较次数。"""

    def __init__(self):
        self.scanned = 0


def new_state(ranges, quota):
    ranges = [list(r) for r in ranges]
    return {
        "ranges": ranges,
        "quota": quota,
        "cursor": ranges[0][0],
        "allocated": {},
        "keys": {},
        "by_owner": {},
        "released": [],
    }


def save(state, path):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=2)


def load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def alloc(state, owner, key, counter):
    """给 owner+key 分一个端口。"""
    used = state["allocated"]
    for _pstr in used:
        counter.scanned += 1
    port = state["cursor"]
    state["cursor"] = port + 1
    used[str(port)] = {"owner": owner, "key": key}
    state["keys"][owner + "|" + key] = port
    state["by_owner"][owner] = state["by_owner"].get(owner, 0) + 1
    return port


def free(state, port):
    """回收一个端口。"""
    used = state["allocated"]
    p = int(port)
    if str(p) in used:
        del used[str(p)]
        return True
    return False


def status(state):
    return {
        "allocated": len(state["allocated"]),
        "by_owner": dict(state["by_owner"]),
        "ranges": state["ranges"],
        "quota": state["quota"],
    }
