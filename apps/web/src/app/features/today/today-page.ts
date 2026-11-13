import { Component, OnInit, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { MatchCard } from './match-card/match-card';
import { Match } from './match.model';
import { MOCK_MATCHES } from './mock-matches';

/**
 * The Today page: today's matches as a list of cards.
 * For now the data is mock data; in W2 it moves into a service,
 * and later it comes from FastAPI.
 */
@Component({
  selector: 'app-today-page',
  imports: [DatePipe, MatchCard],
  templateUrl: './today-page.html',
  styleUrl: './today-page.scss',
})
export class TodayPage implements OnInit {
  // signal() = a reactive value, like useState. Read: matches(). Write: set()/update().
  // (Signals get their own step in W2; here we only need a list we can change.)
  protected readonly matches = signal<Match[]>(MOCK_MATCHES);

  protected readonly today = new Date();

  ngOnInit(): void {
    console.log(`[TodayPage] ngOnInit: ${this.matches().length} matches`);
  }

  // Called when a card emits (skip). UI only for now: it just hides the card.
  protected onSkip(matchId: number): void {
    this.matches.update((list) => list.filter((m) => m.id !== matchId));
  }
}
