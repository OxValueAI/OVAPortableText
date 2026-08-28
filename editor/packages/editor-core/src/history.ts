import type { OVAReportDocument } from "./types";
import { cloneDocument } from "./json";

export interface HistoryState {
  past: OVAReportDocument[];
  present: OVAReportDocument;
  future: OVAReportDocument[];
}

export function createHistory(document: OVAReportDocument): HistoryState {
  return {
    past: [],
    present: cloneDocument(document),
    future: []
  };
}

export function pushHistory(state: HistoryState, document: OVAReportDocument): HistoryState {
  return {
    past: [...state.past, cloneDocument(state.present)],
    present: cloneDocument(document),
    future: []
  };
}

export function undo(state: HistoryState): HistoryState {
  const previous = state.past.at(-1);
  if (!previous) {
    return state;
  }

  return {
    past: state.past.slice(0, -1),
    present: previous,
    future: [cloneDocument(state.present), ...state.future]
  };
}

export function redo(state: HistoryState): HistoryState {
  const next = state.future[0];
  if (!next) {
    return state;
  }

  return {
    past: [...state.past, cloneDocument(state.present)],
    present: next,
    future: state.future.slice(1)
  };
}
