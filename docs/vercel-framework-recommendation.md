# Vercel Framework Recommendation

## Project Context
- **Project type:** Other (fintech/analytics dashboards & marketing surfaces)
- **Tech stack:** React, TypeScript, Tailwind CSS, Node.js backend (monorepo-friendly)
- **Primary goals:** SEO, fast initial load, development speed, dynamic data delivery
- **Data strategy:** Mixed (static marketing + dynamic dashboards via APIs/DB)
- **Team expertise:** Expert in Next.js and comfortable with SSR/RSC

## Recommendation: Next.js (App Router, Vercel Preset)
Next.js 14+ with the App Router is the optimal Vercel preset because it blends Server Components, ISR/SSG, and Edge Functions for low-latency fintech experiences while keeping a cohesive React developer workflow.

### Why it fits
- **Performance & UX:** Server Components + Streaming SSR reduce bundle size and time-to-hydration; ISR keeps marketing pages fast while dashboards stream real-time data.
- **SEO:** Native SSR/SSG ensures crawlable HTML; built-in metadata API and dynamic routes simplify structured data.
- **Vercel-native:** First-class support for Image Optimization, Edge Middleware/Functions, and Analytics/Speed Insights without custom infra.
- **Scalability:** Incremental adoption of Partial Prerendering (PPR), Route Handlers, and middleware enables global, compliant delivery with clear observability.

## Comparison: Next.js vs. Vite/SPA (React)
| Dimension | Next.js (App Router) | Vite/SPA (React) |
| --- | --- | --- |
| Initial Load (FCP/LCP) | Faster via SSR/SSG, streaming, and smaller client bundles | Slower; full client hydration before content is interactive |
| SEO | Strong: SSR/SSG, metadata API, sitemap/robots automation | Weak by default (CSR); requires prerendering add-ons |
| Vercel Optimization | Native Image Optimization, Edge Middleware/Functions, ISR/PPR, Analytics/Speed Insights | Limited; manual CDN/image tooling; Edge requires custom config |
| Data Delivery | Server Components fetch on server; Route Handlers/Edge Functions for low-latency APIs | Client-only fetch; separate backend service needed |
| Complexity | Moderate (SSR/RSC patterns) | Lower (CSR-only), but adds infra burden for SEO/perf |
| Observability | Built-in Vercel Analytics & Speed Insights; simple logging for Route Handlers/Edge | Needs third-party wiring for traces/metrics |

## Deployment Strategy (Vercel)
- **Framework Preset:** Next.js (auto-detected; confirm in Vercel settings)
- **Install Command:** `npm install`
- **Build Command:** `npm run build`
- **Output Directory:** `.next`
- **Environment:** Configure env vars (e.g., `NEXT_PUBLIC_APP_ENV`, `DATABASE_URL`) in Vercel; use `vercel env pull .env.local` for local parity.
- **Edge/Server:** Use Route Handlers for API needs and Middleware for auth/region routing; set memory/timeouts per endpoint if needed.

## KPIs, Measurements, and Traceability
- **Performance:** Track FCP/LCP/TTFB via Vercel Speed Insights; set alerts for regressions >10% week-over-week.
- **Reliability:** Error rates and latency for Route Handlers/Edge Functions; SLOs per critical route.
- **Delivery:** Build success rate and duration in GitHub Actions; cache hit ratios for artifacts.
- **SEO:** Organic impressions/click-through; index coverage; structured data validation.
- **Usage:** Dashboard engagement (session length, funnel completion), API call volume, and cache effectiveness.

## Commands (copy/paste)
```bash
npm install
npm run lint
npm run build
vercel --prod
```
