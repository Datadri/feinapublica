import type { FilterOptions, Posting, PostingChange } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function fetchOptions(): Promise<FilterOptions> {
  const res = await fetch(`${API_BASE}/api/options`);
  return res.json();
}

export async function fetchPostings(params: URLSearchParams): Promise<{ items: Posting[]; total: number }> {
  const res = await fetch(`${API_BASE}/api/postings?${params.toString()}`);
  return res.json();
}

export async function fetchPostingDetail(id: number): Promise<{ item: Posting | null; changes: PostingChange[] }> {
  const res = await fetch(`${API_BASE}/api/postings/${id}`);
  return res.json();
}

export async function fetchRecentChanges(limit = 50): Promise<PostingChange[]> {
  const res = await fetch(`${API_BASE}/api/changes/recent?limit=${limit}`);
  return res.json();
}