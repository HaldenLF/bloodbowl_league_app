# Security

This project is in active development and has not been deployed. This page records how it is
designed to stay secure, what is known to be missing, and what must be done before it runs on a
public server.

## Reporting a vulnerability

Please do not open a public issue. Use GitHub's **Report a vulnerability** button on the
repository's Security tab, which sends a private report to the maintainer.

## How the API is protected

### Accounts and login
- Passwords are hashed with **Argon2id** (pwdlib defaults: 64 MB memory, 3 iterations). Plain
  passwords and hashes are never returned, logged or printed.
- Passwords must be 8 to 128 characters. The upper limit stops oversized inputs from being used to
  make hashing expensive.
- Login returns the same `401` for an unknown email and a wrong password, and both take the same
  time: a dummy hash is verified when the email doesn't exist.
- Disabled accounts are rejected on every request, not only at login.
- Public signup can create **coach** or **commissioner** accounts only. The super admin is created
  once by the host with `python -m scripts.create_super_admin`, which never stores the password in
  a file or shell history.

### Tokens
- Access tokens are JWTs signed with HS256 and a secret of at least 32 characters, loaded from
  `.env` and never committed. The app refuses to start with a missing or short secret.
- Only HS256 is accepted when decoding, and `sub`, `exp` and `iat` are required, so unsigned or
  non-expiring tokens are rejected.
- Tokens last 24 hours (`ACCESS_TOKEN_MINUTES`). The user is re-read from the database on every
  request, so disabling an account takes effect immediately.

### Who can see and change what
- Every endpoint that takes an id checks the caller's relationship to that object, not just that
  they are logged in. The rules live in one file, `backend/app/core/permissions.py`.
- **Outsiders get `404`** for leagues, seasons, teams and players they can't see. The response is
  identical to the one for an id that doesn't exist, so ids can't be probed.
- **Members who lack the right get `403`.** Members can read their league. Only a team's coach or
  the league's commissioner can change a roster. Only the commissioner manages join codes, join
  requests, seasons and treasuries.
- A commissioner administers only the leagues they own.
- **No silent super-admin bypass.** On normal routes the super admin is an ordinary user. Their
  extra powers are planned for a separate `/admin` console in which every change is audited.
- Other users appear only as `id` and `display_name`. Email addresses are shown only to their
  owner.
- League join codes act as passwords. They are shown only to the league's commissioner, can be
  regenerated (the old code stops working), and are generated with Python's `secrets` module.
- Clients can never set money or stats. Teams start with the season's starting treasury. Hiring
  cost comes from the database. Request schemas are explicit allowlists, so unknown fields are
  ignored.
- Hiring locks the team row (`SELECT ... FOR UPDATE`), so simultaneous requests can't overspend
  the treasury or duplicate a jersey number.

### Abuse limits
- Rate limits per client IP: login 5 per minute, register 10 per hour, join by code 10 per minute,
  league search 30 per minute. Over the limit, the API answers `429`.
- League search escapes `%` and `_`, never shows invite-only leagues, and returns at most 20
  results.
- Lists that can grow are paginated, with at most 100 items per request.

### Production mode (`ENVIRONMENT=production`)
- `/docs`, `/redoc` and `/openapi.json` are switched off.
- CORS allows only the origins listed in `CORS_ORIGINS`. The app refuses to start if `*` is listed.
- Every response carries `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY` and
  `Referrer-Policy: no-referrer`. In production, `Strict-Transport-Security` and a
  `Content-Security-Policy` of `default-src 'none'` are added.

### Dependencies and tests
- Every dependency version is pinned. `pip-audit -r backend/requirements.txt` must be clean before
  deploying. New releases are adopted once they are at least two weeks old.
- The pytest suite runs against a separate `_test` database and covers the permission rules above:
  who gets `401`, `403` and `404` for each kind of request.

## Known limitations

- **Email addresses can be discovered**: registering an address that is already taken returns
  `409`. Planned fix: email verification.
- **Tokens can't be revoked one at a time.** There is no logout or refresh token yet. A stolen
  token works for up to 24 hours unless the account is disabled.
- **Rate limits are per IP and kept in memory.** They reset on restart, aren't shared between
  worker processes, and don't stop a slow attack spread over many IPs against one account.
- **The `/admin` console and its audit log are not built yet**, and commissioner treasury changes
  are not yet audited.
- **The development setup is for development only.** `docker-compose.yml` contains a dev database
  password, and the app connects as the database superuser. Postgres is bound to `127.0.0.1`.

## Before deploying

- [ ] `ENVIRONMENT=production` and `CORS_ORIGINS` set to the real frontend origin(s).
- [ ] A new `JWT_SECRET`, used only in production
      (`python -c "import secrets; print(secrets.token_urlsafe(48))"`).
- [ ] A strong database password kept in the host's secret settings, never in the repo.
- [ ] The database is not reachable from the internet.
- [ ] The app connects with a least-privilege database role; migrations use a separate role.
- [ ] HTTPS terminated by the host. Uvicorn runs with `--proxy-headers` and
      `--forwarded-allow-ips` set to the proxy, so rate limits see real client IPs.
- [ ] More than one worker process means rate limits use a shared store (Redis).
- [ ] No `--reload` in production.
- [ ] `pip-audit -r backend/requirements.txt` is clean and `pytest` passes.
- [ ] `alembic upgrade head` run, then `python -m scripts.create_super_admin` once.
- [ ] Database backups configured.
