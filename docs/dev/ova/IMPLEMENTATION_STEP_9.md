# OVAPortableText Step 9

## 本步目标 / Goal

这一步进入“发布前工程化 + 文档与测试收束”的阶段。

重点不是再大量新增协议字段，而是让当前代码库更接近一个真正可发布、可维护、可协作的 Python 包：

- 补齐发布相关文件
- 补齐 CI 与打包配置
- 补齐一轮边界测试
- 实际验证 wheel / sdist 构建与干净环境安装

协议对齐上，仍然保持以下边界不变：

- 顶层结构、章节树、registry、引用与校验是 v1 重点
- 标题文本与结构编号分离
- `theme` 仍然是轻量占位层
- `datasets.charts` 当前正式细化仍以 `pie` 为主
- Java 渲染样式与页面排版仍不纳入当前 Python 包职责

## 本步新增 / Added in this step

### 1. 发布前工程化文件

新增：

- `LICENSE`
- `CHANGELOG.md`
- `src/ova_portable_text/version.py`
- `src/ova_portable_text/py.typed`
- `.github/workflows/ci.yml`
- `docs/API_REFERENCE.md`
- `docs/PUBLISHING_CHECKLIST.md`

### 2. 运行时版本号

新增统一版本源：

- `ova_portable_text.__version__`

这样后续在：

- 调试
- 发布检查
- wheel 安装验证
- 日志输出

这些场景里都可以直接看到运行时版本。

### 3. 打包配置增强

`pyproject.toml` 已增强：

- 声明 typed package（`Typing :: Typed`）
- 增加 `dev` optional dependencies
- 增加 hatch wheel/sdist 构建配置
- 增加 `ruff` 基础配置

### 4. README 与文档增强

README 已补：

- 本地开发安装方式
- 类发布方式构建测试
- 发布准备说明
- 版本读取示例

docs 新增：

- `API_REFERENCE.md`
- `PUBLISHING_CHECKLIST.md`

### 5. Python 风格易用性修复

在真实 wheel 安装检查时，发现：

- `ValidationReport` 只有协议风格字段 `isValid`
- 但 Python 用户更自然会写 `report.validate().is_valid`

因此新增：

- `ValidationReport.is_valid` 属性

这样既保留协议导出字段风格，也补足 Python 对象使用手感。

### 6. 新增测试

新增测试文件：

- `tests/test_roundtrip_and_runtime_version.py`
- `tests/test_document_validation_error_rendering.py`
- `tests/test_validation_report_python_alias.py`

覆盖点包括：

- `__version__` 暴露
- `Document.from_json()` round-trip
- `ValidationReport.is_valid` Python 别名
- `DocumentValidationError` 文本中是否包含上下文

## 本步实际验证 / What was actually verified

### 单元测试

已实际运行：

```bash
pytest -q
```

结果：

- `29 passed`

### 构建验证

已实际运行：

```bash
python -m build
```

构建成功生成：

- sdist
- wheel

### 干净环境 wheel 安装验证

已实际运行：

- 新建独立虚拟环境
- `pip install dist/*.whl`
- 导入 `ova_portable_text`
- 读取 `__version__`
- 创建最小文档
- 调用 `validate().is_valid`
- 构建 resolver

这说明当前包已经不只是“源码目录下能跑”，而是“构建并安装后也能正常使用”。

## 当前发布前状态 / Current pre-release state

当前已经具备：

- 可运行的 builder API
- registry / resolver / validator
- round-trip
- 文档与样例
- 29 个测试
- CI 基础配置
- wheel / sdist 构建验证
- 干净环境安装验证

## 建议的下一步 / Recommended next step

下一步建议正式进入：

### Step 10：文档与样例进一步完善 + 回测准备

建议内容：

1. 再补 2~3 组更贴近真实业务的完整样例
2. README 再补 FAQ / 设计边界说明
3. 对外 API 做一次“冻结前梳理”
4. 你开始按真实业务写几份 JSON 回测
5. 再集中修一轮 bug / 不顺手 API
6. 然后准备 TestPyPI
