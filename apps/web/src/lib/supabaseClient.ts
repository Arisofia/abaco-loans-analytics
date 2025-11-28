import { createClient, type SupabaseClient } from '@supabase/supabase-js'
import type { LandingPageData } from '../types/landingPage'

type Database = {
  public: {
    Tables: {
      landing_page_data: {
        Row: LandingPageData
      }
    }
  }
}

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Supabase environment variables are missing')
}

// The SDK is correctly typed, but eslint cannot infer the env guard in this setup.
// eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-assignment
export const supabase: SupabaseClient<Database> = createClient<Database>(
  supabaseUrl,
  supabaseAnonKey
)
