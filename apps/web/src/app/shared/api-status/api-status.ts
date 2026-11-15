import { Component } from '@angular/core';
import { httpResource } from '@angular/common/http';
import { HealthResponse } from '../../core/api/health.model';

/**
 * A small "API ok / API down" badge for the top bar.
 *
 * httpResource() = an HTTP GET whose result is exposed as signals:
 * value(), error(), isLoading(), hasValue(). It's like useQuery/useSWR:
 * no subscribe, no manual loading flags. It uses HttpClient underneath,
 * so our interceptors run on it too ('/health' → '/api/health').
 */
@Component({
  selector: 'app-api-status',
  template: `
    @if (health.isLoading()) {
      <span class="status">Checking API…</span>
    } @else if (health.hasValue()) {
      <span class="status status--ok">● API {{ health.value().status }}</span>
    } @else {
      <span class="status status--down">● API down</span>
    }
    <!-- reload() = fetch again -->
    <button type="button" class="status__retry" (click)="health.reload()">Check</button>
  `,
  styles: `
    :host {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.85rem;
    }
    .status {
      color: #cbd5e1;
    }
    .status--ok {
      color: #4ade80;
    }
    .status--down {
      color: #f87171;
    }
    .status__retry {
      border: 1px solid #4b5563;
      background: transparent;
      color: #cbd5e1;
      border-radius: 6px;
      padding: 2px 8px;
      cursor: pointer;
    }
  `,
})
export class ApiStatus {
  // Important: read value() only after hasValue() is true; in an error state value() throws.
  protected readonly health = httpResource<HealthResponse>(() => '/health');
}
