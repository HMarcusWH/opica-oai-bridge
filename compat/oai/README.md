# OpenAI configuration overlays

Upstream OAI source is pinned in `source-lock.json`. Its original `lean/lakefile.lean`
is used to generate this workspace's Lake configuration. The generator changes
only the root package name, the OAI default target, and adds two library targets.
The upstream dependency patch commands and `patches/` directory remain intact.

Do not add a source edit here merely to satisfy a theorem: changes must first
be independently reviewed and recorded with exact patch hashes.
