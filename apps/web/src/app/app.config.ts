import { ApplicationConfig, ErrorHandler, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideHttpClient, withFetch, withInterceptors } from '@angular/common/http';
import { provideRouter, withComponentInputBinding } from '@angular/router';
import { routes } from './app.routes';
import { GlobalErrorHandler } from './core/errors/global-error-handler';
import { apiBaseUrlInterceptor } from './core/interceptors/api-base-url.interceptor';
import { errorInterceptor } from './core/interceptors/error.interceptor';
import { loadingInterceptor } from './core/interceptors/loading.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    // Sends uncaught browser errors (window 'error' events) to the ErrorHandler below.
    provideBrowserGlobalErrorListeners(),
    // Replace Angular's default ErrorHandler with ours (a "useClass" provider).
    { provide: ErrorHandler, useClass: GlobalErrorHandler },
    // withComponentInputBinding(): route params (:id) arrive as component inputs.
    provideRouter(routes, withComponentInputBinding()),
    // HttpClient for the whole app. withFetch() uses the browser's fetch() underneath.
    // Interceptors run in this order on the way out (and in reverse on the way back).
    provideHttpClient(
      withFetch(),
      withInterceptors([apiBaseUrlInterceptor, loadingInterceptor, errorInterceptor]),
    ),
  ],
};
