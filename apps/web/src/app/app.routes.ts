import { Routes } from '@angular/router';

/**
 * Every page is lazy-loaded: `loadComponent` + a dynamic import() means the
 * page's code is downloaded only when you first visit it (its own JS chunk),
 * like React.lazy(() => import('./TodayPage')).
 *
 * `title` sets the browser tab title for that page.
 */
export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'today' },
  {
    path: 'today',
    title: 'Today · JobMatch',
    loadComponent: () => import('./features/today/today-page').then((m) => m.TodayPage),
  },
  {
    path: 'drafts',
    title: 'Drafts · JobMatch',
    loadComponent: () => import('./features/drafts/drafts-page').then((m) => m.DraftsPage),
  },
  {
    // :id is a route parameter; DraftReviewPage receives it as an input.
    path: 'drafts/:id',
    title: 'Draft review · JobMatch',
    loadComponent: () =>
      import('./features/drafts/draft-review-page').then((m) => m.DraftReviewPage),
  },
  {
    path: 'applications',
    title: 'Applications · JobMatch',
    loadComponent: () =>
      import('./features/applications/applications-page').then((m) => m.ApplicationsPage),
  },
  {
    path: 'cv',
    title: 'CV · JobMatch',
    loadComponent: () => import('./features/cv/cv-page').then((m) => m.CvPage),
  },
  {
    path: 'stats',
    title: 'Stats · JobMatch',
    loadComponent: () => import('./features/stats/stats-page').then((m) => m.StatsPage),
  },
  {
    // '**' matches anything not matched above. Keep it LAST: routes are checked in order.
    path: '**',
    title: 'Not found · JobMatch',
    loadComponent: () =>
      import('./shared/not-found-page/not-found-page').then((m) => m.NotFoundPage),
  },
];
