import type { EditorIssue, OVAReportDocument, ReferenceIndex } from "./types";
import { buildReferenceIndex, unusedResourceIds } from "./references";

export interface ValidationResult {
  valid: boolean;
  issues: EditorIssue[];
  referenceIndex: ReferenceIndex;
}

export function validateDocument(document: OVAReportDocument): ValidationResult {
  const referenceIndex = buildReferenceIndex(document);
  const issues: EditorIssue[] = [];

  if (document.schemaVersion !== "report.v1.3") {
    issues.push({
      code: "protocol.schema_version",
      severity: "warning",
      message: `Expected schemaVersion "report.v1.3", received "${document.schemaVersion ?? "missing"}".`,
      path: "$.schemaVersion"
    });
  }

  if (!Array.isArray(document.sections)) {
    issues.push({
      code: "protocol.sections_missing",
      severity: "error",
      message: "Document must contain a sections array.",
      path: "$.sections"
    });
  }

  pushDuplicateIssues(issues, referenceIndex.ids, "id");
  pushDuplicateIssues(issues, referenceIndex.anchors, "anchor");
  pushDanglingReferenceIssues(issues, referenceIndex);
  pushUnusedResourceWarnings(issues, referenceIndex);

  return {
    valid: !issues.some((issue) => issue.severity === "error"),
    issues,
    referenceIndex
  };
}

function pushDuplicateIssues(issues: EditorIssue[], values: Map<string, string[]>, field: string): void {
  values.forEach((paths, value) => {
    if (paths.length > 1) {
      issues.push({
        code: `reference.duplicate_${field}`,
        severity: "error",
        message: `Duplicate ${field} "${value}" appears ${paths.length} times.`,
        path: paths[0] ?? "$"
      });
    }
  });
}

function pushDanglingReferenceIssues(issues: EditorIssue[], index: ReferenceIndex): void {
  index.outgoing.forEach((usage) => {
    const exists =
      (usage.kind === "chart" && index.resources.charts.has(usage.ref)) ||
      (usage.kind === "table" && index.resources.tables.has(usage.ref)) ||
      (usage.kind === "image" && index.resources.images.has(usage.ref)) ||
      (usage.kind === "xref" && (index.ids.has(usage.ref) || index.anchors.has(usage.ref))) ||
      usage.kind === "citation" ||
      usage.kind === "footnote" ||
      usage.kind === "glossary";

    if (!exists) {
      issues.push({
        code: "reference.dangling",
        severity: "error",
        message: `Dangling ${usage.kind} reference "${usage.ref}".`,
        path: usage.path
      });
    }
  });
}

function pushUnusedResourceWarnings(issues: EditorIssue[], index: ReferenceIndex): void {
  (["charts", "tables", "images"] as const).forEach((kind) => {
    unusedResourceIds(index, kind).forEach((id) => {
      issues.push({
        code: "reference.unused_resource",
        severity: "warning",
        message: `Unused ${kind.slice(0, -1)} resource "${id}".`,
        path: `$.*.${kind}[id="${id}"]`
      });
    });
  });
}
