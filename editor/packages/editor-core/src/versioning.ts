import type { OVAReportDocument } from "./types";
import { cloneDocument, stringifyDocument } from "./json";
import { validateDocument } from "./validation";

export interface BrowserVersioningOptions {
  enabled: boolean;
  documentKey: string;
  namespace?: string;
  maxVersions?: number;
}

export interface SavedVersionMeta {
  id: string;
  namespace: string;
  documentKey: string;
  label: string;
  createdAt: string;
  schemaVersion?: string;
  validationStatus: "valid" | "warning" | "error";
  sizeBytes: number;
}

export interface SavedVersion extends SavedVersionMeta {
  document: OVAReportDocument;
}

const DB_NAME = "ova-portable-text-editor";
const DB_VERSION = 1;
const STORE_NAME = "versions";
const DEFAULT_NAMESPACE = "default";
const DEFAULT_MAX_VERSIONS = 20;

export async function saveVersion(
  document: OVAReportDocument,
  options: BrowserVersioningOptions,
  label?: string
): Promise<SavedVersion> {
  ensureVersioningEnabled(options);

  const db = await openVersionDB();
  const createdAt = new Date().toISOString();
  const validation = validateDocument(document);
  const status = validation.issues.some((issue) => issue.severity === "error")
    ? "error"
    : validation.issues.some((issue) => issue.severity === "warning")
      ? "warning"
      : "valid";
  const record: SavedVersion = {
    id: crypto.randomUUID(),
    namespace: options.namespace ?? DEFAULT_NAMESPACE,
    documentKey: options.documentKey,
    label: label?.trim() || createdAt,
    createdAt,
    validationStatus: status,
    sizeBytes: new Blob([stringifyDocument(document, false)]).size,
    document: cloneDocument(document),
    ...(document.schemaVersion ? { schemaVersion: document.schemaVersion } : {})
  };

  const existing = await listVersions(options);
  const maxVersions = options.maxVersions ?? DEFAULT_MAX_VERSIONS;
  if (existing.length >= maxVersions) {
    throw new Error(`Version limit reached (${maxVersions}). Delete an older version before saving.`);
  }

  await requestToPromise(db.transaction(STORE_NAME, "readwrite").objectStore(STORE_NAME).put(record));
  return record;
}

export async function listVersions(options: BrowserVersioningOptions): Promise<SavedVersionMeta[]> {
  ensureVersioningEnabled(options);

  const db = await openVersionDB();
  const records = await getAllVersions(db);
  return records
    .filter((record) => sameDocument(record, options))
    .map(({ document: _document, ...meta }) => meta)
    .sort((a, b) => b.createdAt.localeCompare(a.createdAt));
}

export async function loadVersion(
  options: BrowserVersioningOptions,
  versionId: string
): Promise<SavedVersion | undefined> {
  ensureVersioningEnabled(options);

  const db = await openVersionDB();
  const record = await requestToPromise<SavedVersion | undefined>(
    db.transaction(STORE_NAME, "readonly").objectStore(STORE_NAME).get(versionId)
  );
  return record && sameDocument(record, options) ? record : undefined;
}

export async function renameVersion(
  options: BrowserVersioningOptions,
  versionId: string,
  label: string
): Promise<SavedVersionMeta | undefined> {
  ensureVersioningEnabled(options);

  const db = await openVersionDB();
  const record = await requestToPromise<SavedVersion | undefined>(
    db.transaction(STORE_NAME, "readonly").objectStore(STORE_NAME).get(versionId)
  );
  if (!record || !sameDocument(record, options)) {
    return undefined;
  }

  record.label = label.trim() || record.label;
  await requestToPromise(db.transaction(STORE_NAME, "readwrite").objectStore(STORE_NAME).put(record));
  const { document: _document, ...meta } = record;
  return meta;
}

export async function deleteVersion(options: BrowserVersioningOptions, versionId: string): Promise<boolean> {
  ensureVersioningEnabled(options);

  const existing = await loadVersion(options, versionId);
  if (!existing) {
    return false;
  }

  const db = await openVersionDB();
  await requestToPromise(db.transaction(STORE_NAME, "readwrite").objectStore(STORE_NAME).delete(versionId));
  return true;
}

function ensureVersioningEnabled(options: BrowserVersioningOptions): void {
  if (!options.enabled) {
    throw new Error("Browser versioning is disabled.");
  }
  if (!options.documentKey) {
    throw new Error("Browser versioning requires a stable documentKey.");
  }
  if (typeof indexedDB === "undefined") {
    throw new Error("IndexedDB is not available in this environment.");
  }
}

function sameDocument(record: SavedVersionMeta, options: BrowserVersioningOptions): boolean {
  return (
    record.namespace === (options.namespace ?? DEFAULT_NAMESPACE) &&
    record.documentKey === options.documentKey
  );
}

function openVersionDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        const store = db.createObjectStore(STORE_NAME, { keyPath: "id" });
        store.createIndex("document", ["namespace", "documentKey"], { unique: false });
        store.createIndex("createdAt", "createdAt", { unique: false });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

function getAllVersions(db: IDBDatabase): Promise<SavedVersion[]> {
  return requestToPromise<SavedVersion[]>(
    db.transaction(STORE_NAME, "readonly").objectStore(STORE_NAME).getAll()
  );
}

function requestToPromise<T>(request: IDBRequest<T>): Promise<T> {
  return new Promise((resolve, reject) => {
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}
