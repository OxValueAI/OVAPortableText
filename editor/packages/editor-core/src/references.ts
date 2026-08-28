import type {
  JSONObject,
  OVAReportDocument,
  OVASection,
  OVABlock,
  ReferenceIndex,
  ReferenceUsage
} from "./types";

export function buildReferenceIndex(document: OVAReportDocument): ReferenceIndex {
  const index: ReferenceIndex = {
    ids: new Map(),
    anchors: new Map(),
    resources: {
      charts: new Map(),
      tables: new Map(),
      images: new Map()
    },
    usagesByRef: new Map(),
    outgoing: []
  };

  document.datasets?.charts?.forEach((chart, i) => registerResource(index, "charts", chart, `$.datasets.charts[${i}]`));
  document.datasets?.tables?.forEach((table, i) => registerResource(index, "tables", table, `$.datasets.tables[${i}]`));
  document.assets?.images?.forEach((image, i) => registerResource(index, "images", image, `$.assets.images[${i}]`));

  document.sections?.forEach((section, i) => visitSection(index, section, `$.sections[${i}]`));

  return index;
}

export function getUsages(index: ReferenceIndex, ref: string): ReferenceUsage[] {
  return index.usagesByRef.get(ref) ?? [];
}

export function unusedResourceIds(index: ReferenceIndex, kind: "charts" | "tables" | "images"): string[] {
  return [...index.resources[kind].keys()].filter((id) => getUsages(index, id).length === 0);
}

function registerResource(
  index: ReferenceIndex,
  kind: keyof ReferenceIndex["resources"],
  object: JSONObject,
  path: string
): void {
  const id = typeof object.id === "string" ? object.id : undefined;
  const anchor = typeof object.anchor === "string" ? object.anchor : undefined;

  if (id) {
    index.resources[kind].set(id, object);
    appendPath(index.ids, id, path);
  }
  if (anchor) {
    appendPath(index.anchors, anchor, path);
  }
}

function visitSection(index: ReferenceIndex, section: OVASection, path: string): void {
  if (section.id) {
    appendPath(index.ids, section.id, path);
  }
  if (section.anchor) {
    appendPath(index.anchors, section.anchor, path);
  }

  section.body?.forEach((item, itemIndex) => {
    const itemPath = `${path}.body[${itemIndex}]`;

    if (item.itemType === "subsection" && item.section) {
      visitSection(index, item.section, `${itemPath}.section`);
      return;
    }

    item.blocks?.forEach((block, blockIndex) => {
      visitBlock(index, block, `${itemPath}.blocks[${blockIndex}]`);
    });
  });
}

function visitBlock(index: ReferenceIndex, block: OVABlock, path: string): void {
  if (block.id) {
    appendPath(index.ids, block.id, path);
  }
  if (block.anchor) {
    appendPath(index.anchors, block.anchor, path);
  }

  if (block.chartRef) {
    addUsage(index, { kind: "chart", ref: block.chartRef, path, sourceType: block._type ?? "unknown" });
  }
  if (block.tableRef) {
    addUsage(index, { kind: "table", ref: block.tableRef, path, sourceType: block._type ?? "unknown" });
  }
  if (block.imageRef) {
    addUsage(index, { kind: "image", ref: block.imageRef, path, sourceType: block._type ?? "unknown" });
  }

  block.markDefs?.forEach((markDef, markIndex) => {
    const markPath = `${path}.markDefs[${markIndex}]`;
    const type = typeof markDef._type === "string" ? markDef._type : "";
    const ref = extractMarkReference(type, markDef);
    if (ref) {
      addUsage(index, {
        kind: ref.kind,
        ref: ref.value,
        path: markPath,
        sourceType: type
      });
    }
  });
}

function extractMarkReference(
  type: string,
  markDef: JSONObject
): Pick<ReferenceUsage, "kind"> & { value: string } | undefined {
  if (type === "xref" && typeof markDef.target === "string") {
    return { kind: "xref", value: markDef.target };
  }
  if (type === "citation_ref" && typeof markDef.citationRef === "string") {
    return { kind: "citation", value: markDef.citationRef };
  }
  if (type === "footnote_ref" && typeof markDef.footnoteRef === "string") {
    return { kind: "footnote", value: markDef.footnoteRef };
  }
  if (type === "glossary_term" && typeof markDef.termRef === "string") {
    return { kind: "glossary", value: markDef.termRef };
  }
  return undefined;
}

function addUsage(index: ReferenceIndex, usage: ReferenceUsage): void {
  index.outgoing.push(usage);
  const usages = index.usagesByRef.get(usage.ref) ?? [];
  usages.push(usage);
  index.usagesByRef.set(usage.ref, usages);
}

function appendPath(map: Map<string, string[]>, key: string, path: string): void {
  const paths = map.get(key) ?? [];
  paths.push(path);
  map.set(key, paths);
}
