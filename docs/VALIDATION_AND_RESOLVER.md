# Validation and Resolver / 校验与解析器

Validation and resolver functionality are the two most important debugging layers in OVAPortableText.  
校验器与解析器是 OVAPortableText 中最重要的两层调试基础设施。

---

## 1. Validation / 校验

### 1.1 `Document.validate()`

```python
validation = report.validate()
print(validation.to_text())
```

`Document.validate()` returns a structured `ValidationReport`.  
`Document.validate()` 会返回结构化的 `ValidationReport`。

Useful fields / 常用字段：

- `isValid`
- `error_count`
- `warning_count`
- `issues`
- `to_text()`

### 1.2 Why use `validate()` during development / 为什么开发阶段要反复调用 `validate()`

Use it when you want to:  
适合以下场景：

- inspect multiple issues at once  
  一次查看多个问题
- keep working even when the document is not yet valid  
  在文档尚未完全合法时继续调试
- show a report to another developer or renderer implementer  
  给其他开发或渲染器实现方查看问题报告

### 1.3 Issue context / issue 上下文

Validation issues try to carry context such as:  
每条 issue 尽量携带以下上下文：

- `path`
- `sectionId`
- `sectionTitle`
- `contextType`
- `contextId`
- `contextAnchor`
- `suggestion`

This is especially useful when the document becomes large.  
当文档很大时，这一点尤其有帮助。

---

## 2. Fail-fast mode / 强制失败模式

```python
report.assert_valid()
```

`assert_valid()` raises `DocumentValidationError` if the report contains errors.  
如果文档存在错误，`assert_valid()` 会抛出 `DocumentValidationError`。

Use it when / 适用场景：

- you are about to export JSON for handoff  
  即将导出 JSON 交给下游
- you want CI to fail immediately  
  希望 CI 立即失败
- you treat validation as a release gate  
  把校验当成发布闸门

---

## 3. Resolver / 解析器

### 3.1 Build a resolver / 构建 resolver

```python
resolver = report.build_resolver()
print(resolver.debug_summary())
```

The resolver is the document-wide index of globally addressable targets.  
resolver 是对整份文档中“全局可寻址目标”的统一索引。

### 3.2 What the resolver helps with / resolver 能帮你做什么

- duplicate ID detection  
  检查重复 ID
- duplicate anchor detection  
  检查重复 anchor
- `xref` resolution  
  解析 `xref`
- registry target lookup  
  查 registry 目标
- debugging what is globally visible in the document  
  调试文档里哪些对象在全局可见

### 3.3 Common resolver calls / 常用 resolver 调用

```python
resolver.get("sec-1")
resolver.get_by_id("sec-1")
resolver.get_by_anchor("sec-1")
resolver.resolve_xref(target_type="section", target_id="sec-1")
```

---

## 4. How validation and resolver complement each other / 校验器与解析器如何配合

Use the resolver when you need to understand *what exists*.  
当你想知道“文档里到底有什么”时，用 resolver。

Use validation when you need to understand *what is wrong*.  
当你想知道“哪里不合法”时，用 validation。

Typical workflow / 典型流程：

1. build the document  
   构建文档
2. call `validate()`  
   调用 `validate()`
3. if references look suspicious, inspect with `build_resolver()`  
   如果引用看起来有问题，再用 `build_resolver()` 深挖
4. fix issues  
   修复问题
5. call `assert_valid()` before export  
   导出前调用 `assert_valid()`
