import type { MultilingualText, OVASection, SectionNode } from "./types";

export function buildSectionTree(sections: OVASection[] | undefined): SectionNode[] {
  if (!Array.isArray(sections)) {
    return [];
  }

  return sections.map((section, index) => buildSectionNode(section, `$.sections[${index}]`));
}

export function flattenSections(sections: OVASection[] | undefined): SectionNode[] {
  const roots = buildSectionTree(sections);
  const out: SectionNode[] = [];

  const visit = (node: SectionNode) => {
    out.push(node);
    node.children.forEach(visit);
  };

  roots.forEach(visit);
  return out;
}

export function displayText(value: MultilingualText | undefined, language = "en"): string {
  if (typeof value === "string") {
    return value;
  }
  if (value && typeof value === "object") {
    return value[language] ?? value.en ?? Object.values(value)[0] ?? "";
  }
  return "";
}

function buildSectionNode(section: OVASection, path: string): SectionNode {
  const children: SectionNode[] = [];

  if (Array.isArray(section.body)) {
    section.body.forEach((item, index) => {
      if (item?.itemType === "subsection" && item.section) {
        children.push(buildSectionNode(item.section, `${path}.body[${index}].section`));
      }
    });
  }

  return {
    id: section.id ?? section.anchor ?? path,
    title: displayText(section.title),
    level: typeof section.level === "number" ? section.level : 1,
    path,
    section,
    children
  };
}
