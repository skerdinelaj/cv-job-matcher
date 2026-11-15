import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { CvService } from '../../features/cv/cv.service';

/**
 * A guard decides if the router may open a route.
 * Draft review makes no sense without a CV (drafts are written from it),
 * so without one we redirect to /cv?reason=cv-required.
 *
 * Return true → open the route. Return a UrlTree → go there instead.
 * (Returning a UrlTree is better than calling router.navigate() here:
 * the router handles the redirect as part of the same navigation.)
 */
export const cvRequiredGuard: CanActivateFn = () => {
  const cv = inject(CvService);
  if (cv.hasCv()) {
    return true;
  }
  return inject(Router).createUrlTree(['/cv'], { queryParams: { reason: 'cv-required' } });
};
