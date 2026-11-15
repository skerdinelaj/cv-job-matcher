import { Injectable, signal } from '@angular/core';

/**
 * Holds the message shown in the red error banner at the top of the app.
 * Anyone (the error interceptor, the global error handler) can call show().
 */
@Injectable({ providedIn: 'root' })
export class ErrorService {
  private readonly _message = signal<string | null>(null);
  readonly message = this._message.asReadonly();

  show(message: string): void {
    this._message.set(message);
  }

  clear(): void {
    this._message.set(null);
  }
}
