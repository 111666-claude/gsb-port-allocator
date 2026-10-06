"""命令行入口。"""

import argparse

from . import core, samples


def _parse_range(text):
    lo, hi = text.split("-", 1)
    return [int(lo), int(hi)]


def main(argv=None):
    ap = argparse.ArgumentParser(prog="portalloc")
    sub = ap.add_subparsers(dest="cmd")

    p_init = sub.add_parser("init")
    p_init.add_argument("--state", required=True)
    p_init.add_argument("--range", action="append", required=True)
    p_init.add_argument("--quota", type=int, required=True)

    p_alloc = sub.add_parser("alloc")
    p_alloc.add_argument("--state", required=True)
    p_alloc.add_argument("--owner", required=True)
    p_alloc.add_argument("--key", required=True)

    p_free = sub.add_parser("free")
    p_free.add_argument("--state", required=True)
    p_free.add_argument("--port", required=True)

    p_status = sub.add_parser("status")
    p_status.add_argument("--state", required=True)

    p_demo = sub.add_parser("demo")
    p_demo.add_argument("--name", required=True)

    args = ap.parse_args(argv)

    if args.cmd == "init":
        state = core.new_state([_parse_range(r) for r in args.range], args.quota)
        core.save(state, args.state)
        print(state["ranges"])
        return 0
    if args.cmd == "alloc":
        state = core.load(args.state)
        port = core.alloc(state, args.owner, args.key, core.Counter())
        core.save(state, args.state)
        print(port)
        return 0
    if args.cmd == "free":
        state = core.load(args.state)
        ok = core.free(state, args.port)
        core.save(state, args.state)
        print("freed" if ok else "not-found")
        return 0
    if args.cmd == "status":
        print(core.status(core.load(args.state)))
        return 0
    if args.cmd == "demo":
        return samples.run(args.name)

    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
