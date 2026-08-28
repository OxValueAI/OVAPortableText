export type JSONObject = { [key: string]: JSONValue };
export type JSONArray = JSONValue[];
export type JSONValue = string | number | boolean | null | JSONObject | JSONArray;

export type MultilingualText = string | Record<string, string>;

export interface OVAReportDocument extends JSONObject {
  schemaVersion?: string;
  meta?: JSONObject & {
    title?: MultilingualText;
    language?: string;
    documentType?: string;
  };
  assets?: JSONObject & {
    images?: JSONObject[];
  };
  datasets?: JSONObject & {
    charts?: JSONObject[];
    tables?: JSONObject[];
  };
  bibliography?: JSONObject[];
  footnotes?: JSONObject[];
  glossary?: JSONObject[];
  sections?: OVASection[];
}

export interface OVASection extends JSONObject {
  id?: string;
  anchor?: string;
  level?: number;
  title?: MultilingualText;
  numbering?: string;
  sectionRole?: string;
  body?: OVAContentItem[];
}

export interface OVAContentItem extends JSONObject {
  itemType?: string;
  blocks?: OVABlock[];
  section?: OVASection;
}

export interface OVABlock extends JSONObject {
  _type?: string;
  id?: string;
  anchor?: string;
  chartRef?: string;
  tableRef?: string;
  imageRef?: string;
  children?: JSONObject[];
  markDefs?: JSONObject[];
}

export type Severity = "error" | "warning" | "info";

export interface EditorIssue {
  code: string;
  severity: Severity;
  message: string;
  path: string;
}

export interface LoadResult {
  ok: boolean;
  document?: OVAReportDocument;
  sourceText?: string;
  issues: EditorIssue[];
}

export interface SectionNode {
  id: string;
  title: string;
  level: number;
  path: string;
  section: OVASection;
  children: SectionNode[];
}

export interface ReferenceUsage {
  kind: "chart" | "table" | "image" | "xref" | "citation" | "footnote" | "glossary";
  ref: string;
  path: string;
  sourceType: string;
}

export interface ReferenceIndex {
  ids: Map<string, string[]>;
  anchors: Map<string, string[]>;
  resources: {
    charts: Map<string, JSONObject>;
    tables: Map<string, JSONObject>;
    images: Map<string, JSONObject>;
  };
  usagesByRef: Map<string, ReferenceUsage[]>;
  outgoing: ReferenceUsage[];
}
