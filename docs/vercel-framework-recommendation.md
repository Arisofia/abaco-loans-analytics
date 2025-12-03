<<<<<<< HEAD
# Vercel Framework Preset Recommendation

## Context and roles
- **Audience:** Engineering, DevOps, and product stakeholders shipping fintech analytics experiences.
- **Objective:** Deploy performant, SEO-ready, and data-rich experiences with strong observability and compliance on Vercel.

## Recommendation
- **Framework Preset:** **Next.js (App Router, v14+)**
- **Why:**
  - Native SSR/SSG/ISR for best FCP/LCP and crawlable HTML.
  - Edge Middleware and Edge Functions for global low-latency auth/routing.
  - Server Components and streaming for KPI dashboards with progressive rendering.
  - First-class Vercel optimizations (Images, Caching, Analytics, Speed Insights) with minimal config.

## Comparative analysis (Next.js vs Vite/SPA)
| Dimension | Next.js (App Router) | Vite/SPA (React) |
| --- | --- | --- |
| Initial Load (FCP/LCP) | Faster via SSR/SSG/ISR + route-level code splitting; streaming reduces time-to-data. | Slower: full client hydration before meaningful paint; larger initial bundle. |
| SEO | Strong: HTML rendered on the server; metadata API; ISR for freshness. | Weak by default: CSR requires extra pre-rendering; bots see minimal HTML. |
| Vercel Optimization | Built-in Image Optimization, Edge Middleware, Edge/Node runtimes, ISR, cache tags. | Limited: image/CDN tuning must be manual; no native ISR; edge requires custom setup. |
| Data Handling | Server Components fetch securely; incremental revalidation for KPIs; API Routes for server-side joins. | Client-only data fetch; more API roundtrips; harder to protect secrets. |
| Complexity | Moderate: SSR/RSC patterns; clear conventions for layouts/routes. | Lower: familiar SPA patterns but more infra wiring for SEO/perf. |
| Scalability | Horizontal and edge-native by default; good cold-start profile with Vercel functions. | Depends on separate backend; SPA alone does not scale server logic. |

## Deployment strategy (Vercel)
- **Framework Preset:** Next.js
- **Build command:** `npm run build` (or `pnpm run build` / `yarn build`)
- **Install command:** `npm ci` for deterministic builds.
- **Output directory:** `.next`
- **Environment configuration:**
  - `NODE_ENV=production`
  - `NEXT_PUBLIC_API_URL=https://api.example.com`
  - `DATABASE_URL=<postgres_url>` (server-side only)
  - `NEXT_RUNTIME=edge` per route when low latency matters.
- **Routing and middleware:** Use `middleware.ts` for auth, geo routing, or A/B tests; prefer Edge runtime for latency-sensitive checks.
- **Data freshness:** Prefer ISR with route-specific revalidation or cache tags for KPI pages; fall back to SSR for highly dynamic views.
- **Observability:** Enable `@vercel/analytics` and `@vercel/speed-insights` in `app/layout.tsx`; set up dashboards for FCP, LCP, TTFB, error rate, and cache hit ratio.
- **Security and compliance:** Enforce HTTPS (HSTS), `Strict-Transport-Security`, `Content-Security-Policy` tuned to allowed sources, and `Referrer-Policy: strict-origin-when-cross-origin`.
- **Team workflow:**
  - Branch-based previews for every PR.
  - Protect `main` with required checks: lint, type-check, unit tests.
  - Use GitHub Actions to run `npm ci`, `npm run lint`, `npm run test`, and `npm run build` per push.

## Copy-paste command deck
```bash
# Local verification
npm ci
npm run lint
npm run test
npm run build

# Deploy with Vercel CLI
npm i -g vercel
vercel link
vercel  # preview
vercel --prod

# Manage env vars
vercel env add DATABASE_URL production
vercel env add NEXT_PUBLIC_API_URL production
vercel env pull .env.local
```

## KPIs and dashboards
- **Performance:** FCP, LCP, TTFB, CLS, cache hit ratio, edge vs origin latency.
- **Reliability:** Error rate by route/function, build success rate, ISR revalidate success.
- **Growth/SEO:** Index coverage, crawl errors, organic CTR, structured data validity.
- **Product:** Funnel conversion on marketing pages, dashboard time-to-first-chart, API latency percentiles.

## Continuous improvement
- Review analytics weekly; tune caching and ISR windows per page.
- Add synthetic checks for key journeys (login → dashboard → export KPI report).
- Rotate secrets regularly; enable audit logs on Vercel and connected stores.
=======
# Vercel Framework Recommendation for New Deployments

## Summary Recommendation
- **Framework Preset:** Next.js (App Router, Next.js 14+)
- **Why:** Native Vercel optimizations (ISR, Image Optimization, Edge Functions, Middleware), strong SEO/SSR, streaming Server Components for mixed static/dynamic data, and first-class TypeScript support. Ideal for fintech analytics that demands compliance, observability, and rapid iteration.
- **Team Fit:** Assumes proficiency with Next.js/SSR; supports mixed data strategies and enterprise governance (security headers, env management, auditable CI).

