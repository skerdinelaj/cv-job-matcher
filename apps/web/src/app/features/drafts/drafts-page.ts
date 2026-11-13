import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

/**
 * The draft queue. Placeholder for now: a few fake drafts so we can practise
 * links with a route parameter (/drafts/1, /drafts/2...).
 * Real drafts come from FastAPI (`GET /drafts?status=draft`) later.
 */
@Component({
  selector: 'app-drafts-page',
  imports: [RouterLink],
  template: `
    <h2>Drafts</h2>
    <ul class="list">
      @for (draft of drafts; track draft.id) {
        <li>
          <!-- [routerLink] with an array builds the URL: ['/drafts', 1] → /drafts/1 -->
          <a [routerLink]="['/drafts', draft.id]">{{ draft.title }}</a>
        </li>
      }
    </ul>
  `,
})
export class DraftsPage {
  protected readonly drafts = [
    { id: 1, title: 'Senior Frontend Engineer · Northwind Labs' },
    { id: 2, title: 'Full-Stack Developer (AI products) · Blue Fjord AI' },
  ];
}
