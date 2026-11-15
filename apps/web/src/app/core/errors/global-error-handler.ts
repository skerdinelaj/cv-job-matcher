import { ErrorHandler, Injectable, inject } from '@angular/core';
import { ErrorService } from './error.service';

/**
 * Angular sends every uncaught error to an ErrorHandler. The default one only
 * logs to the console. Ours also shows the banner, so errors are never silent.
 *
 * Registered in app.config.ts with { provide: ErrorHandler, useClass: GlobalErrorHandler }:
 * "when someone asks for ErrorHandler, give them this class instead".
 */
@Injectable()
export class GlobalErrorHandler implements ErrorHandler {
  private readonly errors = inject(ErrorService);

  handleError(error: unknown): void {
    console.error('[GlobalErrorHandler]', error);
    this.errors.show('Something went wrong in the app. Details are in the console.');
  }
}
