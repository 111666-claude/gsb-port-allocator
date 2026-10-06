# port-allocator

从若干端口区间里按 owner 分配、回收端口，状态落在一个 JSON 文件里。只用 Python 标准库。

```
python3 -m unittest discover -s tests
python3 -m portalloc init --state s.json --range 8000-8002 --quota 2
python3 -m portalloc alloc --state s.json --owner a --key k1
python3 -m portalloc free --state s.json --port 8000
python3 -m portalloc status --state s.json
python3 -m portalloc demo --name reuse
```

## 口径

- **区间**：端口只能从声明的区间里取；区间之外、区间之间都不能分配。
- **配额**：同一个 owner 同时持有的端口数不超过 `quota`。
- **回收**：`free` 掉的端口回到可分配池，后续分配要能补上它。
- **幂等**：同一 `owner` + `key` 重复 `alloc` 返回同一个端口，且不重复占配额。

## 不变量

- 已分配端口的 owner 同时持有数之和等于台账条数，任一 owner 不超过 `quota`。
- 一个端口同时只属于一个 `owner`+`key`。
- `scanned` 不随分配次数平方级放大：两千次分配的 `scanned` 不超过 6000。

## 输出契约

`alloc` 成功打印端口号，失败打印 `exhausted`（区间内无可用）或 `quota_exceeded`（配额用尽）。
`demo --name=...` 打印一行 JSON 汇总，字段随场景而定，常见的有 `ports` / `results` / `owner_used` / `scanned`。
状态文件键固定为 `ranges` / `quota` / `cursor` / `allocated` / `keys` / `by_owner` / `released`。
