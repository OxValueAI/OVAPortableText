# Publishing Checklist

## Before release / 发布前检查

- [ ] confirm `pyproject.toml` name/version/author metadata
- [ ] replace repository URLs if needed
- [ ] run `pytest -q`
- [ ] run `python -m build`
- [ ] install the built wheel in a clean virtual environment
- [ ] verify README examples still run
- [ ] update `CHANGELOG.md`
- [ ] tag the release in Git

## Suggested release flow / 建议发布流程

```bash
python -m pip install --upgrade build twine
python -m pytest -q
python -m build
python -m venv .venv-publish-test
source .venv-publish-test/bin/activate
pip install dist/*.whl
python -c "import ova_portable_text; print(ova_portable_text.__version__)"
twine upload --repository testpypi dist/*
```

## Notes / 备注

- Use TestPyPI first.
- 先发 TestPyPI，再发正式 PyPI。
- Keep version bumps explicit and consistent.
- 版本号变更要明确且保持一致。
