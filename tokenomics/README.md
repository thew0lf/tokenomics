# Tokenomics Core

The core package is intentionally small. It contains the domain model used to represent token-loss observations and the boundary between detection and measurement.

## Design rule

Raw AI conversations are not ledger records. A ledger record contains only the metadata required to explain and measure a potential loss.

A `LossEvent` records:

- loss category
- estimated avoidable tokens
- explanation
- detector confidence
- source
- recommendation outcome
- measured tokens saved after testing

This lets Tokenomics answer the important question later:

> Did the recommendation actually save tokens?
