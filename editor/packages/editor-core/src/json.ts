import type { EditorIssue, LoadResult, OVAReportDocument } from "./types";

export function parseJSONSource(sourceText: string): LoadResult {
  try {
    const parsed = JSON.parse(sourceText) as unknown;
    if (!isPlainObject(parsed)) {
      return {
        ok: false,
        sourceText,
        issues: [
          {
            code: "json.root_type",
            severity: "error",
            message: "The root JSON value must be an object.",
            path: "$"
          }
        ]
      };
    }

    return {
      ok: true,
      document: parsed as OVAReportDocument,
      sourceText,
      issues: []
    };
  } catch (error) {
    return {
      ok: false,
      sourceText,
      issues: [
        {
          code: "json.syntax",
          severity: "error",
          message: error instanceof Error ? error.message : "Invalid JSON syntax.",
          path: "$"
        }
      ]
    };
  }
}

export function loadDocument(value: object | string): LoadResult {
  if (typeof value === "string") {
    return parseJSONSource(value);
  }

  if (!isPlainObject(value)) {
    return {
      ok: false,
      issues: [
        {
          code: "json.root_type",
          severity: "error",
          message: "The loaded value must be a plain object.",
          path: "$"
        }
      ]
    };
  }

  return {
    ok: true,
    document: structuredClone(value) as OVAReportDocument,
    sourceText: stringifyDocument(value as OVAReportDocument, true),
    issues: []
  };
}

export function stringifyDocument(document: OVAReportDocument, pretty = true): string {
  return JSON.stringify(document, null, pretty ? 2 : 0);
}

export function cloneDocument(document: OVAReportDocument): OVAReportDocument {
  return structuredClone(document);
}

export function toIssue(error: unknown, path = "$"): EditorIssue {
  return {
    code: "editor.exception",
    severity: "error",
    message: error instanceof Error ? error.message : String(error),
    path
  };
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
