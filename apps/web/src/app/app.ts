import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { ErrorService } from './core/errors/error.service';
import { LoadingService } from './core/loading/loading.service';
import { ApiStatus } from './shared/api-status/api-status';

/**
 * The root component = the app layout: loading bar, top bar + nav,
 * error banner, and the current page.
 * <router-outlet /> is where the router renders the page for the current URL.
 */
@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive, ApiStatus],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {
  protected readonly loading = inject(LoadingService);
  protected readonly errors = inject(ErrorService);

  // The nav items, so the template can loop over them with @for.
  protected readonly navItems = [
    { path: '/today', label: 'Today' },
    { path: '/drafts', label: 'Drafts' },
    { path: '/applications', label: 'Applications' },
    { path: '/cv', label: 'CV' },
    { path: '/stats', label: 'Stats' },
  ];
}
