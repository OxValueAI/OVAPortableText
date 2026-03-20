# Test Matrix

当前测试大致覆盖这些层次：

## 1. Skeleton / 骨架层
- minimal document export
- section / subsection structure

## 2. Text / 文本层
- styles
- marks / markDefs
- lists
- inline objects

## 3. Block objects / 对象层
- image / chart / table / math_block / callout

## 4. Registry / registry 层
- images / logos / backgrounds / icons / attachments
- tables / charts / metrics
- bibliography / footnotes / glossary

## 5. Validation / 校验层
- success case
- failure cases
- mark resolution
- xref / citation / footnote / glossary resolution
- duplicate ids / duplicate anchors
- issue context output

## 6. Round-trip / 回读层
- `to_dict()` + `from_dict()`
- `to_json()` + `from_json()`

## 7. Builder ergonomics / builder 手感层
- append-style authoring
- numbering helpers
- combined end-to-end authoring examples
