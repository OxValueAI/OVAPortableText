# OVAPortableText Editor Page Logic Roadmap v0.1

Date: 2026-08-28
Status: Proposed redesign route
Scope: Redesign the editor page logic so OVAPortableText editing follows the document's parent-to-child structure.

## Current Problem

The current MVP layout is easy to explain but hard to use:

```text
---------+----------------------+------------------+
| Outline | Section text editor  | Meta / Data      |
+---------+----------------------+------------------+
```

This makes the right panel feel detached from the content being edited. In OVAPortableText, that is especially confusing because chart/table data is not optional metadata. It is often the real content behind a `chartRef` or `tableRef` block.

The current mental model is:

```text
Select section -> edit text in center -> edit related data somewhere on the right
```

The better mental model should be:

```text
Select section -> see its blocks -> select a block -> edit that block's content/data
```

## Correct Interpretation

The current layout roughly means:

- Left: section outline as document index.
- Center: selected section title, first text block, and section-level block ordering.
- Right: document meta, selected resource data, search results, and versions.

This is technically workable, but it does not match how OVAPortableText is structured:

```text
Document
  -> Section
      -> Body / ContentItem
          -> Block
              -> Text children
              -> chartRef -> datasets.charts[id]
              -> tableRef -> datasets.tables[id]
              -> imageRef -> assets.images[id]
```

So chart/table editing should be understood as block editing, not as unrelated right-side metadata editing.

## Proposed Page Logic

Use a left-to-right drill-down model:

```text
+----------------+------------------------------+------------------------------+
| 1. Outline     | 2. Selected Section Blocks    | 3. Selected Block Inspector  |
|                |                              |                              |
| Document tree  | Section title                | Text editor                  |
| Sections       | Ordered block list           | Chart data editor            |
| Search hits    | Add block controls           | Table cell editor            |
| Issues badges  | Move/duplicate/delete block  | Image/source/ref details     |
+----------------+------------------------------+------------------------------+
```

The page should feel like moving from parent to child:

```text
Document / Section tree
  -> Section's ordered content blocks
      -> Selected block's actual editable content and backing data
```

## New Responsibility Split

### Left Panel: Navigate

Purpose: choose the section-level context.

Contains:

- Document outline.
- Section-level issue badges.
- Search entry and search results grouped by section.
- Optional resource usage entry points later.

Does not contain:

- Full resource data editing.
- Large validation lists unless filtered to navigation hints.

### Center Panel: Compose Section

Purpose: show the selected section as an ordered list of content blocks.

Contains:

- Section title editor.
- Section role/level summary.
- Every block in the selected section, in document order.
- Block cards for:
  - paragraph/text
  - chart reference
  - table reference
  - image reference
  - unknown/read-only block
- Add block controls.
- Move block up/down, duplicate block, delete block.
- Lightweight previews or labels for referenced chart/table/image blocks.

Important behavior:

- Selecting a block highlights it in the center.
- Move up/down acts on the selected block within this center list.
- Users should immediately see the list reorder after a move.

### Right Panel: Inspect Selected Block

Purpose: edit the selected block's actual fields and backing data.

Contains by selected block type:

- Text block:
  - rich/plain text content
  - marks later
  - link/citation/xref later
- Chart block:
  - block fields such as caption/layout if present
  - linked chart dataset label
  - chart type-specific data editor
  - reference health and usage
- Table block:
  - block fields such as caption/layout if present
  - linked table dataset label
  - table cell/content editor
  - reference health and usage
- Image block:
  - image preview
  - URL or asset fields
  - alt/caption fields if present
- Unknown block:
  - read-only summary
  - go to JSON path

Global meta, versions, and validation should not dominate this panel. They can move to a top-level utility drawer or compact toolbar popover.

## Recommended User Routes

### Edit Text

```text
Click section in Outline
  -> Click text block in center block list
  -> Edit text in right inspector
```

### Edit Chart

```text
Click section in Outline
  -> Click chart block in center block list
  -> Edit chart data in right inspector
```

The user should not need to manually locate the chart in a separate global resource list.

### Edit Table

```text
Click section in Outline
  -> Click table block in center block list
  -> Edit table cells in right inspector
```

### Reorder Content

```text
Click section in Outline
  -> See all blocks in center
  -> Select a block
  -> Click Move Block Up / Move Block Down
  -> Watch the center list reorder immediately
```

This makes movement visible and local.

### Advanced Resource Management

```text
Open Resources drawer
  -> See all charts/tables/images
  -> Filter unused resources
  -> Show usage
  -> Insert existing resource into current section
```

This belongs outside the normal editing path.

## Toolbar Redesign

Keep global actions in the top toolbar:

- Visual / JSON
- EN / 中文
- Open
- Copy JSON
- Download
- Find
- Undo
- Redo
- Validate
- Save
- Save Version
- Versions

Move structure actions closer to the relevant object:

- Add Section: near or inside the outline.
- Add Subsection: near selected section header.
- Add Block: center panel.
- Move/Duplicate/Delete Block: on selected block card or center block toolbar.

This reduces the feeling that all actions are global.

## Component Refactor Route

### Step 1: Selection Model

Add explicit selected object state:

```ts
type EditorSelection =
  | { kind: "section"; sectionId: string }
  | { kind: "block"; sectionId: string; blockIndex: number }
  | { kind: "resource"; resourceKind: "chart" | "table" | "image"; id: string };
```

Keep `selectedSectionId` as derived or compatibility state during migration.

### Step 2: Center Section Composer

Replace the current `VisualSection` shape with:

```text
SectionComposer
  - SectionHeader
  - BlockList
  - AddBlockBar
```

Block cards should show:

- type
- preview label
- linked resource id
- warning/error badges
- selected state
- local actions

### Step 3: Right Block Inspector

Replace the current always-visible `Properties + Data` stack with:

```text
BlockInspector
  - TextBlockInspector
  - ChartBlockInspector
  - TableBlockInspector
  - ImageBlockInspector
  - UnknownBlockInspector
```

The existing `DataEditor`, `SliceDataEditor`, `BarDataEditor`, `LineDataEditor`, `MatrixBubbleDataEditor`, and table editor should move under the relevant chart/table inspector.

### Step 4: Utilities

Move global utilities into compact secondary surfaces:

- Document meta: toolbar button or drawer.
- Versions: drawer/popover.
- Full issue list: drawer or left filtered panel.
- Global resources: drawer for resource management, not the default right panel.

### Step 5: Browser Tests

Update smoke test to verify the new route:

- select section
- select chart/table block in center
- edit data in right inspector
- select text block
- edit text in right inspector
- move a block and confirm center order changes

## P0 Implementation Target

P0 should deliver the new mental model without overbuilding:

- Left outline remains.
- Center shows selected section's full ordered block list.
- Right edits selected block.
- Chart/table data moves from global right-side resource selection into block inspector.
- Resource list becomes secondary or hidden behind a drawer/button.
- Move up/down visibly reorders center block list.
- Manual stays short and updates to the new route.

## P1 Later

- Drag-and-drop block reordering.
- Split preview mode.
- Resource manager drawer with unused resource cleanup.
- More complete table operations.
- Rich text marks and links.
- Section promote/demote.

## Decision

The editor should move away from:

```text
Outline | Document editor | Meta/Data
```

and toward:

```text
Outline | Section block composer | Selected block inspector
```

This better matches OVAPortableText because the editable unit is usually not just a section or a resource; it is a block inside a section, sometimes backed by a dataset.
