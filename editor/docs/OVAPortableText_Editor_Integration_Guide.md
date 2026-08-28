# OVAPortableText 编辑器对接指南

## 推荐接入面

对外优先暴露 React 组件包：

```ts
import {
  OVAPortableTextEditor,
  type OVAPortableTextEditorHandle,
  type OVAReportDocument
} from "@ova/portable-text-editor-react";
```

宿主项目只需要传入 OVAPortableText JSON，并处理保存回调。

## 最小示例

```tsx
import { useRef } from "react";
import {
  OVAPortableTextEditor,
  type OVAPortableTextEditorHandle,
  type OVAReportDocument
} from "@ova/portable-text-editor-react";

export function ReportEditorPage({ initialReport }: { initialReport: OVAReportDocument }) {
  const editorRef = useRef<OVAPortableTextEditorHandle>(null);

  return (
    <OVAPortableTextEditor
      ref={editorRef}
      initialValue={initialReport}
      initialLocale="zh"
      style={{ height: "calc(100vh - 64px)" }}
      onSave={async (document) => {
        await fetch("/api/reports/current", {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(document)
        });
      }}
      onDirtyChange={(dirty) => {
        console.log("dirty", dirty);
      }}
      onValidationChange={(result) => {
        console.log("validation issues", result.issues);
      }}
      onRequestFinalPreview={(document) => {
        console.log("preview", document);
      }}
    />
  );
}
```

## Props

- `initialValue`: 初始 OVAPortableText JSON，可传对象或 JSON 字符串。
- `initialLocale`: `"zh"` 或 `"en"`，不传则跟随浏览器语言。
- `readOnly`: 只读模式。
- `className`: 宿主页面追加外层 class。
- `style`: 宿主页面控制外层尺寸，嵌入页面时建议显式传高度。
- `versioning`: 浏览器本地版本能力；不传则隐藏/禁用本地版本保存。
- `onSave(document)`: 用户点击 Save 时触发，宿主在这里调后端保存。
- `onDirtyChange(dirty)`: 文档脏状态变化。
- `onValidationChange(result)`: 校验结果变化。
- `onRequestFinalPreview(document)`: 用户点击最终预览时触发。

## Ref API

```ts
await editorRef.current?.setValue(nextJson);
const value = editorRef.current?.getValue();
const json = editorRef.current?.getJSONString(true);
const validation = editorRef.current?.validate();
editorRef.current?.setMode("json");
editorRef.current?.undo();
editorRef.current?.redo();
const dirty = editorRef.current?.isDirty();
```

本地版本相关：

```ts
await editorRef.current?.saveVersion("before publish");
const versions = await editorRef.current?.listVersions();
await editorRef.current?.loadVersion(versionId);
```

## 宿主保存流程

推荐流程：

```text
加载报告 JSON -> initialValue -> 用户编辑 -> onSave(document) -> PUT/POST 到业务后端
```

如果宿主需要主动保存：

```ts
const document = editorRef.current?.getValue();
if (document) {
  await saveReport(document);
}
```

## 尺寸约定

编辑器默认按可视窗口高度工作。嵌入已有管理后台时，建议宿主给外层固定高度：

```tsx
<OVAPortableTextEditor style={{ height: "calc(100vh - 56px)", minHeight: 720 }} />
```

## 本地版本配置

```tsx
<OVAPortableTextEditor
  versioning={{
    enabled: true,
    documentKey: reportId,
    namespace: "ova-report-editor"
  }}
/>
```

`documentKey` 应由宿主业务对象 ID 提供，避免不同报告的本地版本混在一起。

## 包形态

当前 monorepo 中可通过 workspace 使用：

```json
{
  "dependencies": {
    "@ova/portable-text-editor-react": "file:../path/to/editor/packages/editor-react"
  }
}
```

正式嵌入其他仓库时，建议把 `packages/editor-core` 和 `packages/editor-react` 发布到私有 npm registry，或在目标前端仓库中以 git submodule/workspace 方式接入。
