# Clerk API Keys

## Backend Keys (Already in backend/.env)

- **Secret Key**: `sk_test_aC7xdnf8HZLpi6erMxMFQdT1RUbX7m7c92tKTTVLhE`

## Frontend Keys (For Next.js - Use Later)

- **Publishable Key**: `pk_test_ZXhvdGljLW1pbmstNTAuY2xlcmsuYWNjb3VudHMuZGV2JA`

## Notes

- The publishable key is safe to expose in frontend code (it's public)
- The secret key must NEVER be exposed to the frontend
- When we build the Next.js frontend, we'll add the publishable key to `frontend/.env.local`
