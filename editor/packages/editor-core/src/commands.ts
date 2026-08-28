import type {
  JSONObject,
  JSONValue,
  MultilingualText,
  OVABlock,
  OVAContentItem,
  OVAReportDocument,
  OVASection
} from "./types";
import { cloneDocument } from "./json";
import { displayText, flattenSections } from "./sections";
import { validateDocument } from "./validation";

export interface CommandResult {
  document: OVAReportDocument;
  changed: boolean;
  selectionId?: string;
}

export function updateSectionTitle(
  document: OVAReportDocument,
  sectionId: string,
  title: string,
  language = document.meta?.language ?? "en"
): CommandResult {
  const next = cloneDocument(document);
  const node = flattenSections(next.sections).find((item) => item.id === sectionId);

  if (!node) {
    return { document, changed: false };
  }

  node.section.title = updateMultilingualText(node.section.title, title, language);
  return { document: next, changed: true, selectionId: sectionId };
}

export function updateFirstTextBlock(
  document: OVAReportDocument,
  sectionId: string,
  text: string
): CommandResult {
  const next = cloneDocument(document);
  const node = flattenSections(next.sections).find((item) => item.id === sectionId);
  const firstBlock = node?.section.body
    ?.flatMap((item) => item.blocks ?? [])
    .find((block) => block._type === "block" && Array.isArray(block.children));

  const firstSpan = firstBlock?.children?.find((child) => child._type === "span");
  if (!firstSpan) {
    return { document, changed: false };
  }

  firstSpan.text = text;
  return { document: next, changed: true, selectionId: sectionId };
}

export function updateTextBlock(
  document: OVAReportDocument,
  sectionId: string,
  blockIndex: number,
  text: string
): CommandResult {
  const next = cloneDocument(document);
  const slot = editableBlockSlots(next, sectionId)[blockIndex];
  if (!slot?.block || slot.block._type !== "block" || !Array.isArray(slot.block.children)) {
    return { document, changed: false };
  }

  const firstSpan = slot.block.children.find((child) => child._type === "span");
  if (!firstSpan) {
    return { document, changed: false };
  }

  firstSpan.text = text;
  return { document: next, changed: true, selectionId: sectionId };
}

export function addSection(
  document: OVAReportDocument,
  options: { parentSectionId?: string; title?: string } = {}
): CommandResult {
  const next = cloneDocument(document);
  const ids = collectIds(next);
  const parent = options.parentSectionId
    ? flattenSections(next.sections).find((node) => node.id === options.parentSectionId)?.section
    : undefined;
  const level = parent ? normalizeLevel(parent.level) + 1 : 1;
  const id = uniqueId(slugify(options.title ?? "section"), ids);
  const section = createSection(id, options.title ?? "Untitled Section", level);

  if (parent) {
    parent.body = parent.body ?? [];
    parent.body.push({ itemType: "subsection", section });
  } else {
    next.sections = next.sections ?? [];
    next.sections.push(section);
  }

  return { document: next, changed: true, selectionId: id };
}

export function deleteSection(document: OVAReportDocument, sectionId: string): CommandResult {
  const node = flattenSections(document.sections).find((item) => item.id === sectionId);
  if (!node || isProtectedSection(node.section)) {
    return { document, changed: false };
  }

  const next = cloneDocument(document);
  const removed = removeSection(next.sections ?? [], sectionId);
  return { document: next, changed: removed };
}

export function duplicateSection(document: OVAReportDocument, sectionId: string): CommandResult {
  const next = cloneDocument(document);
  const ids = collectIds(next);
  const duplicated = duplicateSectionInList(next.sections ?? [], sectionId, ids);
  return duplicated
    ? { document: next, changed: true, selectionId: duplicated }
    : { document, changed: false };
}

