# CarbonKit

CarbonKit is a proposed open platform for personal carbon understanding. This repository publishes the public project website, a proposed Working Standard v0.1, reference architecture, staged rollout, workshop paper review and call for volunteers. It does not implement a private tracking service or an API.

Research foundation: Laura Guzman, Stephen Makonin and Alex Clapp (2019), *CarbonKit: Designing A Personal Carbon Tracking Platform*, Fourth International Workshop on Social Sensing, Montreal. [DOI](https://doi.org/10.1145/3313294.3313385).

## Website

Buildless HTML, CSS and JavaScript. GitHub Pages serves `main` from `/`. All website links are relative so the site works at the project Pages URL and at `carbonkit.org`. The website collects no activity records, has no analytics scripts, and uses no third-party assets. GitHub's hosting policies apply.

Preview from this directory:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

## Working draft

- `standard.html`: proposed record model, methods, corrections, lifecycle and conformance criteria.
- `architecture.html`: proposed components, StreamingCalc candidate, rollout gates and volunteer roles.
- `paper-review.html`: evidence and limitations of the 2019 paper.
- `consumer-rights.html`: seven proposed consumer rights from Makonin, Guzman Flores, Gill, Clapp, Bartram and Gill (2014), with proposed CarbonKit applications. [Paper DOI](https://doi.org/10.1109/IHTC.2014.7147535).
- `downloads/carbonkit-working-draft-v0.1.pdf`: complete discussion draft, in embedded Times New Roman.
- `schemas/0.1/`: draft electricity activity and estimate record shapes.
- `examples/`: explicitly synthetic fixtures with an invented factor; never use it in a real inventory.
- `domain-setup.html`: maintainer checklist for GoDaddy DNS and GitHub HTTPS.

The schemas check shape, not full conformance. No endpoint, adapter, consent system, vault, certification, partner, funding or measured outcome is claimed. StreamingCalc currently supplies a Numbers workbook and is a candidate for a reviewed port or adapter.

## Check the draft

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python tools/check_draft.py
node --check assets/main.js
```

Checks cover local links/anchors, schema validity, fixture arithmetic and artifact digests, incompatible units, geography/time mismatch, missing versus zero and synthetic-factor exclusion from real inventories. They do not establish full system conformance.

## Rebuild documents

The generated HTML, schemas, examples and PDF share `tools/build_documents.py` as their content source. Install `requirements-authoring.txt` and run it from the repository. PDF authoring currently expects macOS Times New Roman fonts under `/System/Library/Fonts/Supplemental/`; it embeds them in the output. The HTML pages provide a more accessible reading alternative to the untagged PDF.

## Contribute

Review an issue or propose a focused change. Standards, carbon methods, software, accessibility, privacy and community contributions are welcome. Contact Stephen Makonin at [smakonin@sfu.ca](mailto:smakonin@sfu.ca) with an area of interest, possible first contribution and availability. No message is sent by the website.

Proposed review process: describe rationale, compatibility and method/privacy impacts; seek software and subject-matter review for affected areas. Maintainer appointments and decision rules remain open.

## License and sources

Draft documentation: Copyright © 2026 Stephen Makonin.

The repository's original **GNU Affero General Public License version 3** is preserved in `LICENSE`. No warranty. The 2019 ACM paper remains separately copyrighted; the website links its DOI rather than republishing it. StreamingCalc's MIT software notice and requested research citation must accompany any future port; its paper and reference documents retain their own terms.
