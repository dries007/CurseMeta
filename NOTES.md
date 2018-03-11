# Notes

## Decompiler helpers

### C# data class to list of members with types: 

```regexp
\s+\[DataMember\]\n\s+\w+ ([\w<>]+) (\w+)\s+\{([^\[]*\s?)*\}
```
```regexp
$2: $1\n
```