export function moveSection(
  document: OVAReportDocument,
  sectionId: string,
  targetParentSectionId: string | undefined,
  targetIndex: number
): CommandResult {
  const node = flattenSections(document.sections).find((item) => item.id === sectionId);
  if (!node || isProtectedSection(node.section) || sectionId === targetParentSectionId) {
    return { document, changed: false };
  }

  const next = cloneDocument(document);
  const removed = detachSection(next.sections ?? [], sectionId);
  if (!removed) {
    return { document, changed: false };
  }

  const targetParent = targetParentSectionId
    ? flattenSections(next.sections).find((item) => item.id === targetParentSectionId)?.section
    : undefined;
  const newLevel = targetParent ? normalizeLevel(targetParent.level) + 1 : 1;
  updateSectionLevels(removed, newLevel);

  if (targetParent) {
    targetParent.body = targetParent.body ?? [];
    const bodyIndex = clampIndex(targetIndex, targetParent.body.length);
    targetParent.body.splice(bodyIndex, 0, { itemType: "subsection", section: removed });
  } else {
    next.sections = next.sections ?? [];
    next.sections.splice(clampIndex(targetIndex, next.sections.length), 0, removed);
  }

  return withSelection(next, true, removed.id ?? removed.anchor);
}

export function addParagraphBlock(
  document: OVAReportDocument,
  sectionId: string,
  text = ""
): CommandResult {
  const next = cloneDocument(document);
  const section = flattenSections(next.sections).find((item) => item.id === sectionId)?.section;
  if (!section) {
    return { document, changed: false };
  }

  const content = ensureEditableContent(section);
  content.blocks = content.blocks ?? [];
  content.blocks.push(createParagraphBlock(text));

  return { document: next, changed: true, selectionId: sectionId };
}

export function addChartBlock(document: OVAReportDocument, sectionId: string, chartRef: string): CommandResult {
  return addReferencedBlock(document, sectionId, { _type: "chart", chartRef });
}

export function addTableBlock(document: OVAReportDocument, sectionId: string, tableRef: string): CommandResult {
  return addReferencedBlock(document, sectionId, { _type: "table", tableRef });
}

export function deleteBlock(document: OVAReportDocument, sectionId: string, blockIndex: number): CommandResult {
  const next = cloneDocument(document);
  const slot = editableBlockSlots(next, sectionId)[blockIndex];
  if (!slot) {
    return { document, changed: false };
  }

  slot.blocks.splice(slot.index, 1);
  return { document: next, changed: true, selectionId: sectionId };
}

export function moveBlock(
  document: OVAReportDocument,
  sectionId: string,
  fromIndex: number,
  toIndex: number
): CommandResult {
  const next = cloneDocument(document);
  const slots = editableBlockSlots(next, sectionId);
  const from = slots[fromIndex];
  if (!from) {
    return { document, changed: false };
  }

  const [block] = from.blocks.splice(from.index, 1);
  if (!block) {
    return { document, changed: false };
  }

  const refreshedSlots = editableBlockSlots(next, sectionId);
  const target = toIndex >= refreshedSlots.length ? undefined : refreshedSlots[clampIndex(toIndex, refreshedSlots.length - 1)];
  if (target) {
    target.blocks.splice(target.index, 0, block);
  } else {
    const section = flattenSections(next.sections).find((item) => item.id === sectionId)?.section;
    const content = section ? ensureEditableContent(section) : undefined;
    content?.blocks?.push(block);
  }

  return { document: next, changed: true, selectionId: sectionId };
}

export function duplicateBlock(document: OVAReportDocument, sectionId: string, blockIndex: number): CommandResult {
  const next = cloneDocument(document);
  const slot = editableBlockSlots(next, sectionId)[blockIndex];
  if (!slot) {
    return { document, changed: false };
  }

  const ids = collectIds(next);
  const copy = cloneBlockWithIndependentData(next, slot.block, ids);
  slot.blocks.splice(slot.index + 1, 0, copy);
  return { document: next, changed: true, selectionId: sectionId };
}

