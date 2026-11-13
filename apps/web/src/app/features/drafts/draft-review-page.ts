import { Component, input, numberAttribute } from '@angular/core';
import { RouterLink } from '@angular/router';

/**
 * Review one draft: /drafts/:id
 *
 * With withComponentInputBinding() (see app.config.ts), the router puts the
 * :id from the URL into this input automatically. No ActivatedRoute needed.
 * The URL always gives a string; `numberAttribute` turns "2" into 2.
 */
@Component({
  selector: 'app-draft-review-page',
  imports: [RouterLink],
  template: `
    <a routerLink="/drafts">← Back to drafts</a>
    <h2>Draft #{{ id() }}</h2>
    <p>The full review screen (job, score, editable draft, Send / Skip) comes in W4.</p>
  `,
})
export class DraftReviewPage {
  // The input name must match the route param name (:id).
  readonly id = input.required({ transform: numberAttribute });
}
