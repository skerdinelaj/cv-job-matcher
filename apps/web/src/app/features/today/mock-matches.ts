import { Match } from './match.model';

// Fake data shaped like the real API. Companies and links are made up.
// Replaced by real data from FastAPI once `GET /matches` exists (backend step 6).
export const MOCK_MATCHES: Match[] = [
  {
    id: 1,
    score: 91,
    matched_skills: ['TypeScript', 'React', 'Node.js', 'PostgreSQL'],
    missing_skills: ['GraphQL'],
    why_text: 'Strong overlap on the frontend stack and 5 years of React.',
    created_at: '2026-11-13T06:00:00Z',
    job: {
      id: 101,
      source: 'remoteok',
      url: 'https://example.com/jobs/101',
      title: 'Senior Frontend Engineer',
      company: 'Northwind Labs',
      location: 'Remote, Worldwide',
      posted_at: '2026-11-12T08:00:00Z',
      location_rule: 'worldwide',
      apply_email: 'jobs@northwind.example',
    },
  },
  {
    id: 2,
    score: 78,
    matched_skills: ['Python', 'FastAPI', 'TypeScript'],
    missing_skills: ['Kubernetes', 'AWS'],
    why_text: 'Good match on the API stack; cloud experience is missing.',
    created_at: '2026-11-13T06:00:00Z',
    job: {
      id: 102,
      source: 'arbeitnow',
      url: 'https://example.com/jobs/102',
      title: 'Full-Stack Developer (AI products)',
      company: 'Blue Fjord AI',
      location: 'Remote, Europe',
      posted_at: '2026-11-11T10:30:00Z',
      location_rule: 'europe',
      apply_email: null,
    },
  },
  {
    id: 3,
    score: 64,
    matched_skills: ['React'],
    missing_skills: ['Angular', 'Java', 'Spring'],
    why_text: 'Only the frontend part matches; most backend requirements are missing.',
    created_at: '2026-11-13T06:00:00Z',
    job: {
      id: 103,
      source: 'remotive',
      url: 'https://example.com/jobs/103',
      title: 'Software Engineer',
      company: 'Contoso Cloud',
      location: null,
      posted_at: null,
      location_rule: 'unclear',
      apply_email: null,
    },
  },
];
