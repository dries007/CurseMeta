# Notes

A (partial) history of CurseMeta sits in [this](https://gist.github.com/dries007/10d8dc05a6fc5d1e700404cdd4446d21) gist.

## Software

- For the love of god use a decent IDE/editor, for example: `Pycharm`
- `Redis Desktop Manager` is also a good took to have around. 

## Decompiler helpers

### C# data class to list of members with types: 

```regexp
\s+\[DataMember\]\n\s+\w+ ([\w<>]+) (\w+)\s+\{([^\[]*\s?)*\}
```
```regexp
$2: $1\n
```

## Redis

- Cleaning a redis completely: `flushall`
- Cleaning only 1 db: `select <DB>` and `flushdb`

Useful when celery task que explodes because of oversight/bug.
