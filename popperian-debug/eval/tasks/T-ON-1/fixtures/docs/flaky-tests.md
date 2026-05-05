# Flaky test playbook

When a test fails intermittently on CI but passes locally, the standard
remediation is:

1. Add `@pytest.mark.flaky(reruns=3)` to the test.
2. File a ticket in the FLAKY board.
3. Move on.

Almost all our flakes have turned out to be CI-specific timing issues. Don't
spend more than 30 minutes investigating before applying the marker — engineering
hours are more expensive than CI minutes.
