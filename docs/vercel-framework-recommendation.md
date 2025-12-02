# Vercel Framework Recommendation

## Context
- **Project type:** Other (cross-domain fintech analytics experiences)
- **Tech stack:** React, TypeScript, Tailwind CSS, Node.js, and supporting libraries
- **Primary goals:** SEO excellence, fast initial load, rapid iteration, and strong dynamic data support
- **Data strategy:** Mixed (static marketing + dynamic dashboards/APIs)
- **Team expertise:** Expert in Next.js and Server Components/SSR

## Recommendation
**Choose the Next.js (App Router) preset on Vercel.** It delivers the best mix of SEO, performance, and platform-native optimizations for mixed static/dynamic workloads and supports progressive rendering with Server Components, ISR, Edge Functions, and streaming for real-time analytics.

## Comparison: Next.js (App Router) vs Vite/SPA (React)
| Metric | Next.js (App Router) | Vite/SPA (React) |
| --- | --- | --- |
| Initial load (FCP/LCP) | Faster via SSR/SSG + partial prerendering; predictable sub-2s FCP targets with caching and image optimization | Slower first paint; full client bundle + hydration before content is interactive |
| SEO capability | Native SSR/SSG produces crawlable HTML; dynamic routes can leverage ISR for freshness | CSR requires prerendering plugins or server adaptor; higher risk of SEO gaps |
| Vercel platform fit | Built-in Image Optimization, Edge Middleware/Functions, ISR/PPR, automatic routing, and seamless Analytics/Speed Insights | Limited native optimizations; image handling and edge routing require custom setup |
| Dynamic data | Server Actions/RSC fetch close to data, reducing round-trips; streaming for dashboards | Client-only fetching; more latency and larger bundles |
| Complexity | Moderate (SSR, RSC, caching strategy) but aligned with team expertise | Lower concept count but loses platform-native performance features |
| Scalability | Horizontal scaling via Edge + smart caching; zero-config CDN for assets | Requires custom CDN rules and separate backend scaling story |

## Deployment Strategy for Next.js on Vercel
- **Framework preset:** Next.js (auto-detected)  
- **Install command:** `npm install` (or `npm ci` in CI)  
- **Build command:** `npm run build`  
- **Output directory:** `.next`
- **Key environment variables:**
  - `NODE_ENV=production`
  - `DATABASE_URL=<postgres_or_db_url>`
  - `NEXT_PUBLIC_API_URL=<public_api_endpoint>`
  - `NEXT_TELEMETRY_DISABLED=1` (optional for CI privacy)
- **Recommended middleware/auth routing:** Protect `/dashboard` and API routes with Edge Middleware for cookie-based auth, and set security headers (`Strict-Transport-Security`, `Content-Security-Policy`, `Referrer-Policy`, `Permissions-Policy`).
- **Monitoring and KPIs:** Enable `@vercel/analytics` and `@vercel/speed-insights` for FCP/LCP tracking; push metrics to dashboards with alerts on p95/p99 latency, cache hit rate, and build failure rates.

## Command Snippets (ready to paste)
```bash
# Local quality gates
npm run lint && npm run build

# Vercel CLI workflow
npm i -g vercel
vercel link
vercel  # preview
vercel --prod  # production

# Environment management
vercel env add DATABASE_URL production
vercel env add NEXT_PUBLIC_API_URL production
vercel env pull .env.local
```