export function safeRenameChart(document: OVAReportDocument, oldId: string, newId: string): CommandResult {
  if (!newId || oldId === newId) {
    return { document, changed: false };
  }

  const validation = validateDocument(document);
  if (validation.referenceIndex.resources.charts.has(newId)) {
    return { document, changed: false };
  }

  const next = cloneDocument(document);
  next.datasets?.charts?.forEach((chart) => {
    if (chart.id === oldId) {
      chart.id = newId;
    }
    if (chart.anchor === oldId) {
      chart.anchor = newId;
    }
  });

  const rewrite = (value: unknown): void => {
    if (Array.isArray(value)) {
      value.forEach(rewrite);
      return;
    }
    if (value && typeof value === "object") {
      const object = value as Record<string, unknown>;
      if (object.chartRef === oldId) {
        object.chartRef = newId;
      }
      Object.values(object).forEach(rewrite);
    }
  };

  rewrite(next.sections);
  return { document: next, changed: true };
}

export function updateChartLabel(
  document: OVAReportDocument,
  chartId: string,
  label: string,
  language = document.meta?.language ?? "en"
): CommandResult {
  const next = cloneDocument(document);
  const chart = next.datasets?.charts?.find((item) => item.id === chartId);
  if (!chart) {
    return { document, changed: false };
  }

  chart.label = updateMultilingualText(chart.label as MultilingualText | undefined, label, language);
  return { document: next, changed: true };
}

export function updateChartSlice(
  document: OVAReportDocument,
  chartId: string,
  sliceKey: string,
  patch: { label?: string; value?: number },
  language = document.meta?.language ?? "en"
): CommandResult {
  const next = cloneDocument(document);
  const chart = next.datasets?.charts?.find((item) => item.id === chartId);
  const slices = Array.isArray(chart?.slices) ? chart.slices : undefined;
  const slice = slices?.find((item) => isJSONObject(item) && item.key === sliceKey) as JSONObject | undefined;
  if (!slice) {
    return { document, changed: false };
  }

  if (patch.label !== undefined) {
    slice.label = updateMultilingualText(slice.label as MultilingualText | undefined, patch.label, language);
  }
  if (patch.value !== undefined && Number.isFinite(patch.value)) {
    slice.value = patch.value;
  }

  return { document: next, changed: true };
}

export function updateBarChartCategory(
  document: OVAReportDocument,
  chartId: string,
  categoryKey: string,
  label: string,
  language = document.meta?.language ?? "en"
): CommandResult {
  const next = cloneDocument(document);
  const chart = next.datasets?.charts?.find((item) => item.id === chartId);
  const categories = Array.isArray(chart?.categories) ? chart.categories : undefined;
  const category = categories?.find((item) => isJSONObject(item) && item.key === categoryKey) as JSONObject | undefined;
  if (!category) {
    return { document, changed: false };
  }

  category.label = updateMultilingualText(category.label as MultilingualText | undefined, label, language);
  return { document: next, changed: true };
}

export function updateBarChartValue(
  document: OVAReportDocument,
  chartId: string,
  seriesKey: string,
  categoryKey: string,
  value: number
): CommandResult {
  const next = cloneDocument(document);
  const point = findSeriesItem(next, chartId, seriesKey, "data", (item) => item.categoryKey === categoryKey);
  if (!point || !Number.isFinite(value)) {
    return { document, changed: false };
  }

  point.value = value;
  return { document: next, changed: true };
}

export function updateLineChartPoint(
  document: OVAReportDocument,
  chartId: string,
  seriesKey: string,
  pointKey: string,
  patch: { label?: string; xValue?: number; yValue?: number },
  language = document.meta?.language ?? "en"
): CommandResult {
  const next = cloneDocument(document);
  const point = findSeriesItem(next, chartId, seriesKey, "points", (item) => item.key === pointKey);
  if (!point) {
    return { document, changed: false };
  }

  if (patch.label !== undefined) {
    point.label = updateMultilingualText(point.label as MultilingualText | undefined, patch.label, language);
  }
  if (patch.xValue !== undefined && Number.isFinite(patch.xValue)) {
    point.xValue = patch.xValue;
  }
  if (patch.yValue !== undefined && Number.isFinite(patch.yValue)) {
    point.yValue = patch.yValue;
  }

  return { document: next, changed: true };
}

