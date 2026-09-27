# Architecture reviews

Independent reviews of Hangar as a whole, written as the platform-approval decision a staff
architect would make. Each review is a standalone illustrated page: open it in a browser, or read
it on the site at [hangarplatform.dev/review](https://hangarplatform.dev/review/).

| Date | Review | Verdict |
|---|---|---|
| 2026-09-27 | [Hangar Architecture Review](2026-09-27-architecture-review.html) | **Conditional approval.** The architecture is approved and a pilot is funded; production use waits on five gates: prod independent of the dev cluster, a GitHub organization and SSO, authorization on Tower's write actions, a tested restore, and admission-time signature checks. |

**Convention:** a new review is a new dated HTML file in this folder and a new row above. Reviews are
point-in-time records, so an old one is never edited to match later changes; the next review says
what moved.
