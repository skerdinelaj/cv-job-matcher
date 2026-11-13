// TEMPORARY: written by hand to match the planned `GET /matches` response.
// In W3 this file is deleted and replaced by types generated from FastAPI's
// OpenAPI schema (we never hand-write API types once the endpoint exists).
// Keys are snake_case because that is what FastAPI sends in JSON.

/** Where the job accepts people from (extracted during enrichment). */
export type LocationRule = 'worldwide' | 'europe' | 'country_restricted' | 'unclear';

/** The job part of a match: only the fields the Today page shows. */
export interface MatchJob {
  id: number;
  source: string; // e.g. "remoteok", the UI links back to it
  url: string; // the original posting
  title: string;
  company: string;
  location: string | null;
  posted_at: string | null; // ISO date string, e.g. "2026-11-12T08:00:00Z"
  location_rule: LocationRule;
  apply_email: string | null; // set only for "email jobs"
}

/** One scored match between a job and my CV. */
export interface Match {
  id: number;
  score: number; // 0-100, calculated in code (never by the LLM)
  matched_skills: string[];
  missing_skills: string[];
  why_text: string;
  created_at: string;
  job: MatchJob;
}
