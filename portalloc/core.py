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
    keys = state["keys"]
    k = owner + "|" + key
    if k in keys:
        return keys[k]
    used_by_owner = state["by_owner"].get(owner, 0)
    if used_by_owner >= state["quota"]:
        return "quota_exceeded"
    released = state["released"]
    if released:
        port = released.pop()
    else:
        port = _next_fresh(state, counter)
        if port is None:
            return "exhausted"
    state["allocated"][str(port)] = {"owner": owner, "key": key}
    keys[k] = port
    state["by_owner"][owner] = used_by_owner + 1
    return port


def _next_fresh(state, counter):
    """按 cursor 在声明的区间里取下一个未用过的端口。"""
    cursor = state["cursor"]
    for lo, hi in state["ranges"]:
        counter.scanned += 1
        if cursor < lo:
            cursor = lo
        if cursor <= hi:
            state["cursor"] = cursor + 1
            return cursor
    return None


def free(state, port):
    """回收一个端口。"""
    used = state["allocated"]
    p = int(port)
    pstr = str(p)
    if pstr in used:
        entry = used.pop(pstr)
        owner = entry["owner"]
        state["keys"].pop(owner + "|" + entry["key"], None)
        state["by_owner"][owner] = state["by_owner"].get(owner, 1) - 1
        state["released"].append(p)
        return True
    return False


def status(state):
    return {
        "allocated": len(state["allocated"]),
        "by_owner": dict(state["by_owner"]),
        "ranges": state["ranges"],
        "quota": state["quota"],
    }
