# Supabase Connection Pooling Guidance

This project should use Supabase's connection pooler (PgBouncer) rather than direct database connections, especially when deploying to serverless platforms such as Vercel. Direct connections from serverless functions open many short-lived Postgres sessions and can quickly exhaust the database's connection limit.

## Why use the connection pooler
- The pooler reuses a small set of Postgres connections and hands them out to individual requests, preventing connection storms in serverless environments.
- Supabase's pooler works over IPv4-only networks and is the recommended production configuration for Vercel deployments.

## Steps to configure
1. **Retrieve the database password** from your Supabase project's **Settings → Database → Connection info** page. Reset it if you do not have the value.
2. **Copy the pooler connection string** from **Connection strings → Connection pooling**. It follows the pattern:
   ```
   postgresql://postgres.<project-ref>:<PASSWORD>@aws-0-us-east-1.pooler.supabase.com:5432/postgres
   ```
3. **Store the URI in an environment file** (never hardcode secrets):
   - Create a `.env.local` file at the project root.
   - Add `DATABASE_URL="postgresql://postgres.<project-ref>:<PASSWORD>@aws-0-us-east-1.pooler.supabase.com:5432/postgres"`.
4. **Point your ORM or database client to the environment variable.** For example, Prisma's datasource block should use `url = env("DATABASE_URL")`.
5. **Set the `DATABASE_URL` environment variable in Vercel** (Settings → Environment Variables) for Production, and optionally Preview/Development, using the same pooler URI.

## Git hygiene
Ensure `.gitignore` excludes local env files so secrets are not committed. Add `.env*.local` to the ignore list if it is not already present.
