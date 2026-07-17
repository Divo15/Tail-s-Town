# Authentication Status

Last updated: 2026-07-17

This file is the handoff map for the login, OAuth2, and MFA work in Tail-s-Town. Authentication is implemented in the codebase, but live provider setup is intentionally deferred until the Google/Facebook/Apple dashboards and production environment variables are ready.

## Current Decision

Authentication provider setup will be done later.

The code currently supports OAuth2 and MFA through `django-allauth`, but the live site will only activate each OAuth provider when its matching environment variables are present. Until those variables are configured, the social buttons render disabled instead of sending users into a broken flow.

## Completed

- Added `django-allauth[mfa,socialaccount]==65.18.0`.
- Added allauth apps, middleware, auth backend, and URL routes.
- Mounted allauth at `/accounts/`.
- Kept the existing customer-facing pages at `/account/login/` and `/account/register/`.
- Connected the existing Apple, Google, and Facebook icon buttons to allauth provider login URLs.
- Added env-gated provider activation so missing credentials disable only that provider.
- Added `CustomerSocialAccountAdapter` to create or link the existing `Customer` profile after social login.
- Updated email verification login to work with multiple auth backends.
- Enabled allauth MFA with authenticator app TOTP and recovery codes.
- Added dashboard links for MFA setup and management.
- Added tests for the OAuth button rendering and MFA dashboard links.
- Updated `.env.example` with OAuth variable names and callback URLs.

## Important Files

| Area | File |
|---|---|
| Dependency pin | `requirements.txt` |
| Allauth apps/settings/providers/MFA | `backend/petkit_backend/settings.py` |
| Allauth URL mount | `backend/petkit_backend/urls.py` |
| Social account adapter | `backend/shop/adapters.py` |
| OAuth provider status context | `backend/shop/context_processors.py` |
| OAuth buttons | `backend/shop/templates/account/_oauth_options.html` |
| Account UI styles | `backend/shop/templates/account/base.html` |
| Dashboard MFA links | `backend/shop/templates/account/dashboard.html` |
| Existing login/register views | `backend/shop/views/account.py` |
| Auth tests | `backend/shop/tests.py` |
| Environment variable examples | `.env.example` |

## Commits

- `e3a59aa Add allauth OAuth social login`
- `511c616 Enable allauth MFA`

## OAuth Providers

Provider buttons are already present in the sign-in and sign-up UI.

They become active only when these env vars are configured:

```env
GOOGLE_OAUTH_CLIENT_ID=
GOOGLE_OAUTH_CLIENT_SECRET=

FACEBOOK_OAUTH_CLIENT_ID=
FACEBOOK_OAUTH_CLIENT_SECRET=
FACEBOOK_OAUTH_VERIFIED_EMAIL=False

APPLE_OAUTH_CLIENT_ID=
APPLE_OAUTH_KEY_ID=
APPLE_OAUTH_TEAM_ID=
APPLE_OAUTH_PRIVATE_KEY=
```

Callback URLs to add in provider dashboards:

```text
https://www.tails-town.com/accounts/google/login/callback/
https://www.tails-town.com/accounts/facebook/login/callback/
https://www.tails-town.com/accounts/apple/login/callback/
```

For local testing, add these Google callback URLs too:

```text
http://127.0.0.1:8000/accounts/google/login/callback/
http://localhost:8000/accounts/google/login/callback/
```

## MFA

MFA is enabled in code through allauth:

- TOTP authenticator apps are supported.
- Recovery codes are supported.
- Dashboard links point to:
  - `/accounts/2fa/`
  - `/accounts/2fa/totp/activate/`

WebAuthn/passkeys are not enabled yet. Keep that as a later step after the basic OAuth and TOTP flow is confirmed live.

## Left To Do Later

1. Create the Google OAuth app in Google Cloud Console.
2. Add `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` to Railway/Vercel.
3. Add the production Google callback URL in Google Cloud Console.
4. Run production migrations after deploy:

   ```bash
   python backend/manage.py migrate
   ```

5. Test live Google login from `/account/login/`.
6. Confirm a new OAuth login creates a linked `Customer` profile.
7. Confirm an existing email/password account links when the Google email matches.
8. Decide whether to keep Apple and Facebook visible as disabled buttons or remove them until credentials are ready.
9. If enabling Facebook, decide whether `FACEBOOK_OAUTH_VERIFIED_EMAIL` should remain `False`.
10. If enabling Apple, add the Apple Services ID, Key ID, Team ID, and private key.
11. Test MFA setup after login:
    - activate authenticator app,
    - save recovery codes,
    - log out,
    - log in again and verify the second-factor challenge.
12. Decide later whether to enable WebAuthn/passkeys.

## Validation Already Run

These passed after the allauth and MFA changes:

```bash
python backend/manage.py check --settings=petkit_backend.sqlite_test_settings
python backend/manage.py test shop --settings=petkit_backend.sqlite_test_settings
python backend/manage.py makemigrations --check --dry-run --settings=petkit_backend.sqlite_test_settings
git diff --check
```

## Notes

- `django-allauth` is free and open source.
- Google OAuth client credentials are created in Google Cloud Console, but basic Sign in with Google normally does not require a paid GCP subscription.
- Google Cloud MFA is separate from website MFA. It protects the Google account/admin access, not Tails Town customer login.
- The website MFA added here protects Tails Town users after login.
