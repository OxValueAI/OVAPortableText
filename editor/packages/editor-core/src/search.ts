import type { OVAReportDocument } from "./types";
import { plainBlockText } from "./commands";
import { flattenSections } from "./sections";

export interface SearchResult {
  label: string;
  path: string;
  kind: "section" | "text" | "chart" | "table";
}

export function searchDocument(document: OVAReportDocument, query: string): SearchResult[] {
  const needle = query.trim().toLowerCase();
  if (!needle) {
    return [];
  }

  const results: SearchResult[] = [];

  flattenSections(document.sections).forEach((node) => {
    if (node.title.toLowerCase().includes(needle)) {
      results.push({ label: node.title || node.id, path: node.path, kind: "section" });
    }

    node.section.body?.forEach((item, itemIndex) => {
      item.blocks?.forEach((block, blockIndex) => {
        const text = plainBlockText(block.children);
        if (text.toLowerCase().includes(needle)) {
          results.push({
            label: text.slice(0, 120),
            path: `${node.path}.body[${itemIndex}].blocks[${blockIndex}]`,
            kind: "text"
          });
        }
      });
    });
  });

  document.datasets?.charts?.forEach((chart, index) => {
    const label = typeof chart.label === "string" ? chart.label : String(chart.id ?? "");
    if (label.toLowerCase().includes(needle)) {
      results.push({ label, path: `$.datasets.charts[${index}]`, kind: "chart" });
    }
  });

  document.datasets?.tables?.forEach((table, index) => {
    const label = typeof table.label === "string" ? table.label : String(table.id ?? "");
    if (label.toLowerCase().includes(needle)) {
      results.push({ label, path: `$.datasets.tables[${index}]`, kind: "table" });
    }
  });

  return results;
}
