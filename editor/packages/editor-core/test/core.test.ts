import { describe, expect, it } from "vitest";
import fixture from "../../../fixtures/report-v1.3-company.json";
import {
  addSection,
  buildSectionTree,
  deleteBlock,
  duplicateBlock,
  displayText,
  flattenSections,
  loadDocument,
  stringifyDocument,
  updateBarChartCategory,
  updateBarChartValue,
  updateChartLabel,
  updateChartSlice,
  updateGridTableCellText,
  updateLineChartPoint,
  updateMatrixBubblePoint,
  updateTextBlock,
  validateDocument
} from "../src";

describe("editor core", () => {
  it("loads and exports the golden fixture", () => {
    const loaded = loadDocument(fixture);

    expect(loaded.ok).toBe(true);
    expect(loaded.document?.schemaVersion).toBe("report.v1.3");
    expect(stringifyDocument(loaded.document!, true)).toContain("Company Valuation Report");
  });

  it("builds the section tree", () => {
    const tree = buildSectionTree(fixture.sections);

    expect(tree.length).toBeGreaterThan(0);
    expect(tree.some((section) => section.children.length > 0)).toBe(true);
  });

  it("builds reference validation information", () => {
    const result = validateDocument(fixture);

    expect(result.referenceIndex.resources.charts.size).toBe(13);
    expect(result.referenceIndex.resources.tables.size).toBe(10);
  });

  it("adds a top-level section with a unique id", () => {
    const result = addSection(fixture, { title: "New Analysis" });

    expect(result.changed).toBe(true);
    expect(result.selectionId).toBe("new-analysis");
    expect(result.document.sections?.at(-1)?.id).toBe("new-analysis");
  });

  it("deletes a chart block without deleting its dataset", () => {
    const found = findFirstChartBlock();
    const before = fixture.datasets.charts.length;
    const result = deleteBlock(fixture, found.sectionId, found.blockIndex);

    expect(result.changed).toBe(true);
    expect(result.document.datasets?.charts?.length).toBe(before);
  });

  it("duplicates a chart block with an independent cloned dataset", () => {
    const found = findFirstChartBlock();
    const before = fixture.datasets.charts.length;
    const result = duplicateBlock(fixture, found.sectionId, found.blockIndex);

    expect(result.changed).toBe(true);
    expect(result.document.datasets?.charts?.length).toBe(before + 1);
  });

  it("updates a selected text block by section block index", () => {
    const found = findTextBlockAfterFirst();
    const result = updateTextBlock(fixture, found.sectionId, found.blockIndex, "Updated selected block");
    const updated = flattenSections(result.document.sections)
      .find((node) => node.id === found.sectionId)
      ?.section.body?.flatMap((item) => item.blocks ?? [])
      ?.[found.blockIndex];

    expect(result.changed).toBe(true);
    expect(updated?.children?.[0]?.text).toBe("Updated selected block");
  });

  it("updates chart labels and pie slices without replacing the dataset", () => {
    const chart = fixture.datasets.charts[0]!;
    const slice = chart.slices[0]!;
    const labeled = updateChartLabel(fixture, chart.id, "Updated Chart Label");
    const sliced = updateChartSlice(labeled.document, chart.id, slice.key, {
      label: "Updated Slice",
      value: 0.5
    });

    expect(labeled.changed).toBe(true);
    expect(sliced.changed).toBe(true);
    expect(sliced.document.datasets?.charts?.[0]?.label).toBe("Updated Chart Label");
    expect(displayText(sliced.document.datasets?.charts?.[0]?.slices?.[0]?.label)).toBe("Updated Slice");
    expect(sliced.document.datasets?.charts?.[0]?.slices?.[0]?.value).toBe(0.5);
  });

  it("updates grid table cell text while preserving span fields", () => {
    const table = fixture.datasets.tables[0]!;
    const result = updateGridTableCellText(fixture, table.id, 0, 1, "Updated Company");
    const cell = result.document.datasets?.tables?.[0]?.rows?.[0]?.cells?.[1];

    expect(result.changed).toBe(true);
    expect(cell?.text).toBe("Updated Company");
    expect(cell?.colSpan).toBe(1);
    expect(cell?.rowSpan).toBe(1);
  });

  it("updates bar chart categories and values", () => {
    const chart = fixture.datasets.charts.find((item) => item.chartType === "bar")!;
    const series = chart.series[0]!;
    const category = chart.categories[0]!;
    const labeled = updateBarChartCategory(fixture, chart.id, category.key, "Updated Category");
    const valued = updateBarChartValue(labeled.document, chart.id, series.key, category.key, 42);
    const updatedChart = valued.document.datasets?.charts?.find((item) => item.id === chart.id);

    expect(labeled.changed).toBe(true);
    expect(valued.changed).toBe(true);
    expect(displayText(updatedChart?.categories?.[0]?.label)).toBe("Updated Category");
    expect(updatedChart?.series?.[0]?.data?.[0]?.value).toBe(42);
  });

  it("updates line chart point fields", () => {
    const chart = fixture.datasets.charts.find((item) => item.chartType === "line")!;
    const series = chart.series[0]!;
    const point = series.points[0]!;
    const result = updateLineChartPoint(fixture, chart.id, series.key, point.key, {
      label: "Updated Point",
      xValue: 11,
      yValue: 22
    });
    const updatedPoint = result.document.datasets?.charts
      ?.find((item) => item.id === chart.id)
      ?.series?.[0]?.points?.[0];

    expect(result.changed).toBe(true);
    expect(displayText(updatedPoint?.label)).toBe("Updated Point");
    expect(updatedPoint?.xValue).toBe(11);
    expect(updatedPoint?.yValue).toBe(22);
  });

  it("updates matrix bubble point size", () => {
    const chart = fixture.datasets.charts.find((item) => item.chartType === "matrix_bubble")!;
    const series = chart.series[0]!;
    const point = series.points[0]!;
    const result = updateMatrixBubblePoint(fixture, chart.id, series.key, point.key, 7);
    const updatedPoint = result.document.datasets?.charts
      ?.find((item) => item.id === chart.id)
      ?.series?.[0]?.points?.[0];

    expect(result.changed).toBe(true);
    expect(updatedPoint?.sizeValue).toBe(7);
  });
});

function findFirstChartBlock(): { sectionId: string; blockIndex: number } {
  for (const node of flattenSections(fixture.sections)) {
    const section = node.section;
    let blockIndex = 0;
    for (const item of section.body ?? []) {
      for (const block of item.blocks ?? []) {
        if (block._type === "chart") {
          return { sectionId: node.id, blockIndex };
        }
        blockIndex += 1;
      }
    }
  }

  throw new Error("Fixture does not contain a top-level chart block.");
}

function findTextBlockAfterFirst(): { sectionId: string; blockIndex: number } {
  for (const node of flattenSections(fixture.sections)) {
    const blocks = node.section.body?.flatMap((item) => item.blocks ?? []) ?? [];
    const firstTextIndex = blocks.findIndex((block) => block._type === "block");
    const secondTextIndex = blocks.findIndex((block, index) => index > firstTextIndex && block._type === "block");
    if (firstTextIndex >= 0 && secondTextIndex >= 0) {
      return { sectionId: node.id, blockIndex: secondTextIndex };
    }
  }

  throw new Error("Fixture does not contain a second text block in one section.");
}
