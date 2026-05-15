---
id: auth-design
title: Auth design
type: decision
status: active
claims:
  - auth-uses-jwt
  - jwt-rs256-only
  - session-ttl-15min
  - refresh-tokens-rotate
entities:
  - auth-component
  - service-api
sources:
  - 3e2f1b8e7a4c9f5e0b2d6c1a4f8e9d3b7c5a2e1f0d8b6c4a3e2f1b8e7a4c9f5e
  - 9b1ac6d4f8e3b7a1c5e2d8f4a9b3c7e1d5f8a2c4b9e7d3f1a5c8b2e6d4f9a3c7
tags:
  - auth
created_at: 2026-04-12T09:30:00Z
updated_at: 2026-05-01T12:00:00Z
---

# Auth design

This page is the canonical write-up of how authentication works for
the service. It links to four atomic decision-claims; the claims are
the source of truth, the page is the narrative.

## Summary

Stateless, JWT-based. RS256 only. 15-minute access tokens with
rotating refresh tokens.

## Components

- `service-api` — issues, accepts, and refreshes tokens.
- `auth-component` — internal module owning verification.

## Decisions

- JWT in `Authorization` header — see [[auth-uses-jwt]].
- RS256-only verification — see [[jwt-rs256-only]].
- 15-minute access token TTL — see [[session-ttl-15min]].
- Refresh-token rotation with replay revocation — see
  [[refresh-tokens-rotate]].

## Why

We picked stateless JWTs because the service is horizontally scaled
and we didn't want session affinity. RS256 lets verifiers be
write-isolated from signers. The 15-minute TTL and rotation policy
together bound the blast radius of a leaked access token to a single
short window.

## Status

Active as of 2026-05-01. The team revisits this page each quarter or
when a significant change ships. Last touched 2026-05-01.
