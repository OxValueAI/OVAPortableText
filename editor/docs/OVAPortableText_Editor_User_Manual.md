# OVAPortableText 编辑器操作手册

这是本项目唯一的精简操作手册。

## 页面逻辑

- 左侧：选择章节。
- 中间：查看当前章节下的所有区块，并调整区块顺序。
- 右侧：编辑当前选中区块的内容、引用或数据。

推荐理解为：

```text
章节 -> 区块 -> 区块详情
```

## 顶部工具栏

- 模式区：`Visual/JSON` / `可视化/JSON`。
- 文件区：`Open`、`Copy JSON`、`Download`。
- 查找区：输入关键词，结果显示在右侧查找结果。
- 历史区：`Undo/Redo` / `撤销/重做`。
- 校验保存区：`Validate`、`Final Preview`、`Save`、`Save Version`。
- 结构区：`Add Section`、`Add Subsection`、`Duplicate Section`、`Delete Section`。
- 语言区：`EN/中文`。

## 常见操作

- 编辑章节标题：左侧选章节，中间修改章节标题。
- 编辑正文：左侧选章节，中间点文本区块，右侧修改文本。
- 编辑图表：左侧选章节，中间点图表区块，右侧修改图表数据。
- 编辑表格：左侧选章节，中间点表格区块，右侧修改表格单元格。
- 新增段落：左侧选章节，中间点 `Add Paragraph` / `添加段落`。
- 调整顺序：在中间区块列表点 `Move Block Up/Down` / `上移区块/下移区块`。
- 复制区块：点 `Duplicate Block` / `复制区块`，会在原区块下方复制一份。
- 删除区块：点 `Delete Block` / `删除区块`，会移除当前章节里的该区块。
- 校验：点 `Validate` / `校验`，问题显示在左侧 `Issues` / `问题`。

## JSON 模式

- 点 `JSON` 进入源码编辑。
- 点 `Apply` / `应用` 应用 JSON 修改。
- 点 `Discard` / `放弃` 丢弃未应用的 JSON 草稿。
- JSON 草稿未应用或无效时，可视化编辑会锁定。

## 文件和版本

- `Open` / `打开`：导入 `.json` 文件。
- `Copy JSON` / `复制 JSON`：复制当前 JSON。
- `Download` / `下载`：下载当前 JSON。
- `Save` / `保存`：触发宿主应用保存回调。
- `Save Version` / `保存版本`：保存浏览器本地版本。
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
