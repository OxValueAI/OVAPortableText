# OVAPortableText 编辑器操作手册

这是本项目唯一的精简操作手册。

## 界面结构

- 左侧：大纲、资源、问题。
- 中间：当前章节编辑区，或 JSON 源码编辑区。
- 右侧：属性、图表/表格数据、查找结果、本地版本。
- 桌面端左/中/右三栏各自独立滚动。

## 语言切换

- 点击顶部 `EN` / `中文` 切换编辑器界面语言。
- 这只改变按钮和面板文案，不会翻译报告内容。

## 常见操作

- 编辑章节：在左侧大纲点选章节，在中间修改标题或正文。
- 新增章节：点 `Add Section` / `添加章节`，新增一级章节。
- 新增子章节：先选中章节，再点 `Add Subsection` / `添加子章节`。
- 新增正文段落：先选中章节，再点 `Add Paragraph` / `添加段落`。
- 上移/下移区块：`Move Block Up/Down` / `上移区块/下移区块` 只改变当前章节内该区块的前后顺序。
- 复制区块：`Duplicate Block` / `复制区块` 会在原区块下方复制一份。
- 删除区块：`Delete Block` / `删除区块` 会从当前章节移除该区块。
- 编辑图表/表格：左侧 `Resources` / `资源` 里选择图表或表格，在右侧 `Data` / `数据` 修改支持字段。
- 查找：在顶部 `Find` / `查找` 输入关键词，结果显示在右侧 `Find Results` / `查找结果`。
- 校验：点 `Validate` / `校验`，错误和警告显示在左侧 `Issues` / `问题`。
- 撤销/重做：点 `Undo/Redo` / `撤销/重做` 回退或恢复可视化编辑。

## JSON 模式

- 点 `JSON` 进入源码编辑。
- 点 `Apply` / `应用` 解析并应用 JSON 修改。
- 点 `Discard` / `放弃` 丢弃未应用的 JSON 草稿。
- JSON 有未应用或无效内容时，可视化编辑会被锁定。

## 文件和版本

- `Open` / `打开`：导入另一个 `.json` 文件。
- `Copy JSON` / `复制 JSON`：复制当前 JSON。
- `Download` / `下载`：下载当前 JSON。
- `Save` / `保存`：触发宿主应用保存回调。
- `Save Version` / `保存版本`：保存一个浏览器本地版本。
- `Versions` / `版本`：加载、重命名、删除浏览器本地版本。

## 本地测试

在 `editor/` 目录执行：

```powershell
$env:Path = (Resolve-Path '.\.tools\node-v22.23.2-win-x64').Path + ';' + $env:Path
npm.cmd run dev
```

打开 `http://127.0.0.1:5173/`。

浏览器自动化 smoke test：

```powershell
npm.cmd run browser:smoke
```
