# AI EA: Institutional Trading Platform

## Architecture
- **L1 Feature Factory**: Modular plugin-based indicator engine.
- **L2 Regime Engine**: Market state classification.
- **L3 Signal Engine**: Multi-model Ensemble (XGB, LGBM, RF).
- **L4 Risk Manager**: Kelly-based dynamic position sizing.
- **L5 Execution Bridge**: Decoupled MT5/Broker interface.

## Milestone 1 Complete: Infrastructure
- Decoupled Broker Logic
- Event-Driven Orchestration
- SQLite SSOT Schema
- Unit Test Suite for Core Modules