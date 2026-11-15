import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { API_BASE_URL } from '../api/api.tokens';

/**
 * Adds the API prefix to relative URLs: '/health' → '/api/health'.
 * Absolute URLs (http://..., https://...) are left alone.
 *
 * An interceptor is a function that sees every HTTP request on its way out
 * (and the response on its way back), like axios interceptors.
 * Requests are immutable, so we clone() with the change.
 */
export const apiBaseUrlInterceptor: HttpInterceptorFn = (req, next) => {
  const baseUrl = inject(API_BASE_URL);
  const isAbsolute = /^https?:\/\//.test(req.url);

  if (isAbsolute || req.url.startsWith(baseUrl)) {
    return next(req);
  }
  return next(req.clone({ url: `${baseUrl}${req.url}` }));
};
