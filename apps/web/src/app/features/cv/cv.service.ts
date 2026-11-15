import { Injectable, signal } from '@angular/core';

/**
 * Knows whether I have uploaded a CV.
 * MOCK for now: a simple flag I can toggle on the CV page (it resets on page
 * reload). When the backend has CVs (step 5), this asks FastAPI instead.
 */
@Injectable({ providedIn: 'root' })
export class CvService {
  private readonly _hasCv = signal(false);
  readonly hasCv = this._hasCv.asReadonly();

  /** Mock only: pretend a CV was uploaded / removed. */
  setHasCv(value: boolean): void {
    this._hasCv.set(value);
  }
}
