# Holdout & Out-of-Sample Register

To prevent data snooping and curve-fitting, market data is partitioned into strict temporal segments:

| Data Segment | Date Boundary | Purpose | Status |
| :--- | :--- | :--- | :---: |
| **Development (In-Sample)** | `2024-01-01 to 2024-12-31` | Parameter search, rule formulation | `CONSUMED` |
| **Walk-Forward Validation** | `2025-01-01 to 2025-12-31` | Out-of-sample parameter stability testing | `RESERVED / ACTIVE` |
| **Final Untouched Holdout** | `2026-01-01 to Present` | Final verification before live/funded deployment | `UNTOUCHED / FROZEN` |

---
*Rule*: No candidate may alter parameters based on performance observed in the Final Untouched Holdout period.
