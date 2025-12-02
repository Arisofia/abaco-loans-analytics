# Vercel Framework Preset Recommendation

## Recommendation
Choose **Next.js (App Router, Next.js 14+)** as the framework preset. Your team is already expert in Next.js, and the mixed static/dynamic data profile plus fintech analytics requirements benefit from SSR/SSG/ISR, streaming Server Components, Edge Middleware, and Vercel-native optimizations (Image Optimization, Analytics, Speed Insights).

## Comparative Analysis
| Dimension | Next.js (App Router) | Vite SPA (React) |
| --- | --- | --- |
| Initial Load (FCP/LCP) | Faster via SSR/SSG/ISR, Partial Prerendering (PPR), streaming; delivers HTML before hydration | Slower first paint; waits for client bundle and API fetch before meaningful content |
| SEO | First-class SSR/SSG/ISR so crawlers get HTML immediately | CSR only; requires prerendering workarounds for SEO |
| Vercel Optimization | Native Image Optimization, Edge Functions/Middleware, Route Handlers, Server Actions, caching | Mostly static hosting; Edge/Middleware patterns require manual setup |
| Real-Time/Data | Server Components stream data; Route Handlers/APIs co-located; good for dashboards | Client-only fetching; higher time-to-data and larger hydration payload |
| Complexity | Moderate (SSR/RSC concepts), aligned to team expertise | Lower for pure CSR, but SEO/SSR needs add-ons |
| Scalability | Global edge network, ISR caching, DB pooling patterns | Requires separate backend/services; fewer built-ins for scale |

## Deployment Strategy for Vercel
- **Framework Preset:** Next.js (auto-detected, but set explicitly if desired)
- **Install Command:** `npm install`
- **Build Command:** `npm run build`
- **Output Directory:** `.next`
- **Environment Variables (examples):**
  - `NODE_ENV=production`
  - `DATABASE_URL=<postgres_url>`
  - `NEXT_PUBLIC_API_URL=<public_api>`
- **Observability:** Add `@vercel/analytics` and `@vercel/speed-insights` in `app/layout.tsx` to capture Web Vitals and performance KPIs.
- **Security:** Enforce auth via Edge Middleware on `/dashboard` and `/api`; apply HSTS, Referrer-Policy, and Permissions-Policy headers.

## Copy/Paste Commands
```bash
# Install dependencies
npm install

# Lint / type-check / test (if defined) / build
npm run lint
npm run test   # if present
npm run build

# Deploy (after `vercel link`)
vercel
vercel --prod
```
