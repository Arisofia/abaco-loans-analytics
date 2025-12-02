# Vercel Framework Recommendation

## Context
- **Project type:** Other (fintech analytics)
- **Stack:** React, TypeScript, Tailwind CSS, Node.js, with mixed data strategy
- **Goals:** SEO, fast initial load, rapid delivery, dynamic data handling
- **Team expertise:** Expert in Next.js and SSR

## Recommendation
Choose **Next.js 14+ (App Router)** as the Vercel Framework Preset. It provides SSR/SSG, Partial Prerendering (PPR), Image Optimization, Edge Middleware, and native analytics. This aligns with mixed dynamic/static needs, high SEO requirements, and team skills.

## Comparison vs Vite/SPA
| Capability | Next.js (App Router) | Vite/SPA (React) |
| --- | --- | --- |
| Initial Load (FCP/LCP) | Faster via SSR/SSG + RSC streaming | Slower; full client bundle hydration |
| SEO | Full SSR/SSG; crawler-ready HTML | CSR; needs extra pre-rendering setup |
| Vercel Optimizations | Native Image Optimization, Edge Functions, ISR, Middleware | Limited; manual CDN/config needed |
| Dynamic Data | Server Components + client streaming; DB-friendly | Client-only fetch; higher latency |
| Complexity | Moderate (SSR/RSC concepts) | Low (CSR only) |
| Scalability | Edge + Serverless pooling, cache control | Requires separate backend stack |

## Deployment Strategy (Vercel)
- **Framework Preset:** Next.js
- **Install command:** `npm ci`
- **Build command:** `npm run build`
- **Output directory:** `.next`
- **Environment:** add `NODE_ENV=production`, `DATABASE_URL`, `NEXT_PUBLIC_API_URL`
- **Performance tooling:** add `@vercel/analytics` and `@vercel/speed-insights` in `app/layout.tsx` to track FCP/LCP and real-user metrics.

## Operational KPIs & Traceability
- **Performance:** FCP/LCP <2s (Speed Insights), TTFB via Edge regions, cache hit rates.
- **Reliability:** Error rate <0.1% (Vercel Analytics + logging), ISR revalidation success, API latency p95.
- **Security & Compliance:** HSTS/Permissions-Policy headers, audit via git history and Vercel deployments.
- **Collaboration:** Enforce PR checks (lint, typecheck, build), GitHub Actions for CI, and Vercel preview deployments for each PR.

## Commands (local/CI)
- Install: `npm ci`
- Lint: `npm run lint`
- Type check: `npm run typecheck` (or `tsc --noEmit`)
- Build: `npm run build`
- Deploy preview: `vercel`
- Deploy production: `vercel --prod`
