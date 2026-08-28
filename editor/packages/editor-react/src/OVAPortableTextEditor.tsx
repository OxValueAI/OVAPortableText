import {
  addParagraphBlock,
  addSection,
  buildSectionTree,
  deleteBlock,
  deleteSection,
  duplicateBlock,
  duplicateSection,
  displayText,
  deleteVersion as deleteBrowserVersion,
  loadDocument,
  listVersions as listBrowserVersions,
  loadVersion as loadBrowserVersion,
  moveBlock,
  renameVersion as renameBrowserVersion,
  searchDocument,
  saveVersion as saveBrowserVersion,
  stringifyDocument,
  updateBarChartCategory,
  updateBarChartValue,
  updateChartLabel,
  updateChartSlice,
  updateFirstTextBlock,
  updateGridTableCellText,
  updateLineChartPoint,
  updateMatrixBubblePoint,
  updateSectionTitle,
  validateDocument,
  type BrowserVersioningOptions,
  type EditorIssue,
  type OVAReportDocument,
  type SectionNode,
  type CommandResult,
  type JSONObject,
  type SavedVersion,
  type SavedVersionMeta
} from "@ova/portable-text-editor-core";
import {
  forwardRef,
  useEffect,
  useImperativeHandle,
  useMemo,
  useRef,
  useState,
  type ReactNode
} from "react";
import "./styles.css";

export interface OVAPortableTextEditorHandle {
  setValue(value: object | string): Promise<{ ok: boolean; issues: EditorIssue[] }>;
  getValue(): OVAReportDocument | undefined;
  getJSONString(pretty?: boolean): string;
  validate(): ReturnType<typeof validateDocument> | undefined;
  setMode(mode: "visual" | "json"): void;
  undo(): void;
  redo(): void;
  isDirty(): boolean;
  saveVersion(label?: string): Promise<SavedVersion | undefined>;
  listVersions(): Promise<SavedVersionMeta[]>;
  loadVersion(versionId: string): Promise<{ ok: boolean; issues: EditorIssue[] }>;
}

export interface OVAPortableTextEditorProps {
  initialValue?: object | string;
  readOnly?: boolean;
  versioning?: BrowserVersioningOptions;
  onSave?: (document: OVAReportDocument) => void | Promise<void>;
  onDirtyChange?: (dirty: boolean) => void;
  onValidationChange?: (result: ReturnType<typeof validateDocument>) => void;
  onRequestFinalPreview?: (document: OVAReportDocument) => void;
}

export const OVAPortableTextEditor = forwardRef<
  OVAPortableTextEditorHandle,
  OVAPortableTextEditorProps
