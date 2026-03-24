# Publishing Checklist

## Before release / 发布前检查

- [ ] confirm `pyproject.toml` package metadata
- [ ] confirm `src/ova_portable_text/version.py` matches the release version
- [ ] confirm root `CHANGELOG.md` exists and is updated
- [ ] confirm `docs/dev/ova/CHANGELOG.md` is synced if you keep both copies
- [ ] replace repository URLs if needed
- [ ] run `pytest -q`
- [ ] run `python -m build`
- [ ] inspect the generated sdist and wheel filenames
- [ ] verify root `CHANGELOG.md` is included in the sdist
- [ ] install the built wheel in a clean virtual environment
- [ ] verify README examples still run
- [ ] tag the release in Git

## Suggested release flow / 建议发布流程

```bash
python -m pip install --upgrade build twine
python -m pytest -q
python -m build

# Optional: inspect the build artifacts
ls -lh dist/

tar -tf dist/ovaportabletext-*.tar.gz | grep CHANGELOG

python -m venv .venv-publish-test
source .venv-publish-test/bin/activate
pip install dist/*.whl
python -c "import ova_portable_text; print(ova_portable_text.__version__)"
python -c "from ova_portable_text import create_document; print(create_document(title='Smoke', language='en').meta.title)"

twine check dist/*
twine upload --repository testpypi dist/*
# After verifying TestPyPI, upload to the real PyPI repository.
```

## Release notes for 0.1.2 / 0.1.2 发布重点

- packaging metadata and changelog layout were aligned for release
- `Section.numbering` is now restricted to the protocol values: `auto` / `none` / `manual`
- optional `strict_ids=True` was added to fail earlier on common duplicate-ID mistakes
- continuous-content helpers were added to make protocol-aligned `content` authoring easier
- docs now state more clearly that the package implements a stable subset of the v1.0 protocol

## Notes / 备注

- Use TestPyPI first.
- 先发 TestPyPI，再发正式 PyPI。
- Keep version bumps explicit and consistent.
- 版本号变更要明确且保持一致。
- Treat `validate()` / `assert_valid()` as the final gate even if `strict_ids=True` is enabled.
- 即使启用了 `strict_ids=True`，`validate()` / `assert_valid()` 仍然应作为最后一道闸门。
