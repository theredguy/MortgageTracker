# Mortgage Tracker

A custom Home Assistant integration to track mortgages with interactive Lovelace card.

## Installation

Install via HACS under **Integrations**.

### Lovelace Card

Add the following resources:

```yaml
resources:
  - url: /hacsfiles/mortgage-tracker/mortgage-card.js
    type: module