>(function OVAPortableTextEditor(props, ref) {
  const [document, setDocument] = useState<OVAReportDocument>();
  const [sourceText, setSourceText] = useState("");
  const [mode, setMode] = useState<"visual" | "json">("visual");
  const [selectedSectionId, setSelectedSectionId] = useState<string>();
  const [dirty, setDirty] = useState(false);
  const [sourceState, setSourceState] = useState<"SYNCED" | "DRAFT" | "INVALID">("SYNCED");
  const [query, setQuery] = useState("");
  const [versions, setVersions] = useState<SavedVersionMeta[]>([]);
  const [versionError, setVersionError] = useState<string>();
  const [past, setPast] = useState<OVAReportDocument[]>([]);
  const [future, setFuture] = useState<OVAReportDocument[]>([]);
  const [selectedResource, setSelectedResource] = useState<{ kind: "chart" | "table"; id: string }>();
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (props.initialValue === undefined) {
      return;
    }
    const loaded = loadDocument(props.initialValue);
    if (loaded.document) {
      setDocument(loaded.document);
      setSourceText(stringifyDocument(loaded.document, true));
      setSelectedSectionId(buildSectionTree(loaded.document.sections)[0]?.id);
      setPast([]);
      setFuture([]);
      setDirty(false);
    }
  }, [props.initialValue]);

  useEffect(() => {
    props.onDirtyChange?.(dirty);
  }, [dirty, props.onDirtyChange]);

  const validation = useMemo(() => (document ? validateDocument(document) : undefined), [document]);
  const sections = useMemo(() => buildSectionTree(document?.sections), [document]);
  const selectedSection = useMemo(
    () => findSection(sections, selectedSectionId) ?? sections[0],
    [sections, selectedSectionId]
  );
  const searchResults = useMemo(
    () => (document ? searchDocument(document, query) : []),
    [document, query]
  );
  const visualLocked = Boolean(props.readOnly || sourceState !== "SYNCED");
  const versioningEnabled = Boolean(props.versioning?.enabled && props.versioning.documentKey);

  useEffect(() => {
    if (validation) {
      props.onValidationChange?.(validation);
    }
  }, [props.onValidationChange, validation]);

  const applyCommand = (result: CommandResult) => {
    if (!result.changed) {
      return;
    }
    if (document) {
      setPast((current) => [...current, document]);
      setFuture([]);
    }
    setDocument(result.document);
    setSourceText(stringifyDocument(result.document, true));
    setSourceState("SYNCED");
    if (result.selectionId) {
      setSelectedSectionId(result.selectionId);
    }
    setDirty(true);
  };

  const applySource = () => {
    const loaded = loadDocument(sourceText);
    if (loaded.document) {
      setDocument(loaded.document);
      setSourceState("SYNCED");
      setPast((current) => (document ? [...current, document] : current));
      setFuture([]);
      setDirty(true);
      setSelectedSectionId(buildSectionTree(loaded.document.sections)[0]?.id);
      return;
    }
    setSourceState("INVALID");
  };

  const save = async () => {
    if (!document) {
      return;
    }
    await props.onSave?.(document);
    setDirty(false);
  };

  const undo = () => {
    const previous = past.at(-1);
    if (!previous || !document) {
      return;
    }

    setPast((current) => current.slice(0, -1));
    setFuture((current) => [document, ...current]);
    setDocument(previous);
    setSourceText(stringifyDocument(previous, true));
    setSourceState("SYNCED");
    setDirty(true);
  };

  const redo = () => {
    const next = future[0];
    if (!next || !document) {
      return;
    }

    setFuture((current) => current.slice(1));
    setPast((current) => [...current, document]);
    setDocument(next);
    setSourceText(stringifyDocument(next, true));
    setSourceState("SYNCED");
    setDirty(true);
  };

  const openJSONFile = async (file: File | undefined) => {
    if (!file) {
      return;
    }
    if (dirty && !window.confirm("Current document has unsaved changes. Discard them and open another JSON file?")) {
      return;
    }

    const text = await file.text();
    const loaded = loadDocument(text);
    if (loaded.document) {
      setDocument(loaded.document);
      setSourceText(stringifyDocument(loaded.document, true));
      setSourceState("SYNCED");
      setPast([]);
      setFuture([]);
      setDirty(false);
      setSelectedSectionId(buildSectionTree(loaded.document.sections)[0]?.id);
    } else {
      setSourceText(text);
      setSourceState("INVALID");
      setMode("json");
    }
  };

  const copyJSON = async () => {
    if (!document) {
      return;
    }
    await navigator.clipboard.writeText(stringifyDocument(document, true));
  };

  const downloadJSON = () => {
    if (!document) {
      return;
    }
    const blob = new Blob([stringifyDocument(document, true)], { type: "application/json;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = window.document.createElement("a");
    link.href = url;
    link.download = `${document.meta?.documentType ?? "ova-report"}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const refreshVersions = async () => {
    if (!props.versioning?.enabled) {
      setVersions([]);
      return;
    }

    try {
      setVersionError(undefined);
      setVersions(await listBrowserVersions(props.versioning));
    } catch (error) {
      setVersionError(error instanceof Error ? error.message : String(error));
    }
  };

  const saveLocalVersion = async () => {
    if (!document || !props.versioning?.enabled) {
      return;
    }

    try {
      setVersionError(undefined);
      await saveBrowserVersion(document, props.versioning);
      await refreshVersions();
      setDirty(false);
    } catch (error) {
      setVersionError(error instanceof Error ? error.message : String(error));
    }
  };

  const loadLocalVersion = async (versionId: string) => {
    if (!props.versioning?.enabled) {
      return;
    }
    if (dirty && !window.confirm("Current document has unsaved changes. Discard them and load this version?")) {
      return;
    }

    try {
      setVersionError(undefined);
      const version = await loadBrowserVersion(props.versioning, versionId);
      if (!version) {
        return;
      }
      setDocument(version.document);
      setSourceText(stringifyDocument(version.document, true));
      setSourceState("SYNCED");
      setDirty(false);
      setPast([]);
      setFuture([]);
      setSelectedSectionId(buildSectionTree(version.document.sections)[0]?.id);
    } catch (error) {
      setVersionError(error instanceof Error ? error.message : String(error));
    }
  };

  useImperativeHandle(ref, () => ({
    async setValue(value) {
      if (dirty) {
        return {
          ok: false,
          issues: [
            {
              code: "dirty.set_value_blocked",
              severity: "warning",
              message: "Current document has unsaved changes.",
              path: "$"
            }
          ]
        };
      }

      const loaded = loadDocument(value);
      if (loaded.document) {
        setDocument(loaded.document);
        setSourceText(stringifyDocument(loaded.document, true));
        setSourceState("SYNCED");
        setPast([]);
        setFuture([]);
        setDirty(false);
      }
      return { ok: loaded.ok, issues: loaded.issues };
    },
    getValue: () => document,
    getJSONString: (pretty = true) => (document ? stringifyDocument(document, pretty) : ""),
    validate: () => (document ? validateDocument(document) : undefined),
    setMode,
    undo,
    redo,
    isDirty: () => dirty,
    async saveVersion(label) {
      if (!document || !props.versioning?.enabled) {
        return undefined;
      }
      const version = await saveBrowserVersion(document, props.versioning, label);
      await refreshVersions();
      return version;
    },
    async listVersions() {
      return props.versioning?.enabled ? listBrowserVersions(props.versioning) : [];
    },
    async loadVersion(versionId) {
      if (!props.versioning?.enabled) {
        return {
          ok: false,
          issues: [{
            code: "versioning.disabled",
            severity: "warning",
            message: "Browser versioning is disabled.",
            path: "$"
          }]
        };
      }
      const version = await loadBrowserVersion(props.versioning, versionId);
      if (!version) {
        return {
          ok: false,
          issues: [{
            code: "versioning.not_found",
            severity: "warning",
            message: "Local version not found.",
            path: "$"
          }]
        };
      }
      setDocument(version.document);
      setSourceText(stringifyDocument(version.document, true));
      setSourceState("SYNCED");
      setPast([]);
      setFuture([]);
      setDirty(false);
      setSelectedSectionId(buildSectionTree(version.document.sections)[0]?.id);
      return { ok: true, issues: [] };
    }
  }));

  useEffect(() => {
    void refreshVersions();
  }, [props.versioning?.enabled, props.versioning?.documentKey, props.versioning?.namespace]);

  useEffect(() => {
    const handler = (event: BeforeUnloadEvent) => {
      if (!dirty) {
        return;
      }
      event.preventDefault();
      event.returnValue = "";
    };

    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, [dirty]);

  if (!document) {
    return <div className="ova-pte-shell ova-pte-empty">Open or paste OVAPortableText JSON to begin.</div>;
  }

  return (
    <div className="ova-pte-shell">
      <header className="ova-pte-toolbar">
        <button className={mode === "visual" ? "active" : ""} onClick={() => setMode("visual")}>Visual</button>
        <button className={mode === "json" ? "active" : ""} onClick={() => setMode("json")}>JSON</button>
        <input
          ref={fileInputRef}
          type="file"
          accept="application/json,.json"
          hidden
          onChange={(event) => {
            void openJSONFile(event.currentTarget.files?.[0]);
            event.currentTarget.value = "";
          }}
        />
        <button onClick={() => fileInputRef.current?.click()}>Open</button>
        <button onClick={copyJSON}>Copy JSON</button>
        <button onClick={downloadJSON}>Download</button>
        <input
          aria-label="Find"
          placeholder="Find"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
        <button disabled={past.length === 0} onClick={undo}>Undo</button>
        <button disabled={future.length === 0} onClick={redo}>Redo</button>
        <button onClick={() => validation && props.onValidationChange?.(validation)}>Validate</button>
        <button disabled={!props.onRequestFinalPreview} onClick={() => props.onRequestFinalPreview?.(document)}>
          Final Preview
        </button>
        <button onClick={save}>Save</button>
        <button disabled={!versioningEnabled} onClick={saveLocalVersion}>Save Version</button>
        <button disabled={visualLocked} onClick={() => applyCommand(addSection(document))}>Add Section</button>
        <button
          disabled={visualLocked || !selectedSection}
          onClick={() => selectedSection && applyCommand(addSection(document, { parentSectionId: selectedSection.id }))}
        >
          Add Subsection
        </button>
        <button
          disabled={visualLocked || !selectedSection}
          onClick={() => selectedSection && applyCommand(duplicateSection(document, selectedSection.id))}
        >
          Duplicate Section
        </button>
        <button
          disabled={visualLocked || !selectedSection}
          onClick={() => selectedSection && applyCommand(deleteSection(document, selectedSection.id))}
        >
          Delete Section
        </button>
        <span>{dirty ? "Modified" : "Saved"} - {validation?.issues.filter((issue) => issue.severity === "error").length ?? 0} Errors - {validation?.issues.filter((issue) => issue.severity === "warning").length ?? 0} Warnings</span>
      </header>

      <main className="ova-pte-grid">
        <aside className="ova-pte-sidebar">
          <Panel title="Outline">
            <SectionTree nodes={sections} selectedId={selectedSection?.id} onSelect={setSelectedSectionId} />
          </Panel>
          <Panel title="Resources">
            <ResourceStats
              document={document}
              validation={validation}
              selectedResource={selectedResource}
              onSelectResource={setSelectedResource}
            />
          </Panel>
          <Panel title="Issues">
            <IssueList issues={validation?.issues ?? []} />
          </Panel>
        </aside>

        <section className="ova-pte-editor">
          {mode === "visual" ? (
            <VisualSection
              node={selectedSection}
              readOnly={visualLocked}
              onTitleChange={(title) => {
                if (!selectedSection) return;
                applyCommand(updateSectionTitle(document, selectedSection.id, title));
              }}
              onFirstTextChange={(text) => {
                if (!selectedSection) return;
                applyCommand(updateFirstTextBlock(document, selectedSection.id, text));
              }}
              onAddParagraph={() => selectedSection && applyCommand(addParagraphBlock(document, selectedSection.id))}
              onDuplicateBlock={(index) => selectedSection && applyCommand(duplicateBlock(document, selectedSection.id, index))}
              onDeleteBlock={(index) => selectedSection && applyCommand(deleteBlock(document, selectedSection.id, index))}
              onMoveBlock={(fromIndex, toIndex) =>
                selectedSection && applyCommand(moveBlock(document, selectedSection.id, fromIndex, toIndex))
              }
            />
          ) : (
            <div className="ova-pte-source">
              <div className="ova-pte-source-actions">
                <span>{sourceState}</span>
                <button onClick={applySource}>Apply</button>
                <button onClick={() => {
                  setSourceText(stringifyDocument(document, true));
                  setSourceState("SYNCED");
                }}>Discard</button>
              </div>
              <textarea
                value={sourceText}
                spellCheck={false}
                onChange={(event) => {
                  setSourceText(event.target.value);
                  setSourceState("DRAFT");
                }}
              />
            </div>
          )}
        </section>

        <aside className="ova-pte-properties">
          <Panel title="Properties">
            <dl>
              <dt>Schema</dt>
              <dd>{document.schemaVersion}</dd>
              <dt>Title</dt>
              <dd>{displayText(document.meta?.title, document.meta?.language ?? "en")}</dd>
              <dt>Language</dt>
              <dd>{document.meta?.language ?? "en"}</dd>
              <dt>Selected</dt>
              <dd>{selectedSection?.id ?? "None"}</dd>
            </dl>
          </Panel>
          <Panel title="Data">
            <DataEditor
              document={document}
              selectedResource={selectedResource}
              readOnly={visualLocked}
              onCommand={applyCommand}
            />
          </Panel>
          <Panel title="Find Results">
            <IssueList issues={searchResults.map((result) => ({
              code: result.kind,
              severity: "info",
              message: result.label,
              path: result.path
            }))} />
          </Panel>
          <Panel title="Versions">
            <VersionsPanel
              enabled={versioningEnabled}
              versions={versions}
              error={versionError}
              onLoad={loadLocalVersion}
              onRename={async (versionId, label) => {
                if (!props.versioning?.enabled) return;
                await renameBrowserVersion(props.versioning, versionId, label);
                await refreshVersions();
              }}
              onDelete={async (versionId) => {
                if (!props.versioning?.enabled) return;
                await deleteBrowserVersion(props.versioning, versionId);
                await refreshVersions();
              }}
            />
          </Panel>
        </aside>
      </main>
    </div>
  );
});

function Panel({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="ova-pte-panel">
      <h2>{title}</h2>
      {children}
    </section>
  );
}

function SectionTree({
  nodes,
  selectedId,
  onSelect
}: {
  nodes: SectionNode[];
  selectedId: string | undefined;
  onSelect: (id: string) => void;
}) {
  return (
    <ul className="ova-pte-tree">
      {nodes.map((node) => (
        <li key={node.path}>
          <button className={node.id === selectedId ? "active" : ""} onClick={() => onSelect(node.id)}>
            <span>{node.level}</span>
            {node.title || node.id}
          </button>
          {node.children.length > 0 && (
            <SectionTree nodes={node.children} selectedId={selectedId} onSelect={onSelect} />
          )}
        </li>
      ))}
    </ul>
  );
}

function VisualSection({
  node,
  readOnly,
  onTitleChange,
  onFirstTextChange,
  onAddParagraph,
  onDuplicateBlock,
  onDeleteBlock,
  onMoveBlock
}: {
  node: SectionNode | undefined;
  readOnly: boolean;
  onTitleChange: (title: string) => void;
  onFirstTextChange: (text: string) => void;
  onAddParagraph: () => void;
  onDuplicateBlock: (index: number) => void;
  onDeleteBlock: (index: number) => void;
  onMoveBlock: (fromIndex: number, toIndex: number) => void;
}) {
  const firstTextBlock = node?.section.body
    ?.flatMap((item) => item.blocks ?? [])
    .find((block) => block._type === "block");
  const firstText = firstTextBlock?.children
    ?.map((child) => (typeof child.text === "string" ? child.text : ""))
    .join("") ?? "";

  if (!node) {
    return <div className="ova-pte-empty">No section selected.</div>;
  }

  return (
    <article className="ova-pte-document">
      {readOnly && <div className="ova-pte-lock">Visual editing is locked until JSON changes are applied or discarded.</div>}
      <input
        className="ova-pte-title-input"
        value={node.title}
        readOnly={readOnly}
        onChange={(event) => onTitleChange(event.target.value)}
      />
      <textarea
        className="ova-pte-paragraph-input"
        value={firstText}
        readOnly={readOnly}
        onChange={(event) => onFirstTextChange(event.target.value)}
      />
      <div className="ova-pte-section-actions">
        <button disabled={readOnly} onClick={onAddParagraph}>Add Paragraph</button>
      </div>
      <div className="ova-pte-block-list">
        {node.section.body?.flatMap((item) => item.blocks ?? []).map((block, index) => (
          <div className="ova-pte-block-card" key={index}>
            <strong>{block._type ?? "unknown"}</strong>
            {"chartRef" in block && block.chartRef ? <span>{block.chartRef}</span> : null}
            {"tableRef" in block && block.tableRef ? <span>{block.tableRef}</span> : null}
            {"imageRef" in block && block.imageRef ? <span>{block.imageRef}</span> : null}
            <div className="ova-pte-block-actions">
              <button disabled={readOnly || index === 0} onClick={() => onMoveBlock(index, index - 1)}>Up</button>
              <button disabled={readOnly} onClick={() => onMoveBlock(index, index + 1)}>Down</button>
              <button disabled={readOnly} onClick={() => onDuplicateBlock(index)}>Duplicate</button>
              <button disabled={readOnly} onClick={() => onDeleteBlock(index)}>Delete</button>
            </div>
          </div>
        ))}
      </div>
    </article>
  );
}

function ResourceStats({
  document,
  validation,
  selectedResource,
  onSelectResource
}: {
  document: OVAReportDocument;
  validation: ReturnType<typeof validateDocument> | undefined;
  selectedResource: { kind: "chart" | "table"; id: string } | undefined;
  onSelectResource: (resource: { kind: "chart" | "table"; id: string }) => void;
}) {
  return (
    <>
      <ul className="ova-pte-stats">
        <li>Charts <strong>{document.datasets?.charts?.length ?? 0}</strong></li>
        <li>Tables <strong>{document.datasets?.tables?.length ?? 0}</strong></li>
        <li>Images <strong>{document.assets?.images?.length ?? 0}</strong></li>
        <li>Refs <strong>{validation?.referenceIndex.outgoing.length ?? 0}</strong></li>
      </ul>
      <div className="ova-pte-resource-list">
        {document.datasets?.charts?.slice(0, 30).map((chart) => {
          const id = String(chart.id ?? "");
          return (
            <button
              key={`chart-${id}`}
              className={selectedResource?.kind === "chart" && selectedResource.id === id ? "active" : ""}
              onClick={() => id && onSelectResource({ kind: "chart", id })}
            >
              Chart: {displayText(chart.label as string | Record<string, string> | undefined) || id}
            </button>
          );
        })}
        {document.datasets?.tables?.slice(0, 30).map((table) => {
          const id = String(table.id ?? "");
          return (
            <button
              key={`table-${id}`}
              className={selectedResource?.kind === "table" && selectedResource.id === id ? "active" : ""}
              onClick={() => id && onSelectResource({ kind: "table", id })}
            >
              Table: {displayText(table.label as string | Record<string, string> | undefined) || id}
            </button>
          );
        })}
      </div>
    </>
  );
}

function DataEditor({
  document,
  selectedResource,
  readOnly,
  onCommand
}: {
  document: OVAReportDocument;
  selectedResource: { kind: "chart" | "table"; id: string } | undefined;
  readOnly: boolean;
  onCommand: (result: CommandResult) => void;
}) {
  if (!selectedResource) {
    return <p className="ova-pte-muted">Select a chart or table resource</p>;
  }

  if (selectedResource.kind === "chart") {
    const chart = document.datasets?.charts?.find((item) => item.id === selectedResource.id);
    if (!chart) {
      return <p className="ova-pte-muted">Chart not found</p>;
    }

    const chartType = String(chart.chartType ?? "unknown");
    const slices = Array.isArray(chart.slices) ? chart.slices.filter(isRecord) : [];
    const series = Array.isArray(chart.series) ? chart.series.filter(isRecord) : [];
    return (
      <div className="ova-pte-data-editor">
        <label>
          Chart Label
          <input
            value={displayText(chart.label as string | Record<string, string> | undefined, document.meta?.language ?? "en")}
            readOnly={readOnly}
            onChange={(event) =>
              onCommand(updateChartLabel(document, selectedResource.id, event.target.value))
            }
          />
        </label>
        <p className="ova-pte-muted">Type: {chartType}</p>
        {slices.length > 0 ? (
          <SliceDataEditor
            document={document}
            chartId={selectedResource.id}
            slices={slices}
            readOnly={readOnly}
            onCommand={onCommand}
          />
        ) : chartType === "bar" ? (
          <BarDataEditor
            document={document}
            chartId={selectedResource.id}
            chart={chart}
            series={series}
            readOnly={readOnly}
            onCommand={onCommand}
          />
        ) : chartType === "line" ? (
          <LineDataEditor
            document={document}
            chartId={selectedResource.id}
            series={series}
            readOnly={readOnly}
            onCommand={onCommand}
          />
        ) : chartType === "matrix_bubble" ? (
          <MatrixBubbleDataEditor
            document={document}
            chartId={selectedResource.id}
            series={series}
            readOnly={readOnly}
            onCommand={onCommand}
          />
        ) : (
          <p className="ova-pte-muted">This chart type is read-only in the current data editor.</p>
        )}
      </div>
    );
  }

  const table = document.datasets?.tables?.find((item) => item.id === selectedResource.id);
  const rows = Array.isArray(table?.rows) ? table.rows.filter(isRecord) : [];
  if (!table) {
    return <p className="ova-pte-muted">Table not found</p>;
  }

  return (
    <div className="ova-pte-data-editor">
      <p className="ova-pte-muted">Type: {String(table.tableType ?? "unknown")}</p>
      <div className="ova-pte-table-editor">
        {rows.slice(0, 20).map((row, rowIndex) => {
          const cells = Array.isArray(row.cells) ? row.cells.filter(isRecord) : [];
          return (
            <div className="ova-pte-table-row" key={rowIndex}>
              {cells.map((cell, cellIndex) => (
                <input
                  key={`${rowIndex}-${cellIndex}`}
                  value={String(cell.text ?? "")}
                  readOnly={readOnly}
                  onChange={(event) =>
                    onCommand(updateGridTableCellText(document, selectedResource.id, rowIndex, cellIndex, event.target.value))
                  }
                />
              ))}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function SliceDataEditor({
  document,
  chartId,
  slices,
  readOnly,
  onCommand
}: {
  document: OVAReportDocument;
  chartId: string;
  slices: JSONObject[];
  readOnly: boolean;
  onCommand: (result: CommandResult) => void;
}) {
  return (
    <div className="ova-pte-slice-list">
      {slices.map((slice) => {
        const key = String(slice.key ?? "");
        return (
          <div className="ova-pte-slice-row" key={key}>
            <input
              value={displayText(slice.label as string | Record<string, string> | undefined, document.meta?.language ?? "en")}
              readOnly={readOnly}
              onChange={(event) =>
                onCommand(updateChartSlice(document, chartId, key, { label: event.target.value }))
              }
            />
            <input
              type="number"
              value={Number(slice.value ?? 0)}
              readOnly={readOnly}
              step="0.01"
              onChange={(event) =>
                onCommand(updateChartSlice(document, chartId, key, { value: Number(event.target.value) }))
              }
            />
          </div>
        );
      })}
    </div>
  );
}

function BarDataEditor({
  document,
  chartId,
  chart,
  series,
  readOnly,
  onCommand
}: {
  document: OVAReportDocument;
  chartId: string;
  chart: JSONObject;
  series: JSONObject[];
  readOnly: boolean;
  onCommand: (result: CommandResult) => void;
}) {
  const categories = Array.isArray(chart.categories) ? chart.categories.filter(isRecord) : [];
  return (
    <div className="ova-pte-chart-table">
      <div className="ova-pte-chart-row ova-pte-chart-head">
        <span>Category</span>
        {series.map((item) => <span key={String(item.key)}>{displayText(item.label as string | Record<string, string> | undefined) || String(item.key)}</span>)}
      </div>
      {categories.slice(0, 30).map((category) => {
        const categoryKey = String(category.key ?? "");
        return (
          <div className="ova-pte-chart-row" key={categoryKey}>
            <input
              value={displayText(category.label as string | Record<string, string> | undefined, document.meta?.language ?? "en") || categoryKey}
              readOnly={readOnly}
              onChange={(event) => onCommand(updateBarChartCategory(document, chartId, categoryKey, event.target.value))}
            />
            {series.map((item) => {
              const seriesKey = String(item.key ?? "");
              const data = Array.isArray(item.data) ? item.data.filter(isRecord) : [];
              const point = data.find((entry) => entry.categoryKey === categoryKey);
              return (
                <input
                  key={`${seriesKey}-${categoryKey}`}
                  type="number"
                  value={Number(point?.value ?? 0)}
                  readOnly={readOnly}
                  onChange={(event) =>
                    onCommand(updateBarChartValue(document, chartId, seriesKey, categoryKey, Number(event.target.value)))
                  }
                />
              );
            })}
          </div>
        );
      })}
    </div>
  );
}

function LineDataEditor({
  document,
  chartId,
  series,
  readOnly,
  onCommand
}: {
  document: OVAReportDocument;
  chartId: string;
  series: JSONObject[];
  readOnly: boolean;
  onCommand: (result: CommandResult) => void;
}) {
  const firstSeries = series[0];
  const seriesKey = String(firstSeries?.key ?? "");
  const points = Array.isArray(firstSeries?.points) ? firstSeries.points.filter(isRecord) : [];
  return (
    <div className="ova-pte-chart-table">
      <div className="ova-pte-chart-row ova-pte-chart-head">
        <span>Label</span>
        <span>X</span>
        <span>Y</span>
      </div>
      {points.slice(0, 40).map((point) => {
        const pointKey = String(point.key ?? "");
        return (
          <div className="ova-pte-chart-row" key={pointKey}>
            <input
              value={displayText(point.label as string | Record<string, string> | undefined, document.meta?.language ?? "en") || pointKey}
              readOnly={readOnly}
              onChange={(event) =>
                onCommand(updateLineChartPoint(document, chartId, seriesKey, pointKey, { label: event.target.value }))
              }
            />
            <input
              type="number"
              value={Number(point.xValue ?? 0)}
              readOnly={readOnly}
              onChange={(event) =>
                onCommand(updateLineChartPoint(document, chartId, seriesKey, pointKey, { xValue: Number(event.target.value) }))
              }
            />
            <input
              type="number"
              value={Number(point.yValue ?? 0)}
              readOnly={readOnly}
              onChange={(event) =>
                onCommand(updateLineChartPoint(document, chartId, seriesKey, pointKey, { yValue: Number(event.target.value) }))
              }
            />
          </div>
        );
      })}
    </div>
  );
}

function MatrixBubbleDataEditor({
  document,
  chartId,
  series,
  readOnly,
  onCommand
}: {
  document: OVAReportDocument;
  chartId: string;
  series: JSONObject[];
  readOnly: boolean;
  onCommand: (result: CommandResult) => void;
}) {
  const firstSeries = series[0];
  const seriesKey = String(firstSeries?.key ?? "");
  const points = Array.isArray(firstSeries?.points) ? firstSeries.points.filter(isRecord) : [];
  return (
    <div className="ova-pte-chart-table">
      <div className="ova-pte-chart-row ova-pte-chart-head">
        <span>X</span>
        <span>Y</span>
        <span>Size</span>
      </div>
      {points.slice(0, 40).map((point) => {
        const pointKey = String(point.key ?? "");
        return (
          <div className="ova-pte-chart-row" key={pointKey}>
            <span>{String(point.xCategoryKey ?? "")}</span>
            <span>{String(point.yCategoryKey ?? "")}</span>
            <input
              type="number"
              value={Number(point.sizeValue ?? 0)}
              readOnly={readOnly}
              onChange={(event) =>
                onCommand(updateMatrixBubblePoint(document, chartId, seriesKey, pointKey, Number(event.target.value)))
              }
            />
          </div>
        );
      })}
    </div>
  );
}

function IssueList({ issues }: { issues: EditorIssue[] }) {
  if (issues.length === 0) {
    return <p className="ova-pte-muted">None</p>;
  }

  return (
    <ul className="ova-pte-issues">
      {issues.slice(0, 80).map((issue, index) => (
        <li key={`${issue.path}-${issue.code}-${index}`} data-severity={issue.severity}>
          <span>{issue.severity}</span>
          <p>{issue.message}</p>
          <small>{issue.path}</small>
        </li>
      ))}
    </ul>
  );
}

function VersionsPanel({
  enabled,
  versions,
  error,
  onLoad,
  onRename,
  onDelete
}: {
  enabled: boolean;
  versions: SavedVersionMeta[];
  error: string | undefined;
  onLoad: (id: string) => void;
  onRename: (id: string, label: string) => void | Promise<void>;
  onDelete: (id: string) => void | Promise<void>;
}) {
  if (!enabled) {
    return <p className="ova-pte-muted">Local versions disabled</p>;
  }

  if (error) {
    return <p className="ova-pte-error">{error}</p>;
  }

  if (versions.length === 0) {
    return <p className="ova-pte-muted">No local versions</p>;
  }

  return (
    <ul className="ova-pte-versions">
      {versions.map((version) => (
        <li key={version.id}>
          <button onClick={() => onLoad(version.id)}>
            <strong>{version.label}</strong>
            <span>{version.validationStatus} - {Math.ceil(version.sizeBytes / 1024)} KB</span>
          </button>
          <div className="ova-pte-version-actions">
            <button
              onClick={() => {
                const label = window.prompt("Rename local version", version.label);
                if (label !== null) {
                  void onRename(version.id, label);
                }
              }}
            >
              Rename
            </button>
            <button
              onClick={() => {
                if (window.confirm("Delete this local version?")) {
                  void onDelete(version.id);
                }
              }}
            >
              Delete
            </button>
          </div>
        </li>
      ))}
    </ul>
  );
}

function findSection(nodes: SectionNode[], id: string | undefined): SectionNode | undefined {
  for (const node of nodes) {
    if (node.id === id) {
      return node;
    }
    const child = findSection(node.children, id);
    if (child) {
      return child;
    }
  }
  return undefined;
}

function isRecord(value: unknown): value is JSONObject {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
