# Validation and Resolver

## Validation

`Document.validate()` 会返回 `ValidationReport`。

你可以重点看：
- `isValid`
- `error_count`
- `warning_count`
- `issues`
- `to_text()`

```python
report = ...
validation = report.validate()
print(validation.to_text())
```

每条 issue 现在尽量会带这些上下文：
- `path`
- `sectionId`
- `sectionTitle`
- `contextType`
- `contextId`
- `contextAnchor`
- `suggestion`

这让你在维护大文档时，不必只靠一条 path 去反推到底是哪一个对象出了问题。

## Fail-fast mode

```python
report.assert_valid()
```

如果存在 `error`，会抛出 `DocumentValidationError`。

## Resolver

`Document.build_resolver()` 会返回全局 resolver，用于：
- 检查重复 id
- 检查重复 anchor
- 按语义 targetType + id 解析 `xref`
- 输出调试摘要

```python
resolver = report.build_resolver()
print(resolver.debug_summary())
```

你也可以按 id / anchor 直接查：

```python
resolver.get("sec-1")
resolver.get_by_anchor("sec-1")
resolver.resolve_xref(target_type="section", target_id="sec-1")
```