## Comparative Analysis (Next.js vs Vite/SPA)
| Dimension | Next.js (App Router) | Vite/SPA (React) |
| --- | --- | --- |
| Initial Load (FCP/LCP) | Faster: SSR/SSG + code-splitting; PPR/ISR reduce TTFB and payload | Slower: full client bundle + hydration gate; relies on aggressive caching | 
| SEO Coverage | Strong: HTML pre-rendered; Metadata API; dynamic routes with ISR | Weak: CSR-first; needs pre-render hacks; bots may miss dynamic content | 
| Vercel Optimization | Native: Image Optimization, Edge Functions/Middleware, ISR cache, Analytics/Speed Insights | Limited: requires manual CDN/image setup; fewer edge primitives | 
| Real-time/Data | Server Components stream data; Route Handlers/APIs colocated; Edge auth | Client-only fetching; backend hosted elsewhere; higher latency | 
| Complexity | Moderate: SSR/RSC patterns, caching strategies, middleware | Low: familiar SPA patterns only | 
| Scalability | Auto-edge scaling; DB pooling with Route Handlers; multi-region cache | Frontend only; must build/operate separate backend | 
| Compliance/Observability | Built-in headers, Middleware for auth/A/B testing; Vercel Analytics + Speed Insights; supports logging and tracing | Mostly client-centric; requires extra services for telemetry/compliance | 

## Deployment Strategy on Vercel (Next.js Preset)
1. **Project Settings → General**
   - Root Directory: `apps/web` (for monorepo)
   - Framework Preset: **Next.js**
2. **Build & Install Commands**
   - Install: `npm install` (workspace-aware) or `npm ci`
   - Build: `npm run build` (executes from `apps/web` when Root Directory is set)
   - Dev: `npm run dev`
   - Output Directory: `.next`
3. **Environment & Secrets** (Vercel Dashboard → Environment Variables)
   - `NODE_ENV=production`
   - `DATABASE_URL=<postgres-url>`
   - `NEXT_PUBLIC_API_URL=<public-api>`
   - `NEXT_RUNTIME=experimental-edge` (for edge-first routes, optional)
4. **Recommended next.config.ts settings**
   - Enable `reactStrictMode`, `swcMinify`, and AVIF/WebP images
   - Configure `experimental.serverActions` and `experimental.ppr` for streaming/partial prerendering where safe
   - Harden headers (HSTS, XSS, Referrer-Policy), and prefer Edge Middleware for auth/geo-based rules
5. **CI/CD & Quality Gates**
   - Pre-deploy checks: `npm run lint`, `npm run test` (if defined), `npm run build`
   - Observability: add `@vercel/analytics` and `@vercel/speed-insights` in `app/layout.tsx`
   - Auditing: lockfile in repo; enable branch protection + required checks; use Vercel deployments with GitHub Checks for traceability
6. **Performance & KPI Tracking**
   - Target <2s FCP and <2.5s LCP for landing pages; monitor via Vercel Speed Insights
   - Track cache HIT ratio for ISR/Edge cache; alert on miss spikes
   - Dashboard: surface build duration, error rate, p95 latency, and bundle size per deployment

## Command Snippets (copy/paste)
- **Local build (monorepo aware):**
  ```bash
  cd apps/web && npm run build
  ```
- **Preview deploy via Vercel CLI:**
  ```bash
  vercel --cwd apps/web
  ```
- **Production deploy:**
  ```bash
  vercel --prod --cwd apps/web
  ```
- **Pull envs locally:**
  ```bash
  vercel env pull apps/web/.env.local
  ```

## Why Not Vite/SPA for This Use Case
- Lacks native SSR/ISR, so SEO and initial render speed depend on client hydration.
- Requires separate backend + CDN configuration for images/edge caching, increasing operational surface area.
- Observability, auth, and compliance controls must be stitched together manually rather than leveraging Vercel middleware/Edge Functions.

## Roles & Responsibilities (RACI-style)
- **Product/Analytics:** define KPIs (FCP, LCP, conversion, DAU), instrumentation events, and dashboards.
- **Engineering:** implement Next.js App Router, caching strategy (ISR/PPR), middleware for auth/compliance, and CI gates.
- **DevOps/SRE:** manage Vercel project settings, environment secrets, incident playbooks, and release governance.
- **Security/Compliance:** review headers, data residency, logging/PII handling, and audit trails.

## Continuous Improvement
- Run quarterly performance audits (Lighthouse/Speed Insights); regressions >10% trigger remediation.
- Rotate secrets regularly and enforce least-privilege for Vercel/GitHub tokens.
- Keep Next.js and Vercel CLI updated to inherit platform optimizations and security patches.
>>>>>>> origin/main
