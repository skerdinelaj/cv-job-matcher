import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { ErrorService } from '../errors/error.service';

/**
 * Global HTTP error handling: one place that turns any failed request into a
 * readable message in the banner, so components don't each need a try/catch.
 *
 * catchError() catches the failed response; throwError() passes the error on,
 * so the caller (e.g. a resource) still knows the request failed.
 */
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const errors = inject(ErrorService);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      errors.show(toMessage(error, req.url));
      return throwError(() => error);
    }),
  );
};

/** A short, human message for each kind of HTTP failure. */
function toMessage(error: HttpErrorResponse, url: string): string {
  if (error.status === 0) return `Can't reach the server (${url}). Check your connection.`;
  if (error.status >= 502 && error.status <= 504) {
    return `The API is not responding (${url}). Is FastAPI running?`;
  }
  if (error.status >= 500) return `Server error ${error.status} on ${url}.`;
  return `Request failed: ${error.status} on ${url}.`;
}
