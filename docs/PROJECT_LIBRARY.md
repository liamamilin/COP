# Project library: adaptive browsing

The library is not designed around exactly two projects. Three independent axes
determine its presentation:

- **Available width:** CSS auto-fit/minmax selects the column count; a lone result
  has a readable maximum width. Compact phone cards shed extra vertical spacing.
- **Collection size:** Auto uses overview for up to four active projects, compact
  cards beyond that, and a list for archived projects. These are default-density
  heuristics, not fixed layouts. Filtering does not flip the selected view.
- **User choice:** View offers Auto, Overview, Compact and List regardless of count.
  The choice is session-local, not a persisted account setting.

Larger collections expose search, publication-status filtering and sorting by
recorded update time, creation time or title. Search examines stored title, scope,
domain and description across the supplied collection **before** paging. It does
not depend on the optional published-plan previews. Pages render at most 12 items;
changing a query/filter/sort resets the page. No matches is distinct from no projects.
Archived work has separate controls and remains collapsed by default.

Fetching stays in `apps/web/app/page.tsx`; `ProjectCollection` owns browsing state;
`lib/project-collection.ts` owns pure selection/paging; `ProjectActions` retains
explicit lifecycle confirmation. Browsing never writes project or learning data.
Existing optional version reads remain bounded to six published projects.

This is **client-side browsing pagination**, not server-side pagination: existing
project endpoints still return the collection. No claim is made about thousands
of records or backend latency. At that scale, add server query/sort/paging without
changing the view controls or conflating them with learning progress.

Verification: 122 frontend tests, typecheck and lint pass. The isolated collection
browser test covers 1/2/8/30/200 synthetic active projects across six widths, plus
50 archived projects, all views, filters, date sorting, paging and no-match states.
Lifecycle browser tests use mocked writes only. The real homepage regression
checks four widths and two color schemes, console/hydration errors, keyboard
navigation and unchanged project lists; it blocks non-GET/HEAD requests.
