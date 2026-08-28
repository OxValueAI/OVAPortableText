# OVAPortableText Editor Development Log 008

Date: 2026-08-28
Scope: Reassess the page information architecture and document a revised editor logic route.

## Trigger

The current three-panel MVP is functional but not intuitive enough for OVAPortableText. The user correctly identified that:

- The left panel works as a section index.
- The center panel edits section content and block order.
- The right panel currently mixes meta information and chart/table data.

This split makes chart/table data feel detached from the content block that references it.

## Design Finding

OVAPortableText is best edited as a parent-to-child drill-down:

```text
Section tree -> Section blocks -> Selected block details/data
```

The right panel should primarily inspect and edit the selected block, not act as a global meta/data bucket.

## Output

Added a new page logic roadmap:

```text
docs/OVAPortableText_Editor_Page_Logic_Roadmap_v0.1.md
```

## Proposed Direction

- Keep the left panel as the section outline.
- Redesign the center panel as the selected section's ordered block composer.
- Redesign the right panel as the selected block inspector.
- Move chart/table data editing under chart/table block inspection.
- Move document meta, versions, full resources, and full issues into secondary utility surfaces.

## Next Implementation Route

1. Add explicit selected object state for section/block/resource.
2. Replace `VisualSection` with a `SectionComposer`.
3. Move existing chart/table `DataEditor` pieces under a `BlockInspector`.
4. Update the concise user manual after the UI route changes.
5. Update browser smoke tests to follow the new section -> block -> inspector path.
