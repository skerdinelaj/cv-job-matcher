import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

/** Shown for any URL that matches no route (the '**' route). */
@Component({
  selector: 'app-not-found-page',
  imports: [RouterLink],
  template: `
    <h2>Page not found</h2>
    <p><a routerLink="/today">Go to Today</a></p>
  `,
})
export class NotFoundPage {}
