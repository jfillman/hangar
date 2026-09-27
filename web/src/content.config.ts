import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

// Hangar's product docs, pulled from each repo by scripts/sync-docs.mjs.
const docs = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/docs.generated' }),
  schema: z.object({
    title: z.string(),
    product: z.string(),
    route: z.string(),
    source: z.string(),
  }),
});

export const collections = { docs };
