import { Component, inject, input } from '@angular/core';
import { CvService } from './cv.service';

/**
 * The CV page. Upload and skill chips come in W4.
 * For now: a mock switch to test the CV guard on Draft review.
 */
@Component({
  selector: 'app-cv-page',
  template: `
    <h2>CV</h2>

    <!-- reason comes from the URL (?reason=cv-required), bound as an input -->
    @if (reason() === 'cv-required' && !cv.hasCv()) {
      <p class="notice">Upload a CV first: drafts are written from your CV.</p>
    }

    <p>
      CV uploaded: <strong>{{ cv.hasCv() ? 'yes' : 'no' }}</strong>
      <button type="button" (click)="cv.setHasCv(!cv.hasCv())">
        {{ cv.hasCv() ? 'Remove mock CV' : 'Pretend I uploaded a CV' }}
      </button>
    </p>
    <p>Upload and skill chips come in W4.</p>
  `,
  styles: `
    .notice {
      background: #fef3c7;
      color: #78350f;
      padding: 10px 14px;
      border-radius: 8px;
    }
    button {
      margin-left: 8px;
    }
  `,
})
export class CvPage {
  protected readonly cv = inject(CvService);

  // withComponentInputBinding() also binds QUERY params: /cv?reason=x → reason() === 'x'.
  readonly reason = input<string>();
}
