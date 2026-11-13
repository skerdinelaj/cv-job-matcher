import { Component, OnDestroy, OnInit, input, output } from '@angular/core';
import { DatePipe, TitleCasePipe } from '@angular/common';
import { ScoreLabelPipe } from '../../../shared/pipes/score-label.pipe';
import { Match } from '../match.model';

/**
 * Shows one match as a card. It only displays data and reports clicks:
 * the parent owns the list and decides what "skip" does.
 */
@Component({
  selector: 'app-match-card',
  // A standalone component lists what its template uses (like imports in a .tsx file).
  imports: [DatePipe, TitleCasePipe, ScoreLabelPipe],
  templateUrl: './match-card.html',
  styleUrl: './match-card.scss',
})
export class MatchCard implements OnInit, OnDestroy {
  // input.required<T>() = a required prop. Read it as a function: match().
  readonly match = input.required<Match>();

  // output<T>() = a callback prop. The parent listens with (skip)="...".
  readonly skip = output<number>();

  // Lifecycle hook: runs once, after the first inputs are set.
  // (In the constructor, inputs are NOT available yet.)
  ngOnInit(): void {
    console.log(`[MatchCard] created: match ${this.match().id}`);
  }

  // Lifecycle hook: runs when Angular removes the card from the page.
  ngOnDestroy(): void {
    console.log(`[MatchCard] destroyed: match ${this.match().id}`);
  }

  protected onSkip(): void {
    this.skip.emit(this.match().id);
  }
}
