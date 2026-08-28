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
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
  type ReactNode
} from "react";
import { detectInitialLocale, UI_TEXT, type EditorLocale, type EditorMessages } from "./i18n";
import { Badge, Button, Panel, ToolbarGroup } from "./ui";
import "./styles.css";

type FocusTarget = "section" | "block";

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
  const [focusTarget, setFocusTarget] = useState<FocusTarget>("section");
  const [expandedSectionIds, setExpandedSectionIds] = useState<Set<string>>(() => new Set());
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (props.initialValue === undefined) {
      return;
    }
    const loaded = loadDocument(props.initialValue);
    if (loaded.document) {
      const firstSectionId = buildSectionTree(loaded.document.sections)[0]?.id;
      setDocument(loaded.document);
      setSourceText(stringifyDocument(loaded.document, true));
      setSelectedSectionId(firstSectionId);
      setFocusTarget("section");
      setExpandedSectionIds(new Set(firstSectionId ? [firstSectionId] : []));
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
  const selectedResource = selectedBlock ? resourceFromBlock(selectedBlock) : undefined;
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
      setExpandedSectionIds((current) => new Set(current).add(result.selectionId as string));
    }
    setDirty(true);
  };

  const applySource = () => {
    const loaded = loadDocument(sourceText);
    if (loaded.document) {
      const firstSectionId = buildSectionTree(loaded.document.sections)[0]?.id;
      setDocument(loaded.document);
      setSourceState("SYNCED");
      setPast((current) => (document ? [...current, document] : current));
      setFuture([]);
      setDirty(true);
      setSelectedSectionId(firstSectionId);
      setFocusTarget("section");
      setExpandedSectionIds(new Set(firstSectionId ? [firstSectionId] : []));
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
      const firstSectionId = buildSectionTree(loaded.document.sections)[0]?.id;
      setDocument(loaded.document);
      setSourceText(stringifyDocument(loaded.document, true));
      setSourceState("SYNCED");
      setPast([]);
      setFuture([]);
      setDirty(false);
      setSelectedSectionId(firstSectionId);
      setFocusTarget("section");
      setExpandedSectionIds(new Set(firstSectionId ? [firstSectionId] : []));
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
      const firstSectionId = buildSectionTree(version.document.sections)[0]?.id;
      setSelectedSectionId(firstSectionId);
      setFocusTarget("section");
      setExpandedSectionIds(new Set(firstSectionId ? [firstSectionId] : []));
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
        const firstSectionId = buildSectionTree(loaded.document.sections)[0]?.id;
        setDocument(loaded.document);
        setSourceText(stringifyDocument(loaded.document, true));
        setSourceState("SYNCED");
        setPast([]);
        setFuture([]);
        setDirty(false);
        setSelectedSectionId(firstSectionId);
        setFocusTarget("section");
        setExpandedSectionIds(new Set(firstSectionId ? [firstSectionId] : []));
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
      const firstSectionId = buildSectionTree(version.document.sections)[0]?.id;
      setSelectedSectionId(firstSectionId);
      setFocusTarget("section");
      setExpandedSectionIds(new Set(firstSectionId ? [firstSectionId] : []));
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

  const selectSection = (id: string) => {
    setSelectedSectionId(id);
    setSelectedBlockIndex(0);
    setFocusTarget("section");
    setExpandedSectionIds((current) => new Set(current).add(id));
  };

  const selectBlock = (sectionId: string, index: number) => {
    setSelectedSectionId(sectionId);
    setSelectedBlockIndex(index);
    setFocusTarget("block");
    setExpandedSectionIds((current) => new Set(current).add(sectionId));
  };

  const toggleSection = (id: string) => {
    setExpandedSectionIds((current) => {
      const next = new Set(current);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };
  return (
    <div className="ova-pte-shell">
      <header className="ova-pte-toolbar">
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
        <ToolbarGroup label={t.mode} compact>
          <div className="ova-pte-segmented" aria-label={t.mode}>
            <Button className={mode === "visual" ? "active" : ""} onClick={() => setMode("visual")}>{t.visual}</Button>
            <Button className={mode === "json" ? "active" : ""} onClick={() => setMode("json")}>{t.json}</Button>
          </div>
        </ToolbarGroup>
        <ToolbarGroup label={t.file}>
          <Button onClick={() => fileInputRef.current?.click()}>{t.open}</Button>
          <Button onClick={copyJSON}>{t.copyJSON}</Button>
          <Button onClick={downloadJSON}>{t.download}</Button>
        </ToolbarGroup>
        <ToolbarGroup label={t.search} compact>
          <input
            aria-label={t.find}
            placeholder={t.find}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </ToolbarGroup>
        <ToolbarGroup label={t.history} compact>
          <Button disabled={past.length === 0} onClick={undo}>{t.undo}</Button>
          <Button disabled={future.length === 0} onClick={redo}>{t.redo}</Button>
        </ToolbarGroup>
        <ToolbarGroup label={t.output}>
          <Button onClick={() => validation && props.onValidationChange?.(validation)}>{t.validate}</Button>
          <Button disabled={!props.onRequestFinalPreview} onClick={() => props.onRequestFinalPreview?.(document)}>
            {t.finalPreview}
          </Button>
          <Button tone="primary" onClick={save}>{t.save}</Button>
          <Button disabled={!versioningEnabled} onClick={saveLocalVersion}>{t.saveVersion}</Button>
        </ToolbarGroup>
        <ToolbarGroup label={t.language} compact>
          <div className="ova-pte-segmented ova-pte-locale" aria-label={t.language}>
            <Button className={locale === "en" ? "active" : ""} onClick={() => setLocale("en")}>EN</Button>
            <Button className={locale === "zh" ? "active" : ""} onClick={() => setLocale("zh")}>中文</Button>
          </div>
        </ToolbarGroup>
        <span className="ova-pte-status">
          <Badge>{dirty ? t.modified : t.saved}</Badge>
          <span>{validation?.issues.filter((issue) => issue.severity === "error").length ?? 0} {t.errors}</span>
          <span>{validation?.issues.filter((issue) => issue.severity === "warning").length ?? 0} {t.warnings}</span>
        </span>
      </header>

      <main className="ova-pte-grid">
        <aside className="ova-pte-sidebar">
          <Panel title={t.outline}>
            <NavigatorTree
              nodes={sections}
              selectedId={selectedSection?.id}
              selectedBlockIndex={focusTarget === "block" ? selectedBlockIndex : undefined}
              expandedIds={expandedSectionIds}
              document={document}
              onSelectSection={selectSection}
              onSelectBlock={selectBlock}
              onToggleSection={toggleSection}
              t={t}
            />
          </Panel>
          <Panel title={t.issues}>
            <IssueList issues={validation?.issues ?? []} t={t} />
          </Panel>
        </aside>

        <section className="ova-pte-editor">
          {mode === "visual" ? (
            <FocusedEditor
              node={selectedSection}
              focusTarget={focusTarget}
              block={selectedBlock}
              selectedBlockIndex={selectedBlockIndex}
              readOnly={visualLocked}
              document={document}
              onTitleChange={(title) => {
                if (!selectedSection) return;
                applyCommand(updateSectionTitle(document, selectedSection.id, title));
              }}
              onSelectBlock={(index) => selectedSection && selectBlock(selectedSection.id, index)}
              onAddParagraph={() => selectedSection && applyCommand(addParagraphBlock(document, selectedSection.id))}
              onAddSubsection={() => selectedSection && applyCommand(addSection(document, { parentSectionId: selectedSection.id }))}
              onAddRootSection={() => applyCommand(addSection(document))}
              onDuplicateSection={() => selectedSection && applyCommand(duplicateSection(document, selectedSection.id))}
              onDeleteSection={() => selectedSection && applyCommand(deleteSection(document, selectedSection.id))}
              onDuplicateBlock={(index) => {
                if (!selectedSection) return;
                applyCommand(duplicateBlock(document, selectedSection.id, index));
                setSelectedBlockIndex(index + 1);
                setFocusTarget("block");
              }}
              onDeleteBlock={(index) => {
                if (!selectedSection) return;
                applyCommand(deleteBlock(document, selectedSection.id, index));
                setSelectedBlockIndex(Math.max(0, index - 1));
                setFocusTarget("section");
              }}
              onMoveBlock={(fromIndex, toIndex) => {
                if (!selectedSection) return;
                applyCommand(moveBlock(document, selectedSection.id, fromIndex, toIndex));
                setSelectedBlockIndex(Math.max(0, Math.min(toIndex, selectedBlocks.length - 1)));
                setFocusTarget("block");
              }}
              onTextChange={(text) => {
                if (!selectedSection) return;
                applyCommand(updateTextBlock(document, selectedSection.id, selectedBlockIndex, text));
              }}
              onCommand={applyCommand}
              t={t}
            />
          ) : (
            <div className="ova-pte-source">
              <div className="ova-pte-source-actions">
                <span>{sourceState}</span>
                <Button onClick={applySource}>{t.apply}</Button>
                <Button onClick={() => {
                  setSourceText(stringifyDocument(document, true));
                  setSourceState("SYNCED");
                }}>{t.discard}</Button>
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
          <Panel title={t.context}>
            <SelectedContext
              document={document}
              section={selectedSection}
              focusTarget={focusTarget}
              block={selectedBlock}
              blockIndex={selectedBlockIndex}
              resource={selectedResource}
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

function NavigatorTree({
  nodes,
  selectedId,
  selectedBlockIndex,
  expandedIds,
  document,
  onSelectSection,
  onSelectBlock,
  onToggleSection,
  t
}: {
  nodes: SectionNode[];
  selectedId: string | undefined;
  selectedBlockIndex: number | undefined;
  expandedIds: Set<string>;
  document: OVAReportDocument;
  onSelectSection: (id: string) => void;
  onSelectBlock: (sectionId: string, index: number) => void;
  onToggleSection: (id: string) => void;
  t: EditorMessages;
}) {
  return (
    <ul className="ova-pte-tree ova-pte-navigator">
      {nodes.map((node) => (
        <NavigatorNode
          key={node.path}
          node={node}
          selectedId={selectedId}
          selectedBlockIndex={selectedBlockIndex}
          expandedIds={expandedIds}
          document={document}
          onSelectSection={onSelectSection}
          onSelectBlock={onSelectBlock}
          onToggleSection={onToggleSection}
          t={t}
        />
      ))}
    </ul>
  );
}

function NavigatorNode({
  node,
  selectedId,
  selectedBlockIndex,
  expandedIds,
  document,
  onSelectSection,
  onSelectBlock,
  onToggleSection,
  t
}: {
  node: SectionNode;
  selectedId: string | undefined;
  selectedBlockIndex: number | undefined;
  expandedIds: Set<string>;
  document: OVAReportDocument;
  onSelectSection: (id: string) => void;
  onSelectBlock: (sectionId: string, index: number) => void;
  onToggleSection: (id: string) => void;
  t: EditorMessages;
}) {
  const blocks = getSectionBlocks(node);
  const expanded = expandedIds.has(node.id);
  const totalBlocks = countNestedBlocks(node);
  const hasChildren = node.children.length > 0 || blocks.length > 0;

  return (
    <li>
      <div className="ova-pte-nav-row">
        <Button
          className="ova-pte-nav-toggle"
          disabled={!hasChildren}
          title={expanded ? t.closeSection : t.openSection}
          onClick={() => onToggleSection(node.id)}
        >
          {expanded ? "-" : "+"}
        </Button>
        <Button
          className={node.id === selectedId && selectedBlockIndex === undefined ? "ova-pte-nav-section active" : "ova-pte-nav-section"}
          onClick={() => onSelectSection(node.id)}
        >
          <span>{node.level}</span>
          <strong>{node.title || node.id}</strong>
          <small>{totalBlocks} {t.blocks}</small>
        </Button>
      </div>
      {expanded && (
        <ul>
          {blocks.map((block, index) => (
            <li key={`${node.id}-block-${index}`}>
              <Button
                className={node.id === selectedId && selectedBlockIndex === index ? "ova-pte-nav-block active" : "ova-pte-nav-block"}
                onClick={() => onSelectBlock(node.id, index)}
              >
                <span>{index + 1}</span>
                <strong>{blockNavigatorTitle(block, document, t)}</strong>
                <small>{blockKindLabel(block, t)}</small>
              </Button>
            </li>
          ))}
          {node.children.map((child) => (
            <NavigatorNode
              key={child.path}
              node={child}
              selectedId={selectedId}
              selectedBlockIndex={selectedBlockIndex}
              expandedIds={expandedIds}
              document={document}
              onSelectSection={onSelectSection}
              onSelectBlock={onSelectBlock}
              onToggleSection={onToggleSection}
              t={t}
            />
          ))}
        </ul>
      )}
    </li>
  );
}

function FocusedEditor({
  node,
  focusTarget,
  block,
  selectedBlockIndex,
  readOnly,
  document,
  onTitleChange,
  onSelectBlock,
  onAddParagraph,
  onAddSubsection,
  onAddRootSection,
  onDuplicateSection,
  onDeleteSection,
  onDuplicateBlock,
  onDeleteBlock,
  onMoveBlock,
  onTextChange,
  onCommand,
  t
}: {
  node: SectionNode | undefined;
  focusTarget: FocusTarget;
  block: OVABlock | undefined;
  selectedBlockIndex: number;
  readOnly: boolean;
  document: OVAReportDocument;
  onTitleChange: (title: string) => void;
  onSelectBlock: (index: number) => void;
  onAddParagraph: () => void;
  onAddSubsection: () => void;
  onAddRootSection: () => void;
  onDuplicateSection: () => void;
  onDeleteSection: () => void;
  onDuplicateBlock: (index: number) => void;
  onDeleteBlock: (index: number) => void;
  onMoveBlock: (fromIndex: number, toIndex: number) => void;
  onTextChange: (text: string) => void;
  onCommand: (result: CommandResult) => void;
  t: EditorMessages;
}) {
  if (!node) {
    return <div className="ova-pte-empty">{t.noSectionSelected}</div>;
  }

  if (focusTarget === "block" && block) {
    return (
      <article className="ova-pte-focused-editor">
        {readOnly && <div className="ova-pte-lock">{t.visualLocked}</div>}
        <div className="ova-pte-focus-header">
          <span>{t.currentBlock}</span>
          <h1>{blockKindLabel(block, t)}</h1>
          <p>{node.level} / {node.title || node.id} / {selectedBlockIndex + 1}</p>
        </div>
        <div className="ova-pte-section-actions">
          <Button disabled={readOnly || selectedBlockIndex === 0} title={t.upBlock} onClick={() => onMoveBlock(selectedBlockIndex, selectedBlockIndex - 1)}>
            {t.upBlock}
          </Button>
          <Button disabled={readOnly || selectedBlockIndex >= getSectionBlocks(node).length - 1} title={t.downBlock} onClick={() => onMoveBlock(selectedBlockIndex, selectedBlockIndex + 1)}>
            {t.downBlock}
          </Button>
          <Button disabled={readOnly} onClick={() => onDuplicateBlock(selectedBlockIndex)}>{t.duplicateBlock}</Button>
          <Button tone="danger" disabled={readOnly} onClick={() => onDeleteBlock(selectedBlockIndex)}>{t.deleteBlock}</Button>
        </div>
        <BlockEditor
          document={document}
          block={block}
          readOnly={readOnly}
          onTextChange={onTextChange}
          onCommand={onCommand}
          t={t}
        />
      </article>
    );
  }

  const blocks = getSectionBlocks(node);
  const totalBlocks = countNestedBlocks(node);
  return (
    <article className="ova-pte-focused-editor ova-pte-section-composer">
      {readOnly && <div className="ova-pte-lock">{t.visualLocked}</div>}
      <div className="ova-pte-focus-header">
        <span>{t.currentSection}</span>
        <h1>{node.title || node.id}</h1>
        <p>{node.level} / {totalBlocks} {t.blocks} / {node.children.length} {t.childSections}</p>
      </div>
      <label className="ova-pte-title-field">
        {t.sectionTitle}
        <input
          className="ova-pte-title-input"
          value={node.title}
          readOnly={readOnly}
          onChange={(event) => onTitleChange(event.target.value)}
        />
      </label>
      <div className="ova-pte-section-actions">
        <Button disabled={readOnly} onClick={onAddRootSection}>{t.addSection}</Button>
        <Button disabled={readOnly} onClick={onAddSubsection}>{t.addSubsection}</Button>
        <Button disabled={readOnly} onClick={onAddParagraph}>{t.addParagraph}</Button>
        <Button disabled={readOnly} onClick={onDuplicateSection}>{t.duplicateSection}</Button>
        <Button tone="danger" disabled={readOnly} onClick={onDeleteSection}>{t.deleteSection}</Button>
      </div>
      <div className="ova-pte-block-list">
        {blocks.map((item, index) => (
          <button className="ova-pte-block-card" key={index} onClick={() => onSelectBlock(index)}>
            <strong>{index + 1}. {blockNavigatorTitle(item, document, t)}</strong>
            <span>{blockKindLabel(item, t)}</span>
          </button>
        ))}
      </div>
    </article>
  );
}

function BlockEditor({
  document,
  block,
  readOnly,
  onTextChange,
  onCommand,
  t
}: {
  document: OVAReportDocument;
  block: OVABlock;
  readOnly: boolean;
  onTextChange: (text: string) => void;
  onCommand: (result: CommandResult) => void;
  t: EditorMessages;
}) {
  const selectedResource = resourceFromBlock(block);
  const text = block._type === "block" ? plainBlockText(block.children) : "";

  if (block._type === "block") {
    return (
      <label className="ova-pte-block-editor-field">
        {t.textBlock}
        <AutoGrowTextarea
          className="ova-pte-inspector-textarea"
          value={text}
          readOnly={readOnly}
          onChange={onTextChange}
        />
      </label>
    );
  }

  if (selectedResource) {
    return (
      <DataEditor
        document={document}
        selectedResource={selectedResource}
        readOnly={readOnly}
        onCommand={onCommand}
        t={t}
      />
    );
  }

  return <p className="ova-pte-muted">{blockSummary(block, document, t)}</p>;
}

function SelectedContext({
  document,
  section,
  focusTarget,
  block,
  blockIndex,
  resource,
  t
}: {
  document: OVAReportDocument;
  section: SectionNode | undefined;
  focusTarget: FocusTarget;
  block: OVABlock | undefined;
  blockIndex: number;
  resource: { kind: "chart" | "table"; id: string } | undefined;
  t: EditorMessages;
}) {
  if (!section) {
    return <p className="ova-pte-muted">{t.noSectionSelected}</p>;
  }

  return (
    <dl>
      <dt>{t.selectedObject}</dt>
      <dd>{focusTarget === "block" ? t.currentBlock : t.currentSection}</dd>
      <dt>{t.section}</dt>
      <dd>{section.level} / {section.title || section.id}</dd>
      {focusTarget === "block" && block ? (
        <>
          <dt>{t.blockPath}</dt>
          <dd>{section.id} / {blockIndex + 1}</dd>
          <dt>{t.blockType}</dt>
          <dd>{blockKindLabel(block, t)}</dd>
          <dt>{t.linkedResource}</dt>
          <dd>{resource?.id ?? t.none}</dd>
        </>
      ) : null}
      <dt>{t.resources}</dt>
      <dd>{document.datasets?.charts?.length ?? 0} {t.charts} / {document.datasets?.tables?.length ?? 0} {t.tables}</dd>
    </dl>
  );
}

function AutoGrowTextarea({
  value,
  readOnly,
  className,
  style,
  onChange
}: {
  value: string;
  readOnly: boolean;
  className?: string;
  style?: CSSProperties;
  onChange: (value: string) => void;
}) {
  const ref = useRef<HTMLTextAreaElement>(null);

  useLayoutEffect(() => {
    const element = ref.current;
    if (!element) {
      return;
    }
    element.style.height = "auto";
    element.style.height = `${element.scrollHeight}px`;
  }, [value]);

  return (
    <textarea
      ref={ref}
      className={["ova-pte-autogrow", className].filter(Boolean).join(" ")}
      value={value}
      readOnly={readOnly}
      rows={1}
      style={style}
      onChange={(event) => onChange(event.target.value)}
    />
  );
}

function SyncedDataRow({
  className,
  children,
  style,
  syncKey
}: {
  className: string;
  children: ReactNode;
  style?: CSSProperties;
  syncKey: string;
}) {
  const ref = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const row = ref.current;
    if (!row) {
      return;
    }
    const fields = Array.from(row.querySelectorAll<HTMLElement>("textarea, input, span"));
    fields.forEach((field) => {
      field.style.height = "auto";
      field.style.minHeight = "";
    });
    const maxHeight = fields.reduce((height, field) => {
      return Math.max(height, field.scrollHeight, field.offsetHeight);
    }, 0);
    fields.forEach((field) => {
      if (field instanceof HTMLTextAreaElement || field instanceof HTMLInputElement) {
        field.style.height = `${maxHeight}px`;
      } else {
        field.style.minHeight = `${maxHeight}px`;
      }
    });
  }, [syncKey]);

  return (
    <div ref={ref} className={className} style={style}>
      {children}
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
          <AutoGrowTextarea
            value={displayText(chart.label as string | Record<string, string> | undefined, document.meta?.language ?? "en")}
            readOnly={readOnly}
            onChange={(value) => onCommand(updateChartLabel(document, selectedResource.id, value))}
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
  const columnCount = Math.max(1, ...rows.map((row) => {
    const cells = Array.isArray(row.cells) ? row.cells.filter(isRecord) : [];
    return cells.reduce((total, cell) => total + getCellSpan(cell, "colSpan"), 0);
  }));
  if (!table) {
    return <p className="ova-pte-muted">{t.tableNotFound}</p>;
  }

  return (
    <div className="ova-pte-data-editor">
      <p className="ova-pte-muted">{t.type}: {String(table.tableType ?? "unknown")}</p>
      <div className="ova-pte-table-editor">
        {rows.slice(0, 20).map((row, rowIndex) => {
          const cells = Array.isArray(row.cells) ? row.cells.filter(isRecord) : [];
          const syncKey = cells.map((cell) => tableCellText(cell)).join("\u001f");
          return (
            <SyncedDataRow
              className="ova-pte-table-row"
              key={rowIndex}
              syncKey={syncKey}
              style={{ gridTemplateColumns: `repeat(${columnCount}, minmax(120px, 1fr))` }}
            >
              {cells.map((cell, cellIndex) => (
                <AutoGrowTextarea
                  key={`${rowIndex}-${cellIndex}`}
                  value={tableCellText(cell)}
                  readOnly={readOnly}
                  style={{
                    gridColumn: `span ${getCellSpan(cell, "colSpan")}`,
                    gridRow: `span ${getCellSpan(cell, "rowSpan")}`
                  }}
                  onChange={(value) => onCommand(updateGridTableCellText(document, selectedResource.id, rowIndex, cellIndex, value))}
                />
              ))}
            </SyncedDataRow>
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
        const label = displayText(slice.label as string | Record<string, string> | undefined, document.meta?.language ?? "en");
        return (
          <SyncedDataRow className="ova-pte-slice-row" key={key} syncKey={`${label}\u001f${Number(slice.value ?? 0)}`}>
            <AutoGrowTextarea
              value={label}
              readOnly={readOnly}
              onChange={(value) => onCommand(updateChartSlice(document, chartId, key, { label: value }))}
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
          </SyncedDataRow>
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
        const categoryLabel = displayText(category.label as string | Record<string, string> | undefined, document.meta?.language ?? "en") || categoryKey;
        const rowValues = series.map((item) => {
          const data = Array.isArray(item.data) ? item.data.filter(isRecord) : [];
          return String(data.find((entry) => entry.categoryKey === categoryKey)?.value ?? 0);
        });
        return (
          <SyncedDataRow className="ova-pte-chart-row" key={categoryKey} syncKey={[categoryLabel, ...rowValues].join("\u001f")}>
            <AutoGrowTextarea
              value={categoryLabel}
              readOnly={readOnly}
              onChange={(value) => onCommand(updateBarChartCategory(document, chartId, categoryKey, value))}
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
          </SyncedDataRow>
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
        const pointLabel = displayText(point.label as string | Record<string, string> | undefined, document.meta?.language ?? "en") || pointKey;
        return (
          <SyncedDataRow
            className="ova-pte-chart-row"
            key={pointKey}
            syncKey={`${pointLabel}\u001f${Number(point.xValue ?? 0)}\u001f${Number(point.yValue ?? 0)}`}
          >
            <AutoGrowTextarea
              value={pointLabel}
              readOnly={readOnly}
              onChange={(value) => onCommand(updateLineChartPoint(document, chartId, seriesKey, pointKey, { label: value }))}
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
          </SyncedDataRow>
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
          <SyncedDataRow
            className="ova-pte-chart-row"
            key={pointKey}
            syncKey={`${String(point.xCategoryKey ?? "")}\u001f${String(point.yCategoryKey ?? "")}\u001f${Number(point.sizeValue ?? 0)}`}
          >
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
          </SyncedDataRow>
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

function countNestedBlocks(node: SectionNode | undefined): number {
  if (!node) {
    return 0;
  }
  return getSectionBlocks(node).length + node.children.reduce((total, child) => total + countNestedBlocks(child), 0);
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

function blockNavigatorTitle(block: OVABlock, document: OVAReportDocument, t: EditorMessages): string {
  const locale = document.meta?.language ?? "en";
  const ownTitle = displayMaybeLocalized(block.title, locale) || displayMaybeLocalized(block.label, locale);
  if (ownTitle) {
    return truncateLabel(ownTitle);
  }

  if (block.chartRef) {
    const chart = document.datasets?.charts?.find((item) => item.id === block.chartRef);
    const chartLabel = displayMaybeLocalized(chart?.label, locale);
    return truncateLabel(chartLabel || block.chartRef);
  }

  if (block.tableRef) {
    const table = document.datasets?.tables?.find((item) => item.id === block.tableRef);
    const tableLabel = displayMaybeLocalized(table?.label, locale);
    return truncateLabel(tableLabel || block.tableRef);
  }

  if (block.imageRef) {
    return truncateLabel(block.imageRef);
  }

  if (block._type === "block") {
    const text = plainBlockText(block.children).trim();
    return truncateLabel(text || t.textBlock);
  }

  return truncateLabel(String(block._type ?? t.unknownBlock));
}

function displayMaybeLocalized(value: unknown, locale: string): string {
  if (typeof value === "string") {
    return value.trim();
  }
  if (isRecord(value)) {
    return displayText(value as Record<string, string>, locale).trim();
  }
  return "";
}

function truncateLabel(value: string, maxLength = 86): string {
  const normalized = value.replace(/\s+/g, " ").trim();
  if (normalized.length <= maxLength) {
    return normalized;
  }
  return `${normalized.slice(0, maxLength - 1)}...`;
}

function tableCellText(cell: JSONObject): string {
  if (typeof cell.text === "string") {
    return cell.text;
  }
  if (!Array.isArray(cell.blocks)) {
    return "";
  }
  return cell.blocks
    .filter(isRecord)
    .map((block) => plainBlockText(block.children))
    .filter(Boolean)
    .join("\n");
}

function getCellSpan(cell: JSONObject, key: "colSpan" | "rowSpan"): number {
  const value = Number(cell[key]);
  if (!Number.isFinite(value)) {
    return 1;
  }
  return Math.max(1, Math.floor(value));
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