export function updateMatrixBubblePoint(
  document: OVAReportDocument,
  chartId: string,
  seriesKey: string,
  pointKey: string,
  sizeValue: number
): CommandResult {
  const next = cloneDocument(document);
  const point = findSeriesItem(next, chartId, seriesKey, "points", (item) => item.key === pointKey);
  if (!point || !Number.isFinite(sizeValue)) {
    return { document, changed: false };
  }

  point.sizeValue = sizeValue;
  return { document: next, changed: true };
}

export function updateGridTableCellText(
  document: OVAReportDocument,
  tableId: string,
  rowIndex: number,
  cellIndex: number,
  text: string
): CommandResult {
  const next = cloneDocument(document);
  const table = next.datasets?.tables?.find((item) => item.id === tableId);
  const rows = Array.isArray(table?.rows) ? table.rows : undefined;
  const row = rows?.[rowIndex];
  const cells = isJSONObject(row) && Array.isArray(row.cells) ? row.cells : undefined;
  const cell = cells?.[cellIndex];

  if (!isJSONObject(cell)) {
    return { document, changed: false };
  }

  cell.text = text;
  return { document: next, changed: true };
}

export function plainBlockText(children: unknown): string {
  if (!Array.isArray(children)) {
    return "";
  }

  return children
    .map((child) => {
      if (child && typeof child === "object" && "text" in child) {
        const text = (child as { text?: unknown }).text;
        return typeof text === "string" ? text : "";
      }
      return "";
    })
    .join("");
}

function updateMultilingualText(
  current: MultilingualText | undefined,
  title: string,
  language: string
): MultilingualText {
  if (typeof current === "string" || current === undefined) {
    return title;
  }

  return {
    ...current,
    [language]: title || displayText(current, language)
  };
}

function createSection(id: string, title: string, level: number): OVASection {
  return {
    id,
    anchor: id,
    level,
    title,
    numbering: "auto",
    body: [
      {
        itemType: "content",
        blocks: [createParagraphBlock("")]
      }
    ]
  };
}

function createParagraphBlock(text: string): OVABlock {
  return {
    _type: "block",
    style: "normal",
    children: [{ _type: "span", text, marks: [] }],
    markDefs: []
  };
}

function addReferencedBlock(document: OVAReportDocument, sectionId: string, block: OVABlock): CommandResult {
  const next = cloneDocument(document);
  const section = flattenSections(next.sections).find((item) => item.id === sectionId)?.section;
  if (!section) {
    return { document, changed: false };
  }

  const ids = collectIds(next);
  const id = uniqueId(block._type ?? "block", ids);
  const content = ensureEditableContent(section);
  content.blocks = content.blocks ?? [];
  content.blocks.push({ ...block, id, anchor: id });

  return { document: next, changed: true };
}

function editableBlockSlots(
  document: OVAReportDocument,
  sectionId: string
): Array<{ blocks: OVABlock[]; index: number; block: OVABlock }> {
  const section = flattenSections(document.sections).find((item) => item.id === sectionId)?.section;
  const slots: Array<{ blocks: OVABlock[]; index: number; block: OVABlock }> = [];

  section?.body?.forEach((item) => {
    item.blocks?.forEach((block, index) => {
      slots.push({ blocks: item.blocks!, index, block });
    });
  });

  return slots;
}

function ensureEditableContent(section: OVASection): OVAContentItem {
  section.body = section.body ?? [];
  const content = section.body.find((item) => item.itemType === "content" && Array.isArray(item.blocks));
  if (content) {
    return content;
  }

  const created: OVAContentItem = { itemType: "content", blocks: [] };
  section.body.push(created);
  return created;
}

