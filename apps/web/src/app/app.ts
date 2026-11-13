import { Component } from '@angular/core';
import { TodayPage } from './features/today/today-page';

/**
 * The root component (rendered into <app-root> in index.html).
 * For now it shows the Today page directly; in W3 the router takes over
 * and this becomes the layout with a <router-outlet />.
 */
@Component({
  selector: 'app-root',
  imports: [TodayPage],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {}
