## Week 7 — Issue selection

**Issue link:** https://github.com/ascherj/pathreview/issues/90
**Issue title:** Add integration tests for authentication edge cases
**Tier:** [ ] Tier 1 [x] Tier 2 [ ] Tier 3

**Problem summary:**
There are currently no integration tests whatsoever for the authentication middleware. The issue identifies four specific gaps: expired tokens, malformed tokens, a missing Authorization header, and tokens signed with a different secret. This matters because right now we have no way to know whether an authentication bug is allowing unauthorized access to protected routes — the middleware is only exercised with a valid token, so any regression in the rejection paths would pass unnoticed. A successful fix means each of those four cases is covered by an automated test that fails if the middleware ever stops rejecting them. Because there are no integration tests in the repository yet, this also establishes the pattern that future integration tests will follow.

**Selection notes:**
I selected this issue because I want to focus on the contribution process as much as the implementation. I'm a professional developer and the code itself is familiar territory, but my commit and merge practices have always been low-key and built on worn-out habits, so getting the contribution side right matters more to me here than picking the hardest available problem. I could potentially contribute at a higher tier, but given time constraints I felt it prudent to prioritize the ability to finish within the timeframe above everything else.

I ultimately decided on Tier 2 to balance the time commitment against doing meaningful work. I rejected #102, a Tier 3 frontend issue estimated at 7–10 hours, even though I would have found it more interesting, in favor of this one at 3–5 hours, both lower risk and smaller scope. Test work also degrades gracefully: if my available hours evaporate, four solid tests is still a complete, mergeable PR, whereas a half-finished feature would be nothing. If I get through this cleanly and come out knowing the codebase better, I can take on a higher tier for a second issue.

I did notice that there are no integration tests whatsoever and conftest.py has no client fixture, so I'll be establishing a pattern rather than following one. That is a front-loaded risk I'm accepting knowingly rather than discovering later. I've worked through the "Is this issue right for me?" checklist and this fits.

**Branch name:** test/90-auth-middleware-edge-cases
**Setup confirmation:** [x] App runs locally at localhost:5173
**Cohort ledger:** [x] Issue added to cohort ledger