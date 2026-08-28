# OVAPortableText Editor UX Redesign v0.2

Date: 2026-08-28
Status: Proposed replacement direction
Scope: Redesign navigation, layout widths, toolbar grouping, and component styling before the next implementation pass.

## Why The Current UI Feels Wrong

The current implementation is functionally moving in the right direction, but the interaction surface still feels like a developer scaffold:

- The center column is too wide for the amount of direct editing it currently owns.
- The toolbar has too many equally weighted buttons.
- The visual hierarchy does not express OVAPortableText's nested structure well enough.
- Chart/table data still feels like a form area, not like content reached from a document node.
- Styling is too raw: borders, cards, buttons, spacing, and state cues do not feel like a modern editor.

The main mistake is treating the UI as three flat panels. OVAPortableText should feel like a structured object editor.

## Recommended Information Architecture

Move from:

```text
Outline | Section block composer | Block inspector
```

to:

```text
Hierarchical Navigator | Focused Editor | Context Dock
```

### 1. Hierarchical Navigator

The left side should become the main structural browser.

It should include sections and their blocks as nested children:

```text
Report
  Cover
  Table of Contents
  1. Market Overview
    Text block
    Chart: Patent trend
    Table: Comparable companies
    Text block
  2. Valuation Logic
    Text block
    Matrix chart
```

Behavior:

- Sections can expand/collapse.
- The selected section expands and shows its child blocks.
- Selecting a section opens section-level editing in the center.
- Selecting a block opens block-level editing in the center.
- Search results can jump to either a section or a block.
- Issue badges should appear next to the relevant section/block where possible.

This matches a JSON editor/tree editor mental model while still hiding raw JSON complexity.

### 2. Focused Editor

The center should be the primary editing surface for the selected object.

If a section is selected:

- Edit section title.
- Show a compact ordered block list.
- Add paragraph/chart/table/image block.
- Reorder blocks.

If a text block is selected:

- Edit text directly.
- Later: marks, links, citations, xrefs.

If a chart block is selected:

- Show chart block summary.
- Edit linked chart dataset in the same center editor.
- Show reference id and chart type as secondary information.

If a table block is selected:

- Edit linked table data in the same center editor.
- Preserve rowSpan/colSpan by default.

If an image block is selected:

- Show preview and editable source/alt fields later.

The center should not stretch endlessly. Recommended desktop width:

```text
minmax(560px, 760px)
```

For wide screens, keep the center editor visually constrained and let the context dock use the extra width.

### 3. Context Dock

The right side should stop being the default editing destination. It should provide supporting context:

- Document summary.
- Selected object metadata.
- Reference health and usages.
- Validation details.
- Local versions.
- Advanced JSON path / raw object preview.

Default width:

```text
320px to 360px
```

It can be collapsible in a later pass.

## Proposed Desktop Layout

```text
+---------------------------+--------------------------------+--------------------+
| Toolbar grouped by task                                                     |
+---------------------------+--------------------------------+--------------------+
| Navigator                 | Focused Editor                 | Context Dock       |
| 300-340px                 | 560-760px                      | 320-360px          |
|                           | centered, not over-wide        | support only       |
+---------------------------+--------------------------------+--------------------+
```

CSS target:

```css
grid-template-columns: minmax(300px, 340px) minmax(560px, 760px) minmax(320px, 360px);
justify-content: center;
```

On screens where this does not fit:

- Collapse context dock under the editor.
- Keep navigator above or as a drawer.

## Toolbar Redesign

The toolbar should become a calm command bar with grouped controls.

### Primary Groups

1. Mode
   - Visual
   - JSON

2. File
   - Open
   - Copy JSON
   - Download

3. Search
   - Find input

4. History
   - Undo
   - Redo

5. Validate / Save
   - Validate
   - Save
   - Save Version
   - Final Preview

6. Language
   - EN
   - 中文

7. Status
   - Saved/Modified
   - Error/warning counts

### What Should Move Out Of The Toolbar

These should not be global toolbar buttons:

- Add Section
- Add Subsection
- Duplicate Section
- Delete Section
- Add Paragraph
- Move Block Up/Down
- Duplicate Block
- Delete Block

They should live next to the selected object:

- Section actions in the navigator or section editor header.
- Block actions on block rows or selected block editor header.

## Component System Direction

### Local Search Result

No existing local UI component library was found in this repository.

Current editor UI is hand-written CSS and native controls.

### External Options Considered

#### shadcn/ui-style Local Components

Best fit for this project.

