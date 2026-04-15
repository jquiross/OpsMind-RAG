export type Citation = {
  document_title: string;
  chunk_id: string;
};

export type Triage = {
  severity: string;
  needs_human: boolean;
  confidence: number;
  reasoning_summary: string;
  suggested_next_steps: string[];
  label: string;
};

export type ChatResponse = {
  summary: string;
  probable_cause: string;
  suggested_steps: string[];
  confidence: number;
  needs_human: boolean;
  severity: string;
  citations: Citation[];
  triage: Triage;
  query_id: string;
  rewritten_query?: string | null;
  insufficient_evidence: boolean;
  injection_signals: string[];
};
