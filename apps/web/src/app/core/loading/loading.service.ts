import { Injectable, computed, signal } from '@angular/core';

/**
 * Counts HTTP requests that are still running.
 * A counter (not a true/false) because several requests can run at once:
 * the bar must stay until the LAST one finishes.
 */
@Injectable({ providedIn: 'root' })
export class LoadingService {
  private readonly pending = signal(0);

  readonly isLoading = computed(() => this.pending() > 0);

  start(): void {
    this.pending.update((n) => n + 1);
  }

  stop(): void {
    this.pending.update((n) => Math.max(0, n - 1));
  }
}
