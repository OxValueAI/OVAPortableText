# OVAPortableText Editor Integration Guide / 编辑器对接指南

## Simple Contract / 简单对接约定

Host app passes one raw OVAPortableText JSON value into the editor.

前端宿主项目只需要把一份原始 OVAPortableText JSON 传给编辑器。

When the user clicks `Save`, the editor asks for confirmation, then calls `onSave(document)` with the current full JSON object.

用户点击 `Save / 保存` 时，编辑器会先弹窗确认；确认后通过 `onSave(document)` 把当前完整 JSON 对象回传给宿主项目。

```text
raw JSON -> OVAPortableTextEditor -> user edits -> Save -> onSave(current JSON)
原始 JSON -> 编辑器 -> 用户编辑 -> 保存 -> 回传当前 JSON
```

## Minimal React Usage / 最小 React 用法

```tsx
import { OVAPortableTextEditor, type OVAReportDocument } from "@ova/portable-text-editor-react";

export function ReportEditorPage({ reportJson }: { reportJson: OVAReportDocument }) {
  return (
    <OVAPortableTextEditor
      initialValue={reportJson}
      initialLocale="zh"
      style={{ height: "calc(100vh - 64px)" }}
      onSave={async (currentJson) => {
        await fetch("/api/reports/current", {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(currentJson)
        });
      }}
    />
  );
}
```

## Props You Usually Need / 常用 Props

- `initialValue`: raw JSON object or JSON string. / 原始 JSON 对象或 JSON 字符串。
- `initialLocale`: `"zh"` or `"en"`. / 初始界面语言。
- `style`: set editor height in the host page. / 在宿主页面控制编辑器高度。
- `onSave(document)`: save callback fired after user confirmation. / 用户确认保存后触发的回调。

Optional:

- `readOnly`: disable visual editing. / 只读模式。
- `onDirtyChange(dirty)`: receive unsaved-change state. / 接收是否有未保存修改。
- `onValidationChange(result)`: receive validation result. / 接收校验结果。
- `onRequestFinalPreview(document)`: handle final preview button. / 接管最终预览按钮。

## Imperative API / 主动调用 API

Use a ref only when the host needs to trigger actions outside the editor.

只有宿主需要在编辑器外部主动触发行为时，才需要 ref。

```tsx
import { useRef } from "react";
import { OVAPortableTextEditor, type OVAPortableTextEditorHandle } from "@ova/portable-text-editor-react";

const editorRef = useRef<OVAPortableTextEditorHandle>(null);

const currentJson = editorRef.current?.getValue();
const currentText = editorRef.current?.getJSONString(true);
const validation = editorRef.current?.validate();

await editorRef.current?.setValue(nextRawJson);
editorRef.current?.undo();
editorRef.current?.redo();
```

## Recommended Save Flow / 推荐保存流程

```text
1. Host fetches report JSON from backend.
2. Host renders editor with initialValue.
3. User edits inside the editor.
4. User clicks Save.
5. Editor shows a confirmation dialog.
6. If confirmed, editor calls onSave(currentJson).
7. Host sends currentJson to backend.
```

```text
1. 宿主从后端读取报告 JSON。
2. 宿主用 initialValue 渲染编辑器。
3. 用户在编辑器中修改。
4. 用户点击保存。
5. 编辑器弹窗确认。
6. 用户确认后，编辑器调用 onSave(currentJson)。
7. 宿主把 currentJson 发送到后端。
```

## Package Integration / 包接入

In this monorepo, use the workspace package directly.

在当前 monorepo 内，直接使用 workspace 包。

```ts
import { OVAPortableTextEditor } from "@ova/portable-text-editor-react";
```

For another frontend repository, use one of these practical options:

在其他前端仓库中，建议用下面任一种简单方式：

- private npm package / 私有 npm 包
- git submodule / Git 子模块
- copied `editor/packages/editor-core` and `editor/packages/editor-react` packages / 复制两个 package 到目标仓库
