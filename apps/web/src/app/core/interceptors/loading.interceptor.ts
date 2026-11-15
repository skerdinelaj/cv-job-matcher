import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { finalize } from 'rxjs';
import { LoadingService } from '../loading/loading.service';

/**
 * Turns the loading bar on when a request starts and off when it ends.
 *
 * next(req) returns an Observable (an RxJS stream of the response).
 * finalize() runs when the stream ends: success, error OR cancel, so the
 * counter always goes back down. (RxJS gets its own step in W5.)
 */
export const loadingInterceptor: HttpInterceptorFn = (req, next) => {
  const loading = inject(LoadingService);
  loading.start();
  return next(req).pipe(finalize(() => loading.stop()));
};
