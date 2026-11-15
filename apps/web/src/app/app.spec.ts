import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { App } from './app';

describe('App', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [
        // App uses routerLink and <router-outlet>, so the test needs a router (no routes needed).
        provideRouter([]),
        // The API status badge makes an HTTP call. provideHttpClientTesting() swaps the real
        // network for a fake one, so tests never call a real server.
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    }).compileComponents();
  });

  it('should create the app', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    expect(app).toBeTruthy();
  });

  it('should render the app name', () => {
    const fixture = TestBed.createComponent(App);
    // detectChanges() renders the template once. (We don't wait with whenStable():
    // the fake HTTP request never finishes, so the app would never be "stable".)
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('h1')?.textContent).toContain('JobMatch');
  });
});
