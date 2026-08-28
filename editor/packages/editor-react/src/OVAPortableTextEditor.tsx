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
  plainBlockText,
  renameVersion as renameBrowserVersion,
  searchDocument,
  saveVersion as saveBrowserVersion,
  stringifyDocument,
  updateBarChartCategory,
  updateBarChartValue,
  updateChartLabel,
  updateChartSlice,
  updateGridTableCellText,
  updateLineChartPoint,
  updateMatrixBubblePoint,
  updateSectionTitle,
  updateTextBlock,
  validateDocument,
  type BrowserVersioningOptions,
  type EditorIssue,
  type OVAReportDocument,
  type SectionNode,
  type CommandResult,
  type JSONObject,
  type OVABlock,
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
import { detectInitialLocale, UI_TEXT, type EditorLocale, type EditorMessages } from "./i18n";
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
  initialLocale?: EditorLocale;
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
  const [locale, setLocale] = useState<EditorLocale>(() => detectInitialLocale(props.initialLocale));
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
  const [selectedBlockIndex, setSelectedBlockIndex] = useState(0);
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
  const selectedBlocks = useMemo(() => getSectionBlocks(selectedSection), [selectedSection]);
  const selectedBlock = selectedBlocks[selectedBlockIndex];
  const searchResults = useMemo(
    () => (document ? searchDocument(document, query) : []),
    [document, query]
  );
  const visualLocked = Boolean(props.readOnly || sourceState !== "SYNCED");
  const versioningEnabled = Boolean(props.versioning?.enabled && props.versioning.documentKey);
  const t = UI_TEXT[locale];

  useEffect(() => {
    if (props.initialLocale) {
      setLocale(props.initialLocale);
    }
  }, [props.initialLocale]);

  useEffect(() => {
    setSelectedBlockIndex((current) => {
      if (selectedBlocks.length === 0) {
        return 0;
      }
      return Math.min(current, selectedBlocks.length - 1);
    });
  }, [selectedSection?.id, selectedBlocks.length]);

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
    if (dirty && !window.confirm(t.openDirtyConfirm)) {
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
    if (dirty && !window.confirm(t.openDirtyConfirm)) {
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
    return <div className="ova-pte-shell ova-pte-empty">{t.openEmpty}</div>;
  }

  return (
    <div className="ova-pte-shell">
      <header className="ova-pte-toolbar">
        <div className="ova-pte-toolbar-group ova-pte-segmented" aria-label={t.visual}>
          <button className={mode === "visual" ? "active" : ""} onClick={() => setMode("visual")}>{t.visual}</button>
          <button className={mode === "json" ? "active" : ""} onClick={() => setMode("json")}>{t.json}</button>
        </div>
        <div className="ova-pte-toolbar-group ova-pte-segmented ova-pte-locale" aria-label={t.language}>
          <button className={locale === "en" ? "active" : ""} onClick={() => setLocale("en")}>EN</button>
          <button className={locale === "zh" ? "active" : ""} onClick={() => setLocale("zh")}>中文</button>
        </div>
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
        <div className="ova-pte-toolbar-group">
          <button onClick={() => fileInputRef.current?.click()}>{t.open}</button>
          <button onClick={copyJSON}>{t.copyJSON}</button>
          <button onClick={downloadJSON}>{t.download}</button>
        </div>
        <div className="ova-pte-toolbar-group ova-pte-search-group">
          <input
            aria-label={t.find}
            placeholder={t.find}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </div>
        <div className="ova-pte-toolbar-group">
          <button disabled={past.length === 0} onClick={undo}>{t.undo}</button>
          <button disabled={future.length === 0} onClick={redo}>{t.redo}</button>
        </div>
        <div className="ova-pte-toolbar-group">
          <button onClick={() => validation && props.onValidationChange?.(validation)}>{t.validate}</button>
        <button disabled={!props.onRequestFinalPreview} onClick={() => props.onRequestFinalPreview?.(document)}>
          {t.finalPreview}
        </button>
        <button onClick={save}>{t.save}</button>
        <button disabled={!versioningEnabled} onClick={saveLocalVersion}>{t.saveVersion}</button>
        </div>
        <div className="ova-pte-toolbar-group">
          <button disabled={visualLocked} onClick={() => applyCommand(addSection(document))}>{t.addSection}</button>
        <button
          disabled={visualLocked || !selectedSection}
          onClick={() => selectedSection && applyCommand(addSection(document, { parentSectionId: selectedSection.id }))}
        >
          {t.addSubsection}
        </button>
        <button
          disabled={visualLocked || !selectedSection}
          onClick={() => selectedSection && applyCommand(duplicateSection(document, selectedSection.id))}
        >
          {t.duplicateSection}
        </button>
        <button
          disabled={visualLocked || !selectedSection}
          onClick={() => selectedSection && applyCommand(deleteSection(document, selectedSection.id))}
        >
          {t.deleteSection}
        </button>
        </div>
        <span className="ova-pte-status">{dirty ? t.modified : t.saved} - {validation?.issues.filter((issue) => issue.severity === "error").length ?? 0} {t.errors} - {validation?.issues.filter((issue) => issue.severity === "warning").length ?? 0} {t.warnings}</span>
      </header>

      <main className="ova-pte-grid">
        <aside className="ova-pte-sidebar">
          <Panel title={t.outline}>
            <SectionTree
              nodes={sections}
              selectedId={selectedSection?.id}
              onSelect={(id) => {
                setSelectedSectionId(id);
                setSelectedBlockIndex(0);
              }}
            />
          </Panel>
          <Panel title={t.issues}>
            <IssueList issues={validation?.issues ?? []} t={t} />
          </Panel>
        </aside>

        <section className="ova-pte-editor">
          {mode === "visual" ? (
            <SectionComposer
              node={selectedSection}
              selectedBlockIndex={selectedBlockIndex}
              readOnly={visualLocked}
              document={document}
              onTitleChange={(title) => {
                if (!selectedSection) return;
                applyCommand(updateSectionTitle(document, selectedSection.id, title));
              }}
              onSelectBlock={setSelectedBlockIndex}
              onAddParagraph={() => selectedSection && applyCommand(addParagraphBlock(document, selectedSection.id))}
              onDuplicateBlock={(index) => {
                if (!selectedSection) return;
                applyCommand(duplicateBlock(document, selectedSection.id, index));
                setSelectedBlockIndex(index + 1);
              }}
              onDeleteBlock={(index) => {
                if (!selectedSection) return;
                applyCommand(deleteBlock(document, selectedSection.id, index));
                setSelectedBlockIndex(Math.max(0, index - 1));
              }}
              onMoveBlock={(fromIndex, toIndex) => {
                if (!selectedSection) return;
                applyCommand(moveBlock(document, selectedSection.id, fromIndex, toIndex));
                setSelectedBlockIndex(Math.max(0, Math.min(toIndex, selectedBlocks.length - 1)));
              }}
              t={t}
            />
          ) : (
            <div className="ova-pte-source">
              <div className="ova-pte-source-actions">
                <span>{sourceState}</span>
                <button onClick={applySource}>{t.apply}</button>
                <button onClick={() => {
                  setSourceText(stringifyDocument(document, true));
                  setSourceState("SYNCED");
                }}>{t.discard}</button>
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
          <Panel title={t.blockInspector}>
            <BlockInspector
              document={document}
              sectionId={selectedSection?.id}
              block={selectedBlock}
              blockIndex={selectedBlockIndex}
              readOnly={visualLocked}
              onTextChange={(text) => {
                if (!selectedSection) return;
                applyCommand(updateTextBlock(document, selectedSection.id, selectedBlockIndex, text));
              }}
              onCommand={applyCommand}
              t={t}
            />
          </Panel>
          <Panel title={t.documentSummary}>
            <dl>
              <dt>{t.schema}</dt>
              <dd>{document.schemaVersion}</dd>
              <dt>{t.title}</dt>
              <dd>{displayText(document.meta?.title, document.meta?.language ?? "en")}</dd>
              <dt>{t.language}</dt>
              <dd>{document.meta?.language ?? "en"}</dd>
              <dt>{t.selected}</dt>
              <dd>{selectedSection?.id ?? t.none}</dd>
            </dl>
          </Panel>
          <Panel title={t.findResults}>
            <IssueList issues={searchResults.map((result) => ({
              code: result.kind,
              severity: "info",
              message: result.label,
              path: result.path
            }))} t={t} />
          </Panel>
          <Panel title={t.versions}>
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
              t={t}
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

function SectionComposer({
  node,
  selectedBlockIndex,
  readOnly,
  document,
  onTitleChange,
  onSelectBlock,
  onAddParagraph,
  onDuplicateBlock,
  onDeleteBlock,
  onMoveBlock,
  t
}: {
  node: SectionNode | undefined;
  selectedBlockIndex: number;
  readOnly: boolean;
  document: OVAReportDocument;
  onTitleChange: (title: string) => void;
  onSelectBlock: (index: number) => void;
  onAddParagraph: () => void;
  onDuplicateBlock: (index: number) => void;
  onDeleteBlock: (index: number) => void;
  onMoveBlock: (fromIndex: number, toIndex: number) => void;
  t: EditorMessages;
}) {
  if (!node) {
    return <div className="ova-pte-empty">{t.noSectionSelected}</div>;
  }

  const blocks = getSectionBlocks(node);

  return (
    <article className="ova-pte-section-composer">
      {readOnly && <div className="ova-pte-lock">{t.visualLocked}</div>}
      <div className="ova-pte-section-header">
        <label>
          {t.sectionTitle}
          <input
            className="ova-pte-title-input"
            value={node.title}
            readOnly={readOnly}
            onChange={(event) => onTitleChange(event.target.value)}
          />
        </label>
        <span>{t.sectionBlocks}: {blocks.length}</span>
      </div>
      <div className="ova-pte-section-actions">
        <button disabled={readOnly} onClick={onAddParagraph}>{t.addParagraph}</button>
      </div>
      <div className="ova-pte-block-list">
        {blocks.map((block, index) => (
          <div className={index === selectedBlockIndex ? "ova-pte-block-card active" : "ova-pte-block-card"} key={index}>
            <button className="ova-pte-block-select" onClick={() => onSelectBlock(index)}>
              <strong>{blockKindLabel(block, t)}</strong>
              <span>{blockSummary(block, document, t)}</span>
            </button>
            <div className="ova-pte-block-actions">
              <button
                disabled={readOnly || index === 0}
                title={t.upBlock}
                onClick={() => onMoveBlock(index, index - 1)}
              >
                {t.upBlock}
              </button>
              <button
                disabled={readOnly || index === blocks.length - 1}
                title={t.downBlock}
                onClick={() => onMoveBlock(index, index + 1)}
              >
                {t.downBlock}
              </button>
              <button disabled={readOnly} title={t.duplicateBlock} onClick={() => onDuplicateBlock(index)}>
                {t.duplicateBlock}
              </button>
              <button disabled={readOnly} title={t.deleteBlock} onClick={() => onDeleteBlock(index)}>
                {t.deleteBlock}
              </button>
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
  onSelectResource,
  t
}: {
  document: OVAReportDocument;
  validation: ReturnType<typeof validateDocument> | undefined;
  selectedResource: { kind: "chart" | "table"; id: string } | undefined;
  onSelectResource: (resource: { kind: "chart" | "table"; id: string }) => void;
  t: EditorMessages;
}) {
  return (
    <>
      <ul className="ova-pte-stats">
        <li>{t.charts} <strong>{document.datasets?.charts?.length ?? 0}</strong></li>
        <li>{t.tables} <strong>{document.datasets?.tables?.length ?? 0}</strong></li>
        <li>{t.images} <strong>{document.assets?.images?.length ?? 0}</strong></li>
        <li>{t.refs} <strong>{validation?.referenceIndex.outgoing.length ?? 0}</strong></li>
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
              {t.chart}: {displayText(chart.label as string | Record<string, string> | undefined) || id}
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
              {t.table}: {displayText(table.label as string | Record<string, string> | undefined) || id}
            </button>
          );
        })}
      </div>
    </>
  );
}

function BlockInspector({
  document,
  sectionId,
  block,
  blockIndex,
  readOnly,
  onTextChange,
  onCommand,
  t
}: {
  document: OVAReportDocument;
  sectionId: string | undefined;
  block: OVABlock | undefined;
  blockIndex: number;
  readOnly: boolean;
  onTextChange: (text: string) => void;
  onCommand: (result: CommandResult) => void;
  t: EditorMessages;
}) {
  if (!sectionId || !block) {
    return <p className="ova-pte-muted">{t.noBlockSelected}</p>;
  }

  const selectedResource = resourceFromBlock(block);
  const text = block._type === "block" ? plainBlockText(block.children) : "";

  return (
    <div className="ova-pte-block-inspector">
      <dl>
        <dt>{t.blockType}</dt>
        <dd>{blockKindLabel(block, t)}</dd>
        <dt>{t.linkedResource}</dt>
        <dd>{selectedResource?.id ?? t.none}</dd>
      </dl>
      {block._type === "block" ? (
        <label>
          {t.textBlock}
          <textarea
            className="ova-pte-inspector-textarea"
            value={text}
            readOnly={readOnly}
            onChange={(event) => onTextChange(event.target.value)}
          />
        </label>
      ) : selectedResource ? (
        <DataEditor
          document={document}
          selectedResource={selectedResource}
          readOnly={readOnly}
          onCommand={onCommand}
          t={t}
        />
      ) : (
        <p className="ova-pte-muted">{blockSummary(block, document, t)}</p>
      )}
    </div>
  );
}

function DataEditor({
  document,
  selectedResource,
  readOnly,
  onCommand,
  t
}: {
  document: OVAReportDocument;
  selectedResource: { kind: "chart" | "table"; id: string } | undefined;
  readOnly: boolean;
  onCommand: (result: CommandResult) => void;
  t: EditorMessages;
}) {
  if (!selectedResource) {
    return <p className="ova-pte-muted">{t.selectResource}</p>;
  }

  if (selectedResource.kind === "chart") {
    const chart = document.datasets?.charts?.find((item) => item.id === selectedResource.id);
    if (!chart) {
      return <p className="ova-pte-muted">{t.chartNotFound}</p>;
    }

    const chartType = String(chart.chartType ?? "unknown");
    const slices = Array.isArray(chart.slices) ? chart.slices.filter(isRecord) : [];
    const series = Array.isArray(chart.series) ? chart.series.filter(isRecord) : [];
    return (
      <div className="ova-pte-data-editor">
        <label>
          {t.chartLabel}
          <input
            value={displayText(chart.label as string | Record<string, string> | undefined, document.meta?.language ?? "en")}
            readOnly={readOnly}
            onChange={(event) =>
              onCommand(updateChartLabel(document, selectedResource.id, event.target.value))
            }
          />
        </label>
        <p className="ova-pte-muted">{t.type}: {chartType}</p>
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
            t={t}
          />
        ) : chartType === "line" ? (
          <LineDataEditor
            document={document}
            chartId={selectedResource.id}
            series={series}
            readOnly={readOnly}
            onCommand={onCommand}
            t={t}
          />
        ) : chartType === "matrix_bubble" ? (
          <MatrixBubbleDataEditor
            document={document}
            chartId={selectedResource.id}
            series={series}
            readOnly={readOnly}
            onCommand={onCommand}
            t={t}
          />
        ) : (
          <p className="ova-pte-muted">{t.readOnlyChart}</p>
        )}
      </div>
    );
  }

  const table = document.datasets?.tables?.find((item) => item.id === selectedResource.id);
  const rows = Array.isArray(table?.rows) ? table.rows.filter(isRecord) : [];
  if (!table) {
    return <p className="ova-pte-muted">{t.tableNotFound}</p>;
  }

  return (
    <div className="ova-pte-data-editor">
      <p className="ova-pte-muted">{t.type}: {String(table.tableType ?? "unknown")}</p>
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
  onCommand,
  t
}: {
  document: OVAReportDocument;
  chartId: string;
  chart: JSONObject;
  series: JSONObject[];
  readOnly: boolean;
  onCommand: (result: CommandResult) => void;
  t: EditorMessages;
}) {
  const categories = Array.isArray(chart.categories) ? chart.categories.filter(isRecord) : [];
  return (
    <div className="ova-pte-chart-table">
      <div className="ova-pte-chart-row ova-pte-chart-head">
        <span>{t.barCategory}</span>
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
  onCommand,
  t
}: {
  document: OVAReportDocument;
  chartId: string;
  series: JSONObject[];
  readOnly: boolean;
  onCommand: (result: CommandResult) => void;
  t: EditorMessages;
}) {
  const firstSeries = series[0];
  const seriesKey = String(firstSeries?.key ?? "");
  const points = Array.isArray(firstSeries?.points) ? firstSeries.points.filter(isRecord) : [];
  return (
    <div className="ova-pte-chart-table">
      <div className="ova-pte-chart-row ova-pte-chart-head">
        <span>{t.label}</span>
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
  onCommand,
  t
}: {
  document: OVAReportDocument;
  chartId: string;
  series: JSONObject[];
  readOnly: boolean;
  onCommand: (result: CommandResult) => void;
  t: EditorMessages;
}) {
  const firstSeries = series[0];
  const seriesKey = String(firstSeries?.key ?? "");
  const points = Array.isArray(firstSeries?.points) ? firstSeries.points.filter(isRecord) : [];
  return (
    <div className="ova-pte-chart-table">
      <div className="ova-pte-chart-row ova-pte-chart-head">
        <span>X</span>
        <span>Y</span>
        <span>{t.size}</span>
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

function IssueList({ issues, t }: { issues: EditorIssue[]; t: EditorMessages }) {
  if (issues.length === 0) {
    return <p className="ova-pte-muted">{t.none}</p>;
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
  onDelete,
  t
}: {
  enabled: boolean;
  versions: SavedVersionMeta[];
  error: string | undefined;
  onLoad: (id: string) => void;
  onRename: (id: string, label: string) => void | Promise<void>;
  onDelete: (id: string) => void | Promise<void>;
  t: EditorMessages;
}) {
  if (!enabled) {
    return <p className="ova-pte-muted">{t.localVersionsDisabled}</p>;
  }

  if (error) {
    return <p className="ova-pte-error">{error}</p>;
  }

  if (versions.length === 0) {
    return <p className="ova-pte-muted">{t.noLocalVersions}</p>;
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
                const label = window.prompt(t.renameLocalVersion, version.label);
                if (label !== null) {
                  void onRename(version.id, label);
                }
              }}
            >
              {t.rename}
            </button>
            <button
              onClick={() => {
                if (window.confirm(t.deleteLocalVersionConfirm)) {
                  void onDelete(version.id);
                }
              }}
            >
              {t.delete}
            </button>
          </div>
        </li>
      ))}
    </ul>
  );
}

