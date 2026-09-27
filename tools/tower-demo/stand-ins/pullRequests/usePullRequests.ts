import { useEffect, useState } from 'react';
import { demoPullRequests } from '../../mock/fixtures';

export type CiState = 'success' | 'failure' | 'pending' | 'unknown';
export interface PrCheckRun {
  name: string;
  status: 'queued' | 'in_progress' | 'completed';
  conclusion?: string;
  message?: string;
  commentUrl?: string;
}
export interface PullRequestSummary {
  number: number;
  title: string;
  url: string;
  repo: 'source' | 'gitops';
  state: 'open' | 'merged' | 'closed';
  draft?: boolean;
  author?: string;
  body?: string;
  labels: string[];
  createdAt: string;
  updatedAt: string;
  mergedAt?: string;
  mergeCommitSha?: string;
  review?: { state: 'approved' | 'changes_requested' | 'pending' };
  ci?: { state: CiState; passedChecks: number; totalChecks: number; checks?: PrCheckRun[] };
}
export function usePullRequests(target: { owner: string; appName: string } | undefined, refreshNonce = 0) {
  const [state, setState] = useState<{ loading: boolean; error?: string; data?: PullRequestSummary[] }>({ loading: Boolean(target) });
  const key = target ? `${target.owner}/${target.appName}` : '';
  useEffect(() => {
    if (!target) { setState({ loading: false }); return undefined; }
    const t = setTimeout(() => setState({ loading: false, data: demoPullRequests(target.appName) }), 200);
    return () => clearTimeout(t);
  }, [key, refreshNonce]);
  return state;
}
