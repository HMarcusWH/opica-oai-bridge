# Third-party source notice

This repository bootstraps an integration environment for:

- The OpenAI mathematics collection (`openai/math`), consumed through its
  existing fork `HMarcusWH/math`, pinned to an exact commit.
- Zeta23/OPICA (`HMarcusWH/zeta-23-lean`), pinned to the exact Round 4 source.

Both projects are read as separate Git checkouts, not copied or stripped of
notices. All imported modules retain their original copyright and license
notices. The bridge's generated Lake file is derived from the upstream OAI
Lake configuration and must retain upstream attribution on redistribution.

The bridge scaffolding is licensed under Apache License 2.0. Transitive
libraries may have distinct licenses; check each before redistribution.
