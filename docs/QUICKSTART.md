# OVAPortableText Quick Start

## What this package does

OVAPortableText 用来在 Python 中生成符合 **Report Profile v1.0** 的 JSON 文档。
它不是 PDF 渲染器，而是协议生成器、校验器和调试辅助工具。

## Smallest workflow

```python
from ova_portable_text import create_document

report = create_document(title="Quick Start", language="en")
sec = report.new_section(id="sec-1", level=1, title="Introduction")
sec.append_paragraph("Hello OVAPortableText.")

report.assert_valid()
print(report.to_json())
```

## Recommended writing style

推荐使用这种写法：

1. 先创建一个 `Document`
2. 通过 `new_section()` / `append_section()` 增加章节
3. 在 `Section` 上调用 `append_paragraph()`、`append_image()`、`append_table()` 等方法
4. 最后调用 `validate()` 或 `assert_valid()`

## Round-trip

```python
json_text = report.to_json()
restored = report.__class__.from_json(json_text)
print(restored.meta.title)
```


## Packaging sanity check / 打包自检

Before publishing, run a clean wheel install once.
正式发布前，建议至少做一次干净环境的 wheel 安装自检。