Why:

- Components are copied into the project and can be modified locally.
- Good fit for building an internal, domain-specific editor.
- Works well with Radix primitives and lucide icons.
- Lets us build a self-owned `editor-react/src/ui/` layer instead of importing a heavy black-box component library everywhere.

Tradeoff:

- Requires introducing Tailwind or manually translating component styles.
- Since the current app is plain CSS, we should not run the full CLI immediately unless we decide to adopt Tailwind.

Recommended adaptation:

```text
editor/packages/editor-react/src/ui/
  Button.tsx
  IconButton.tsx
  SegmentedControl.tsx
  Toolbar.tsx
  Tree.tsx
  Panel.tsx
  Badge.tsx
  Field.tsx
  Textarea.tsx
```

Use shadcn/Radix patterns as reference, but keep styling in local CSS variables first.

#### Radix Themes

Good if we want a quick visual upgrade with a polished default theme.

Why:

- Pre-styled React components.
- Theme wrapper provides consistent color, radius, scaling, and panel styling.
- Lower design effort than building everything from raw CSS.

Tradeoff:

- Styling is more closed than a copy-owned component approach.
- The editor may need custom dense tree/table/editor surfaces where Radix Themes is not enough.

Recommended use:

- Consider Radix primitives or Themes for Dialog, Tooltip, Popover, Tabs, ScrollArea, and segmented controls.
- Avoid forcing every editor surface into generic cards.

#### Mantine / Ant Design / MUI

Not recommended for this editor's current stage.

Why:

- They are complete component frameworks and can quickly overpower the domain-specific editor experience.
- They add more visual and dependency commitment than needed for a focused OVAPortableText tool.

## Visual Style Direction

The editor should feel like a modern structured authoring tool, not a prototype form.

Use:

- Neutral background: `#f6f7f9`.
- White or near-white panels.
- Thin borders: `#e4e7ec`.
- Text: `#111827`, secondary `#667085`.
- Accent: restrained blue or teal for selected state.
- 6px to 8px radius.
- Clear hover/selected/focus states.
- Compact density, but not cramped.

Avoid:

- Big decorative cards.
- Saturated gradients.
- One long row of equal buttons.
- Over-wide text editing surfaces.
- Putting every action in the top toolbar.

## New Selection Model

Use one explicit selection object:

```ts
type EditorSelection =
  | { kind: "document" }
  | { kind: "section"; sectionId: string }
  | { kind: "block"; sectionId: string; blockIndex: number };
```

Derived data:

- selected section
- selected block
- selected chart/table/image resource if the block has a reference
- JSON path for context dock

## Implementation Route

### Step 1: Local UI Kit

Create a local UI layer:

```text
packages/editor-react/src/ui/
```

Start with:

- Button
- IconButton
- ToolbarGroup
- SegmentedControl
- Panel
- Badge
- Field
- Textarea
- TreeItem

No dependency install required for the first pass.

Optional later:

- Add `lucide-react` for icons.
- Add Radix primitives for tooltip/dialog/popover/scroll-area.

### Step 2: Navigator Tree With Blocks

Replace the current left outline with:

```text
NavigatorTree
  SectionNode
    BlockNode[]
```

Each block node label should be compact and useful:

- Text: first 40-60 chars
- Chart: chart label or `chartRef`
- Table: table label or `tableRef`
- Image: image id/ref
- Unknown: `_type`

### Step 3: Center Focused Editor

Replace center block-list-first layout with object-specific editors:

- SectionEditor
- TextBlockEditor
- ChartBlockEditor
- TableBlockEditor
- ImageBlockEditor
- UnknownBlockViewer

### Step 4: Context Dock

Keep secondary information on the right:

- selected object path
- reference status
- document summary
- issues
- versions

### Step 5: Toolbar

Remove structure actions from top toolbar.

Use:

```text
[Visual JSON] | [Open Copy Download] | [Find...] | [Undo Redo] | [Validate Save Save Version Preview] | [EN 中文] | Status
```

### Step 6: Tests

Update browser smoke path:

```text
load page
select a section in navigator
expand section blocks
select a text block
edit center text
select a chart block
verify center chart data editor
verify toolbar groups exist
verify independent scrolling
```

## Decision

The next UI implementation should not keep patching the current three flat panels.

Use:

```text
Hierarchical Navigator | Focused Editor | Context Dock
```

This better matches OVAPortableText, reduces center width, makes block movement visible in the navigation hierarchy, and gives the editor a more modern product structure.
