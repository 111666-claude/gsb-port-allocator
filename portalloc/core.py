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
    k = owner + "|" + key
    if k in state["keys"]:
        return state["keys"][k]
    by_owner = state["by_owner"]
    if by_owner.get(owner, 0) >= state["quota"]:
        return "quota_exceeded"
    port = _next_free_port(state, counter)
    if port is None:
        return "exhausted"
    used = state["allocated"]
    used[str(port)] = {"owner": owner, "key": key}
    state["keys"][k] = port
    by_owner[owner] = by_owner.get(owner, 0) + 1
    return port


def _next_free_port(state, counter):
    """优先补回回收池里的端口，否则按游标在区间内取下一个。"""
    released = state["released"]
    while released:
        port = released.pop()
        counter.scanned += 1
        if str(port) not in state["allocated"]:
            return port
    for lo, hi in state["ranges"]:
        candidate = max(state["cursor"], lo)
        while candidate <= hi:
            counter.scanned += 1
            if str(candidate) not in state["allocated"]:
                state["cursor"] = candidate + 1
                return candidate
            candidate += 1
    return None


def free(state, port):
    """回收一个端口。"""
    used = state["allocated"]
    p = int(port)
    entry = used.pop(str(p), None)
    if entry is None:
        return False
    owner = entry["owner"]
    state["keys"].pop(owner + "|" + entry["key"], None)
    state["by_owner"][owner] = state["by_owner"].get(owner, 1) - 1
    state["released"].append(p)
    return True


def status(state):
    return {
        "allocated": len(state["allocated"]),
        "by_owner": dict(state["by_owner"]),
        "ranges": state["ranges"],
        "quota": state["quota"],
    }