function getSectionBlocks(node: SectionNode | undefined): OVABlock[] {
  return node?.section.body?.flatMap((item) => item.blocks ?? []) ?? [];
}

function resourceFromBlock(block: OVABlock): { kind: "chart" | "table"; id: string } | undefined {
  if (block.chartRef) {
    return { kind: "chart", id: block.chartRef };
  }
  if (block.tableRef) {
    return { kind: "table", id: block.tableRef };
  }
  return undefined;
}

function blockKindLabel(block: OVABlock, t: EditorMessages): string {
  if (block.chartRef || block._type === "chart") {
    return t.chartBlock;
  }
  if (block.tableRef || block._type === "table") {
    return t.tableBlock;
  }
  if (block.imageRef || block._type === "image") {
    return t.imageBlock;
  }
  if (block._type === "block") {
    return t.textBlock;
  }
  return t.unknownBlock;
}

function blockSummary(block: OVABlock, document: OVAReportDocument, t: EditorMessages): string {
  if (block.chartRef) {
    const chart = document.datasets?.charts?.find((item) => item.id === block.chartRef);
    const label = displayText(chart?.label as string | Record<string, string> | undefined, document.meta?.language ?? "en");
    return label ? `${t.chart}: ${label}` : `${t.chart}: ${block.chartRef}`;
  }
  if (block.tableRef) {
    const table = document.datasets?.tables?.find((item) => item.id === block.tableRef);
    const label = displayText(table?.label as string | Record<string, string> | undefined, document.meta?.language ?? "en");
    return label ? `${t.table}: ${label}` : `${t.table}: ${block.tableRef}`;
  }
  if (block.imageRef) {
    return `${t.imageBlock}: ${block.imageRef}`;
  }
  if (block._type === "block") {
    return plainBlockText(block.children).trim() || t.textBlock;
  }
  return String(block._type ?? t.unknownBlock);
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
