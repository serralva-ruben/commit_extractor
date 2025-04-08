import orjson, dataclasses

with open("nvd.ndjson", "rb") as f:
    data = orjson.loads(f)

    for line in data:
        print(line)