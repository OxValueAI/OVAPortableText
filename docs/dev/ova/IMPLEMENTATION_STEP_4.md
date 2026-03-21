# OVAPortableText Step 4

## 本步目标

把当前包从“能生成协议 JSON”升级到“能做整份文档的结构化校验与全局引用解析”。

## 本步新增内容

1. `Document.build_resolver()`
2. `Document.validate()`
3. `Document.assert_valid()`
4. `DocumentResolver`
5. `ValidationReport / ValidationIssue / DocumentValidationError`
6. 协议建议的第一版自动校验规则

## 已实现的核心校验

- `schemaVersion` 必填检查
- 顶层 registry 存在性检查
- section 递归结构检查
- 子 section level = 父 level + 1 检查
- 全局重复 ID 检查
- `xref` 解析检查
- `citation_ref` 解析检查
- `footnote_ref` 解析检查
- `glossary_term` 解析检查
- `imageRef / chartRef / tableRef` 解析检查

## 主要新增文件

- `src/ova_portable_text/exceptions.py`
- `src/ova_portable_text/resolver.py`
- `src/ova_portable_text/validator.py`
- `examples/validation_report.py`
- `tests/test_validation_success.py`
- `tests/test_validation_failures.py`

## 使用方式示例

```python
validation = report.validate()
if not validation.isValid:
    for issue in validation.issues:
        print(issue.code, issue.path, issue.message)

report.assert_valid()
resolver = report.build_resolver()
```

## 设计说明

### 为什么要做全局 resolver

因为协议已经明确：所有可能被 `xref`、`citation_ref`、`footnote_ref`、目录、图表目录、书签等能力引用的对象，都应具备统一可解析目标模型。

### 为什么重复 ID 检查放在 validator 而不是构造器里

因为对象一般是逐步 append 进去的。等整份文档拼装完成后再做全局唯一性检查，更符合文档构建类库的使用习惯。

### 当前边界

本步还没有做：
- 目录自动生成
- 图表目录 / 表格目录输出
- 引文样式渲染
- 页码或 PDF 书签映射
- 更细的 anchor 冲突检查

这些后续都可以建立在当前 resolver / validator 之上继续扩展。
