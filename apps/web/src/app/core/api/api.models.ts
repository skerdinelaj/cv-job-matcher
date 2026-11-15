import type { components } from './api-types';

/**
 * Short names for the API types.
 *
 * api-types.ts is GENERATED from FastAPI's OpenAPI schema (`npm run api:types`).
 * Never edit it by hand: change the Pydantic model in FastAPI and regenerate.
 * This file only gives the generated types friendlier names.
 */
type Schemas = components['schemas'];

export type HealthResponse = Schemas['HealthOut'];
