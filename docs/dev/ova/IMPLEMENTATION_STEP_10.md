# OVAPortableText – Step 10

## 本步目标 / Goal of this step

本步正式进入“回测准备”阶段：

1. 不再大幅扩张协议字段范围
2. 优先补强真实使用时最容易需要的能力
3. 继续完善文档、样例、测试和发布前自查

本步仍然遵循 Report Profile v1.0 当前边界：
- 章节树优先
- 标题文本与结构编号分离
- 可被引用对象应统一可解析
- `theme` 仍是轻量占位
- `datasets.charts` 当前正式细化仍以 `pie` 为主

---

## 本步新增内容 / What was added

### 1. 文件级 round-trip 能力

在 `OvaBaseModel` 层新增：

- `save_json(path, ...)`
- `load_json(path, ...)`

这样你现在可以直接：

```python
report.save_json("build/report.json")
restored = Document.load_json("build/report.json")
```

这对后续人工回测、Java 对接、保留失败样例、做 JSON 快照回归非常实用。

---

### 2. Section 批量 helper

为了让日常写法更顺手，`Section` 新增：

- `append_paragraphs(*paragraphs)`
- `append_bullet_items(*items, level=1)`
- `append_number_items(*items, level=1)`

这样你把已有文本数组迁移到协议对象时会更省手。

---

### 3. 更适合下一轮真实试用的文档

新增文档：

- `docs/REAL_WORLD_RECIPES.md`
- `docs/USER_TESTING_CHECKLIST.md`
- `docs/PROTOCOL_ALIGNMENT.md`

并同步更新：

- `README.md`
- `docs/API_REFERENCE.md`

这些文档会更贴近“你下一轮如何真的用它造报告并找问题”。

---

### 4. 新增样例

新增样例：

- `examples/save_and_load_json_demo.py`
- `examples/patent_valuation_style_report.py`

其中第二个样例更接近真实业务报告形态，包含：
- meta
- image registry
- table dataset
- pie chart dataset
- bibliography / footnote / glossary
- sections / subsection
- xref
- caption 相邻写法

---

### 5. 新增测试

新增测试：

- `tests/test_file_io_roundtrip.py`
- `tests/test_section_batch_helpers.py`
- `tests/test_examples_smoke.py`

其中 `test_examples_smoke.py` 会真实运行若干示例脚本，而不是只做静态检查。

---

## 本步验证结果 / Verification results

### 1. 单元测试

```bash
pytest -q
```

结果：

- **33 passed**

### 2. 构建验证

```bash
python -m build
```

结果：

- `ovaportabletext-0.1.1.tar.gz`
- `ovaportabletext-0.1.1-py3-none-any.whl`

构建成功。

### 3. 干净环境安装验证

已额外执行：

- 新建虚拟环境
- 安装构建出的 wheel
- 实际导入包
- 创建文档
- 调用 `append_paragraphs()`
- 调用 `validate()`
- 调用 `save_json()` / `Document.load_json()`

验证通过。

---

## 这一版最值得你先看的内容 / What to review first

建议优先看：

1. `src/ova_portable_text/base.py`
2. `src/ova_portable_text/section.py`
3. `README.md`
4. `docs/USER_TESTING_CHECKLIST.md`
5. `examples/patent_valuation_style_report.py`
6. `examples/save_and_load_json_demo.py`

---

## 我建议你下一轮回测时重点看什么 / Suggested focus for your next testing round

1. API 手感是否足够自然
2. 你是否还会频繁想退回手拼 dict
3. 导出的 JSON 是否和你脑中的协议结构一致
4. 校验输出是否足够容易定位问题
5. 真实业务报告是否还缺少高频 helper

---

## 下一步建议 / Suggested next step

下一步建议正式进入：

**你用真实业务样例做回测 → 我根据反馈集中修 bug / 补 helper / 微调文档 → 再准备最终 TestPyPI / PyPI 发布。**
