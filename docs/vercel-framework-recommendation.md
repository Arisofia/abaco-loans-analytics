# Vercel Framework Recommendation

## Context
- **Project type:** Other (fintech analytics)
- **Stack:** React, TypeScript, Tailwind CSS, Node.js, mixed data strategy (API + static content)
- **Goals:** SEO, sub-2s FCP/LCP, dynamic data, rapid delivery
- **Team expertise:** Expert in Next.js and SSR

## Recommendation
Choose **Next.js 14+ (App Router)** as the Framework Preset. It delivers SSR/SSG, Partial Prerendering (PPR), Server Components streaming, Image Optimization, Edge Middleware/Functions, and native analytics. This aligns with mixed dynamic/static needs, high SEO requirements, and existing team skills.

## Comparison vs Vite/SPA
| Metric | Next.js (App Router) | Vite/SPA (React) |
| --- | --- | --- |
| Initial Load (FCP/LCP) | 40–60% faster via SSR/SSG, RSC streaming, and code-splitting | Slower; full client bundle hydration before render |
| SEO | Full SSR/SSG; HTML is crawler-ready | CSR-only; needs extra pre-rendering to rank |
| Vercel Optimization | Native Image Optimization, Edge Functions, ISR, Middleware, PPR | Limited; manual CDN/config required for images/edge |
| Dynamic Data | Server Components + client streaming; DB/API friendly | Client-only fetch; higher latency and bandwidth |
| Complexity | Moderate (SSR/RSC patterns) | Low (CSR only) |
| Scalability | Edge + Serverless pooling, cache control | Needs separate backend stack for scale |

## Deployment Strategy (Vercel)
- **Framework Preset:** Next.js
- **Install command:** `npm ci`
- **Build command:** `npm run build`
- **Output directory:** `.next`
- **Environment:** set `NODE_ENV=production`, `DATABASE_URL`, `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_APP_ENV`
- **Observability:** add `@vercel/analytics` and `@vercel/speed-insights` in `app/layout.tsx` to track FCP/LCP and user-centric metrics.

## Operational KPIs & Traceability
- **Performance:** FCP/LCP <2s (Speed Insights), TTFB via Edge regions, cache hit rates.
- **Reliability:** Error rate <0.1% (Vercel Analytics + logs), ISR revalidation success, API latency p95.
- **Security & Compliance:** HSTS/Permissions-Policy headers, protected routes via Middleware, audit via git/Vercel deployments.
- **Collaboration:** Enforce PR checks (lint, typecheck, build), GitHub Actions, Vercel preview deployments per PR.

## Commands (local/CI)
```bash
# Install dependencies
npm ci

# Lint and type-check
npm run lint
npm run typecheck  # or: npx tsc --noEmit

# Build
npm run build

# Deploy preview / production
vercel
vercel --prod
```
