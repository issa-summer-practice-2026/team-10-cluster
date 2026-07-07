# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project aims to
follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> During the week, your release automation will generate release notes from your
> merged pull requests. Keep this file as the human-readable history.

## [Unreleased]

## [0.1.0] - 2026-07-05
### Added
- Initial `instrument-cluster` starter.
- Frontend: React + TypeScript (Vite) — SVG tachometer (with redline) and
  speedometer, digital speed/gear readout, fuel/temperature gauges, telltale
  lamp row, startup needle-sweep, and a simulator panel with a "Play drive".
- Backend: Flask JSON API serving the built frontend; deterministic, pytest-
  tested cluster logic in Python; in-memory vehicle state; bundled drive cycle;
  `/health` and `/version` endpoints.
- Cross-platform dev scripts (`scripts/dev.py` + `Makefile`).
