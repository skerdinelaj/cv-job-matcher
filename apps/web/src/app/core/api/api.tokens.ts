import { InjectionToken } from '@angular/core';

/**
 * Where the API lives, as seen from the browser.
 * '/api' works in dev (proxy.conf.json forwards it to FastAPI) and in Docker
 * (nginx forwards it). Services call short paths like '/health' and the
 * apiBaseUrlInterceptor adds this prefix.
 */
export const API_BASE_URL = new InjectionToken<string>('API_BASE_URL', {
  providedIn: 'root',
  factory: () => '/api',
});
