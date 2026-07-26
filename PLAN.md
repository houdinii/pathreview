## Solution plan

**Issue:** Add integration tests for authentication edge cases — https://github.com/ascherj/pathreview/issues/90

### Understand

The root cause is a **test-coverage gap, not a code bug**: no test in the repository exercises
`get_current_user` (`api/middleware/auth.py`). A `grep` for the middleware across `tests/` exits
`1` (zero hits) and `tests/integration/` contains only `__init__.py`, so the middleware is only
ever exercised implicitly through the happy path.

- **Expected:** each way of presenting a bad credential to a protected route returns `401`, and
  that behavior is pinned by an automated test that fails if the middleware ever stops rejecting it.
- **Actual:** the four rejection paths (missing header, malformed token, expired token, wrong-secret
  token) have no coverage, so a regression that let unauthorized requests through would pass silently.

I confirmed today's behavior by probing `GET /reviews` (a route guarded by `get_current_user`):
a missing header returns `401 "Not authenticated"`; malformed, expired, and wrong-secret tokens all
return `401 "Invalid authentication credentials"`. A successful fix is those behaviors captured as
integration tests, plus the first integration-test pattern for this repo.

### Map

This issue (manifest **E-15**) is scoped to a single new file. Files involved:

- `tests/integration/test_auth_middleware.py` — **the only file changed.** Holds a module-level
  `client` fixture (`TestClient(app)`) and the four rejection tests grouped in
  `TestAuthMiddlewareRejections`. Kept self-contained (no `conftest.py` change) because the issue
  scopes to one file and the rejection paths need no shared fixtures.
- Read-only references (not edited):
  - `api/middleware/auth.py` — `get_current_user`; the four 401 branches under test.
  - `core/security.py` — `create_access_token` / `decode_access_token`; used to forge the test JWTs.
  - `api/routes/reviews.py` — `GET /reviews`, the protected route the tests hit.
  - `api/main.py` — the `app` object the `TestClient` wraps.

### Plan

1. Add a module-level `client` fixture returning `TestClient(app)`. No `get_db` override is needed —
   the four rejection paths raise before the DB lookup at `auth.py:58`.
2. **Missing header** → request `GET /reviews` with no `Authorization` header; assert `401` and
   `detail == "Not authenticated"`. Parametrize the "absent credential" variants: wrong scheme
   (`Basic ...`) and an empty `Bearer` token.
3. **Malformed token** → send junk bearer tokens (non-JWT string, wrong segment count, undecodable
   base64) via `@pytest.mark.parametrize`; assert `401` and `detail == "Invalid authentication
   credentials"`.
4. **Expired token** → forge one with `create_access_token(..., expires_delta=timedelta(minutes=-5))`;
   assert `401` and, specifically, `detail == "Invalid authentication credentials"` — pinning the
   generic message, not `"Token has expired"`.
5. **Wrong-secret token** → sign a structurally valid JWT with a different secret (and an
   algorithm-confusion variant, e.g. `alg=none`/`HS512`); assert `401`.
6. Run scoped checks green on the new file only: `ruff check`, `black`, `mypy`, and
   `pytest tests/integration/test_auth_middleware.py`.

### Inputs & outputs

- **Inputs:** crafted JWTs and raw header strings. Valid-but-bad tokens are built with
  `core.security.create_access_token` (expired case) and `jose.jwt.encode` with a foreign secret
  (wrong-secret case); malformed and missing-header cases are plain strings. All are delivered as the
  `Authorization` header on `GET /reviews` through a `TestClient`.
- **Outputs:** `httpx.Response` objects. Tests assert on `response.status_code` (always `401`) and
  `response.json()["detail"]` (the exact message per case). **No production code changes** — this is
  test-only; no function signature or runtime behavior is modified.

### Risks & unknowns

- **No `client`/app fixture exists yet** (`tests/conftest.py` has none). I'm establishing the
  pattern; I keep it self-contained in the one test file so I don't touch shared infrastructure that
  a reviewer might scope to another ticket.
- **The `"Token has expired"` branch (`auth.py:44–49`) is unreachable dead code.** `decode_access_token`
  (`core/security.py:78–86`) catches every `JWTError` — including `ExpiredSignatureError` — and returns
  `None`, so `auth.py:35` fires first and expired tokens get the generic 401. My test must assert the
  real behavior, not the intended-but-dead message.
- **Interaction with issue E-04** ("Authentication middleware doesn't validate token expiry"). That
  separate issue may make the expiry branch reachable and change the expired-token message to
  `"Token has expired"`. If E-04 lands first, my expired-token assertion must be updated. I note this
  explicitly rather than couple the two tickets.
- **Fixture ownership (issue G-01).** A shared sample-user fixture is missing from `tests/fixtures/`
  and is G-01's deliverable. Happy-path and user-not-found tests would depend on it, so I deliberately
  keep those out of scope to avoid stepping on another ticket.
- **Open question:** does `TestClient(app)` need `app.dependency_overrides[get_db]` for these four?
  Reading `auth.py`, the 401s all raise before line 58, so no — but I will confirm during
  implementation that no path reaches the DB session.

### Edge cases

At least two concrete input/state scenarios the tests must handle, all inside the four scenarios (no
scope expansion):

1. **Missing header vs. present-but-wrong scheme.** A truly absent `Authorization` header and an
   `Authorization: Basic ...` header both yield `401 "Not authenticated"` from `OAuth2PasswordBearer`,
   a *different* path and message than the token cases — the tests assert the correct message per path.
2. **`Bearer` with an empty token.** `Authorization: Bearer ` (no token) must still be rejected, not
   treated as anonymous-but-allowed.
3. **Structurally malformed vs. cryptographically invalid.** `not.a.jwt` (bad structure) and a
   correctly-structured token signed with the wrong secret are different failure modes that must both
   return `401 "Invalid authentication credentials"`.
4. **Algorithm confusion.** A token presented with `alg=none` (or a non-whitelisted algorithm) must be
   rejected by the `algorithms=[HS256]` whitelist in `decode_access_token`, not silently accepted.
5. **Expired token returns the generic message**, `"Invalid authentication credentials"` — asserting
   this exact string is what proves the dead-code expiry branch and guards the E-04 boundary.
