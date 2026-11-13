import { Pipe, PipeTransform } from '@angular/core';

/**
 * Turns a score (0-100) into a short label for the UI.
 * Usage in a template: {{ match.score | scoreLabel }}
 *
 * Pipes are "pure" by default: Angular re-runs transform() only when the
 * input value changes, so it is cheap to use in lists.
 */
@Pipe({ name: 'scoreLabel' })
export class ScoreLabelPipe implements PipeTransform {
  transform(score: number): string {
    if (score >= 85) return 'Strong match';
    if (score >= 70) return 'Good match';
    return 'Weak match';
  }
}
