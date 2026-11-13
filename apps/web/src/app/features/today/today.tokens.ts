import { InjectionToken } from '@angular/core';

/**
 * The starting value of the "min score" filter on the Today page.
 *
 * An InjectionToken is a key for injecting a value that is not a class
 * (a number, a string, a config object). Read it with inject(DEFAULT_MIN_SCORE).
 *
 * `factory` gives the default (70). Any provider can override it, e.g. in
 * app.config.ts: { provide: DEFAULT_MIN_SCORE, useValue: 60 }.
 */
export const DEFAULT_MIN_SCORE = new InjectionToken<number>('DEFAULT_MIN_SCORE', {
  providedIn: 'root',
  factory: () => 70,
});
