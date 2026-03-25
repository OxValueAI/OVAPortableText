# Publishing Checklist / 发布清单

This checklist is intended for manual release work.  
这份清单用于手动发布流程。

---

## 1. Before release / 发布前检查

- [ ] confirm `pyproject.toml` package metadata  
      确认 `pyproject.toml` 的包元数据
- [ ] confirm `src/ova_portable_text/version.py` matches the release version  
      确认 `src/ova_portable_text/version.py` 与待发布版本一致
- [ ] confirm root `CHANGELOG.md` exists and is updated  
      确认根目录 `CHANGELOG.md` 存在且已更新
- [ ] confirm docs are synced with the current package behavior  
      确认文档已与当前包行为同步
- [ ] run `pytest -q`  
      运行 `pytest -q`
- [ ] run `python -m build`  
      运行 `python -m build`
- [ ] inspect generated sdist and wheel filenames  
      检查生成的 sdist 和 wheel 文件名
- [ ] install the built wheel in a clean virtual environment  
      在干净虚拟环境中安装构建好的 wheel
- [ ] verify README and example snippets still run  
      确认 README 和示例代码片段仍可运行
- [ ] run `twine check dist/*`  
      运行 `twine check dist/*`

---

## 2. Suggested release flow / 建议发布流程

```bash
python -m pip install --upgrade build twine
python -m pytest -q
python -m build

twine check dist/*

python -m venv .venv-publish-test
source .venv-publish-test/bin/activate
pip install dist/*.whl
python -c "import ova_portable_text; print(ova_portable_text.__version__)"
python -c "from ova_portable_text import create_document; print(create_document(title='Smoke', language='en', documentType='valuationReport').meta.title)"

twine upload --repository testpypi dist/*
# After verifying TestPyPI, upload to the real PyPI repository.
```

---

## 3. Release policy for this repository / 本仓库的发布口径

At the moment, the package and the protocol evolve together.  
当前阶段，包与协议是同步演进的。

That means before release you should verify three kinds of alignment:  
这意味着发布前应同时核对三类对齐关系：

1. package code ↔ tests  
   包代码 ↔ 测试
2. package code ↔ examples  
   包代码 ↔ examples
3. package code ↔ current protocol document  
   包代码 ↔ 当前协议文档

---

## 4. Recommended sanity checks / 推荐额外自检

- Generate one realistic report JSON and keep it as a local release snapshot.  
  生成一份接近真实业务的报告 JSON，并作为本地发布快照保存。
- Run at least one example that uses registries and references.  
  至少跑一个同时使用 registry 与引用系统的示例。
- Run at least one example that uses `grid` tables.  
  至少跑一个使用 `grid` 表格的示例。
- Run at least one example that uses embedded image sources.  
  至少跑一个使用内嵌图片来源的示例。

---

## 5. Notes / 备注

- Use TestPyPI first when practical.  
  条件允许时，优先先发 TestPyPI。
- Keep version bumps explicit and consistent.  
  版本号变更要明确且一致。
- Treat `validate()` / `assert_valid()` as the final gate even if `strict_ids=True` is enabled.  
  即使启用了 `strict_ids=True`，仍应把 `validate()` / `assert_valid()` 作为最后一道闸门。
