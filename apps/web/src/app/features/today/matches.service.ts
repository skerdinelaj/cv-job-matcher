import { Injectable, computed, signal } from '@angular/core';
import { Match } from './match.model';
import { MOCK_MATCHES } from './mock-matches';

/**
 * Holds today's matches for the whole app.
 *
 * providedIn: 'root' → Angular creates ONE instance (a singleton) the first
 * time someone asks for it with inject(MatchesService). Every component that
 * injects it gets the same instance, so they all see the same data.
 *
 * Later the data comes from FastAPI (`GET /matches`); components won't change,
 * because they only talk to this service.
 */
@Injectable({ providedIn: 'root' })
export class MatchesService {
  // Private + writable: only this service can change the list.
  private readonly _matches = signal<Match[]>(MOCK_MATCHES);

  // Public + read-only: components can read matches() but cannot call set().
  readonly matches = this._matches.asReadonly();

  // Derived value: recalculates by itself when _matches changes.
  readonly count = computed(() => this._matches().length);

  /** Removes a match from the list (UI only for now; later it calls the API). */
  skip(matchId: number): void {
    this._matches.update((list) => list.filter((m) => m.id !== matchId));
  }
}
