# OVAPortableText Editor Development Log 010

Date: 2026-08-28
Scope: Reassess dissatisfaction with current editor UI and define a stronger UX redesign before coding the next pass.

## Trigger

The current UI is still not satisfactory:

- The center area is too wide.
- The functional split is not intuitive enough.
- The toolbar is visually noisy.
- The visual design still feels too raw and not modern enough.
- The user suggested moving blocks into the left outline under their sections, similar to a JSON editor tree.

## Findings

- No existing local frontend component library or design system was found in the repository.
- The current editor UI is built from native controls and one CSS file.
- The better OVAPortableText model is:

```text
Hierarchical Navigator -> Focused Editor -> Context Dock
```

instead of:

```text
Outline -> Section block composer -> Block inspector
```

## UI Library Direction

Recommended direction:

- Build a local, self-owned component layer under `packages/editor-react/src/ui/`.
- Borrow interaction and visual patterns from shadcn/ui and Radix, but keep the first pass local and lightweight.
- Consider adding `lucide-react` later for modern icon buttons.
- Consider Radix primitives later for tooltip/dialog/popover/scroll-area.

Avoid for now:

- Full adoption of a large component framework.
- A heavy Tailwind migration before the editor structure is right.

## Output

Added:

```text
docs/OVAPortableText_Editor_UX_Redesign_v0.2.md
```

This document defines:

- New nested navigator model.
- New center focused editor model.
- New context dock responsibility.
- Toolbar grouping rules.
- Local UI kit direction.
- Step-by-step implementation route.

## Next Recommended Implementation

1. Create local UI primitives.
2. Move section blocks into the left hierarchical navigator.
3. Make the center panel edit the selected section or selected block.
4. Reduce center width and use the right side only for context.
5. Update browser tests to verify the new route.
