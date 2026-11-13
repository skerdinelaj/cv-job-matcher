import { Component, OnInit, computed, effect, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { MatchCard } from './match-card/match-card';
import { MatchesService } from './matches.service';
import { DEFAULT_MIN_SCORE } from './today.tokens';

/**
 * The Today page: today's matches as cards, with two filters.
 * The data lives in MatchesService; this component only keeps the filter
 * state (which is UI state, so it belongs to the page).
 */
@Component({
  selector: 'app-today-page',
  imports: [DatePipe, MatchCard],
  templateUrl: './today-page.html',
  styleUrl: './today-page.scss',
})
export class TodayPage implements OnInit {
  // inject() = ask Angular for an instance (like useContext / a store hook).
  private readonly matchesService = inject(MatchesService);
  private readonly defaultMinScore = inject(DEFAULT_MIN_SCORE);

  protected readonly today = new Date();

  // Filter state: writable signals (like useState).
  protected readonly minScore = signal(this.defaultMinScore);
  protected readonly emailOnly = signal(false);

  // computed() = derived state (like useMemo, but no dependency array:
  // Angular tracks which signals are read inside and re-runs when they change).
  protected readonly visibleMatches = computed(() => {
    const min = this.minScore();
    const emailOnly = this.emailOnly();
    return this.matchesService
      .matches()
      .filter((m) => m.score >= min && (!emailOnly || m.job.apply_email !== null));
  });

  protected readonly totalCount = this.matchesService.count;
  protected readonly hiddenCount = computed(() => this.totalCount() - this.visibleMatches().length);

  constructor() {
    // effect() = a side effect that re-runs when the signals it reads change
    // (like useEffect, again without a dependency array).
    // Use it for logging, localStorage, etc. Never to set other signals: use computed() for that.
    // (An effect must be created here or in a field: Angular needs the component's context.)
    effect(() => {
      console.log(
        `[TodayPage] filters: min=${this.minScore()}, emailOnly=${this.emailOnly()}` +
          ` → ${this.visibleMatches().length} shown`,
      );
    });
  }

  ngOnInit(): void {
    console.log(`[TodayPage] ngOnInit: ${this.totalCount()} matches`);
  }

  protected onMinScoreInput(event: Event): void {
    // The range input gives us the DOM event; read the number from its target.
    const input = event.target as HTMLInputElement;
    this.minScore.set(input.valueAsNumber);
  }

  protected toggleEmailOnly(): void {
    this.emailOnly.update((value) => !value);
  }

  protected resetFilters(): void {
    this.minScore.set(this.defaultMinScore);
    this.emailOnly.set(false);
  }

  // The card emits (skip); the service owns the data, so it does the change.
  protected onSkip(matchId: number): void {
    this.matchesService.skip(matchId);
  }
}