function cloneBlockWithIndependentData(
  document: OVAReportDocument,
  block: OVABlock,
  ids: Set<string>
): OVABlock {
  const copy = cloneDocument(block as OVAReportDocument) as OVABlock;

  const copyId = uniqueId(copy.id ?? copy.anchor ?? copy._type ?? "block", ids);
  copy.id = copyId;
  copy.anchor = copyId;
  ids.add(copyId);

  if (copy._type === "chart" && copy.chartRef) {
    const chart = document.datasets?.charts?.find((item) => item.id === copy.chartRef);
    if (chart) {
      const clonedChart = cloneJSONObject(chart);
      const newId = uniqueId(String(chart.id ?? "chart"), ids);
      clonedChart.id = newId;
      clonedChart.anchor = newId;
      clonedChart.label = appendCopyLabel(clonedChart.label);
      document.datasets = document.datasets ?? {};
      document.datasets.charts = document.datasets.charts ?? [];
      document.datasets.charts.push(clonedChart);
      copy.chartRef = newId;
      ids.add(newId);
    }
  }

  if (copy._type === "table" && copy.tableRef) {
    const table = document.datasets?.tables?.find((item) => item.id === copy.tableRef);
    if (table) {
      const clonedTable = cloneJSONObject(table);
      const newId = uniqueId(String(table.id ?? "table"), ids);
      clonedTable.id = newId;
      clonedTable.anchor = newId;
      clonedTable.label = appendCopyLabel(clonedTable.label);
      document.datasets = document.datasets ?? {};
      document.datasets.tables = document.datasets.tables ?? [];
      document.datasets.tables.push(clonedTable);
      copy.tableRef = newId;
      ids.add(newId);
    }
  }

  return copy;
}

function cloneJSONObject(value: JSONObject): JSONObject {
  return structuredClone(value);
}

function appendCopyLabel(label: unknown): JSONValue {
  if (typeof label === "string") {
    return `${label} Copy`;
  }
  if (label && typeof label === "object" && !Array.isArray(label)) {
    const next: JSONObject = {};
    Object.entries(label).forEach(([key, value]) => {
      next[key] = typeof value === "string" ? `${value} Copy` : toJSONValue(value);
    });
    return next;
  }
  return toJSONValue(label);
}

