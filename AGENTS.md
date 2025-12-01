# AGENTS

- For changes to the web app under `apps/web`, install dependencies with `npm ci` and run `npm run check-all` from that directory (runs type-check, lint, and formatting checks). At minimum, `npm run lint` must pass before submitting changes.
- Keep generated build artifacts out of the repo; cache folders such as `.gradle/` and any `build/` directories from Gradle modules should stay ignored along with `.next/` output from the Next.js app.
