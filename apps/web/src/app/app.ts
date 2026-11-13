import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

/**
 * The root component = the app layout: top bar + nav + the current page.
 * <router-outlet /> is where the router renders the page for the current URL.
 */
@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {
  // The nav items, so the template can loop over them with @for.
  protected readonly navItems = [
    { path: '/today', label: 'Today' },
    { path: '/drafts', label: 'Drafts' },
    { path: '/applications', label: 'Applications' },
    { path: '/cv', label: 'CV' },
    { path: '/stats', label: 'Stats' },
  ];
}