function isJSONObject(value: unknown): value is JSONObject {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function toJSONValue(value: unknown): JSONValue {
  if (
    value === null ||
    typeof value === "string" ||
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return value;
  }
  if (Array.isArray(value)) {
    return value.map(toJSONValue);
  }
  if (isJSONObject(value)) {
    const object: JSONObject = {};
    Object.entries(value).forEach(([key, entry]) => {
      object[key] = toJSONValue(entry);
    });
    return object;
  }
  return null;
}

function findSeriesItem(
  document: OVAReportDocument,
  chartId: string,
  seriesKey: string,
  collectionKey: "data" | "points",
  predicate: (item: JSONObject) => boolean
): JSONObject | undefined {
  const chart = document.datasets?.charts?.find((item) => item.id === chartId);
  const series = Array.isArray(chart?.series) ? chart.series : undefined;
  const targetSeries = series?.find((item) => isJSONObject(item) && item.key === seriesKey) as JSONObject | undefined;
  const collection = Array.isArray(targetSeries?.[collectionKey])
    ? targetSeries[collectionKey]
    : undefined;

  return collection?.find((item) => isJSONObject(item) && predicate(item)) as JSONObject | undefined;
}

function duplicateSectionInList(sections: OVASection[], sectionId: string, ids: Set<string>): string | undefined {
  for (let index = 0; index < sections.length; index += 1) {
    const section = sections[index];
    if (!section) {
      continue;
    }

    if ((section.id ?? section.anchor) === sectionId) {
      const copy = cloneSectionWithNewIds(section, ids);
      sections.splice(index + 1, 0, copy);
      return copy.id ?? copy.anchor;
    }

    const nestedId = duplicateSectionInBody(section.body ?? [], sectionId, ids);
    if (nestedId) {
      return nestedId;
    }
  }

  return undefined;
}

function duplicateSectionInBody(
  body: OVAContentItem[],
  sectionId: string,
  ids: Set<string>
): string | undefined {
  for (let index = 0; index < body.length; index += 1) {
    const item = body[index];
    if (item?.itemType !== "subsection" || !item.section) {
      continue;
    }

    if ((item.section.id ?? item.section.anchor) === sectionId) {
      const copy = cloneSectionWithNewIds(item.section, ids);
      body.splice(index + 1, 0, { itemType: "subsection", section: copy });
      return copy.id ?? copy.anchor;
    }

    const nestedId = duplicateSectionInBody(item.section.body ?? [], sectionId, ids);
    if (nestedId) {
      return nestedId;
    }
  }

  return undefined;
}

function cloneSectionWithNewIds(section: OVASection, ids: Set<string>): OVASection {
  const copy = structuredClone(section);
  remapSectionIds(copy, ids);
  return copy;
}

function remapSectionIds(section: OVASection, ids: Set<string>): void {
  const base = section.id ?? section.anchor ?? "section";
  const id = uniqueId(base, ids);
  section.id = id;
  section.anchor = id;
  ids.add(id);

  section.body?.forEach((item) => {
    item.blocks?.forEach((block) => {
      if (block.id) {
        block.id = uniqueId(block.id, ids);
        ids.add(block.id);
      }
      if (block.anchor) {
        block.anchor = block.id ?? uniqueId(block.anchor, ids);
        ids.add(block.anchor);
      }
    });
    if (item.itemType === "subsection" && item.section) {
      remapSectionIds(item.section, ids);
    }
  });
}

function removeSection(sections: OVASection[], sectionId: string): boolean {
  const index = sections.findIndex((section) => (section.id ?? section.anchor) === sectionId);
  if (index >= 0) {
    sections.splice(index, 1);
    return true;
  }

  for (const section of sections) {
    const body = section.body ?? [];
    const bodyIndex = body.findIndex(
      (item) => item.itemType === "subsection" && (item.section?.id ?? item.section?.anchor) === sectionId
    );
    if (bodyIndex >= 0) {
      body.splice(bodyIndex, 1);
      return true;
    }

    for (const item of body) {
      if (item.itemType === "subsection" && item.section && removeSection([item.section], sectionId)) {
        return true;
      }
    }
  }

  return false;
}

function detachSection(sections: OVASection[], sectionId: string): OVASection | undefined {
  const index = sections.findIndex((section) => (section.id ?? section.anchor) === sectionId);
  if (index >= 0) {
    return sections.splice(index, 1)[0];
  }

  for (const section of sections) {
    const body = section.body ?? [];
    const bodyIndex = body.findIndex(
      (item) => item.itemType === "subsection" && (item.section?.id ?? item.section?.anchor) === sectionId
    );
    if (bodyIndex >= 0) {
      const [item] = body.splice(bodyIndex, 1) as [OVAContentItem | undefined];
      return item?.section;
    }

    for (const item of body) {
      if (item.itemType === "subsection" && item.section) {
        const nested = detachSection([item.section], sectionId);
        if (nested) {
          return nested;
        }
      }
    }
  }

  return undefined;
}

function updateSectionLevels(section: OVASection, level: number): void {
  section.level = level;
  section.body?.forEach((item) => {
    if (item.itemType === "subsection" && item.section) {
      updateSectionLevels(item.section, level + 1);
    }
  });
}

function collectIds(document: OVAReportDocument): Set<string> {
  const validation = validateDocument(document);
  return new Set([
    ...validation.referenceIndex.ids.keys(),
    ...validation.referenceIndex.anchors.keys(),
    ...validation.referenceIndex.resources.charts.keys(),
    ...validation.referenceIndex.resources.tables.keys(),
    ...validation.referenceIndex.resources.images.keys()
  ]);
}

function uniqueId(base: string, existing: Set<string>): string {
  const safeBase = slugify(base) || "item";
  if (!existing.has(safeBase)) {
    return safeBase;
  }

  let suffix = 2;
  while (existing.has(`${safeBase}-${suffix}`)) {
    suffix += 1;
  }
  return `${safeBase}-${suffix}`;
}

function slugify(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function normalizeLevel(level: unknown): number {
  return typeof level === "number" && Number.isFinite(level) ? level : 1;
}

function clampIndex(index: number, length: number): number {
  if (!Number.isFinite(index)) {
    return length;
  }
  return Math.max(0, Math.min(length, Math.trunc(index)));
}

function isProtectedSection(section: OVASection): boolean {
  return section.sectionRole === "cover" || section.sectionRole === "toc" || section.sectionRole === "backCover";
}

function withSelection(
  document: OVAReportDocument,
  changed: boolean,
  selectionId: string | undefined
): CommandResult {
  return selectionId ? { document, changed, selectionId } : { document, changed };
}
