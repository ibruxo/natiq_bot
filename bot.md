# Project Charter - Bot

**Last Updated**: [Date]
**Version**: 1.0.0
**Status**: In Progress

---

## 1. Project Identification

| Field                  | Value                               |
| ---------------------- | ----------------------------------- |
| **Project Name**       | Bot                                 |
| **Project Repo**       | bot                                 |
| **Project Manager**    | [ibruxo](https://github.com/ibruxo) |
| **Development Team**   | Backend                             |
| **Start Date**         | 2026-04-07                          |
| **Estimated End Date** |                                     |

---

## 2. Vision and Goals

### Vision

A Telegram bot that engages users with daily Quranic content and other Islamic topics.

### High-Level Goals

- Deliver a daily Quranic verse or page to users & channels and groups (scheduled posting).
- Offer an “Open in Natiq” button that deep‑links to the companion app.
- Support multiple languages via environment configuration.
- (Future) Extend the same bot logic to other social media platforms.

---

## 3. Project Scope

### In-Scope

- Core bot logic built against the Telegram Bot API, which can also be deployed on any other platform that implements the same API.
- All Telegram-specific features must be wrapped in automatic runtime capability checks. If a platform does not support a particular API endpoint, the associated UI elements and logic will be automatically disabled without breaking the core experience.
- Quran section:
  - Daily 1 Ayah/Page (auto‑send to user or channel or group)
  - Random 1 Ayah/Page on demand
  - Search/select a specific Ayah by reference
  - Inline button under each Ayah/Page to open the Natiq app
- Bot keyboard (ReplyKeyboardMarkup) with:
  - “Quran” (access Quran features)
  - “Admin Settings” (for bot configuration)
- Support multiple languages (selectable via environment variable or admin settings).
- Platform identifier via environment variable (e.g., PLATFORM=TELEGRAM). This value is stored in all relevant database records to logically separate data belonging to different social media platforms that share the same bot logic.

### Out-of-Scope

- Non‑Telegram platforms (Discord, WhatsApp, etc.)
- Features that are specific to non‑Telegram APIs (e.g., PLATFORM_X) that would break the unified codebase.
- User reading tracking – no analytics on how much a user reads.
- Voice/audio features beyond text.

---

## 4. Architecture & Technologies

## Bot

- **Language**: Python
- **SDK**: python-telegram-bot
- **Quran Data Source**: Natiq API
- **Database**: PostgreSQL (shared across all platform instances)
- **Broker**: Redis

### Infrastructure

- **CI/CD**: GitHub Actions
- **Hosting**:
  - Single standalone server (Linux) running Docker
  - One Bot container instance per supported social media platform (each configured via environment variables)
- **Docker available containers**:
  - bot (one container per platform, e.g., bot-telegram, bot-platformX)
  - postgres (shared database server)
  - redis (shared message broker / cache)

---

## 5. Pending Decisions

- Future feature roadmap – Which Islamic topics (Hadith, Tafsir, prayer times, etc.) should the bot cover after the Quran module?

---

## 6. Timeline

TBD

---

## 7. Risks & Challenges

- Platform API changes – Telegram (or compatible platforms) may deprecate or modify Bot API features.
- Cross‑platform compatibility – Platforms with “Telegram‑like” APIs may introduce subtle differences that still require code adaptation.

---

## 8. Success Metrics

- Bot runs stably for 30 consecutive days without manual intervention.
- Daily verse delivery reliability ≥ 99% (no missed scheduled posts).

---

## 9. Budget & Resources

- **Human Resources**: 1 developer
- **Hardware/Software Resources**: 1 server

---

## 10. Approval Signatures

| Role            | Github Account                                    |
| --------------- | ------------------------------------------------- |
| Curator         | [Al-Abd](https://github.com/al-abd)               |
| DevOps          | [codebysilence](https://github.com/codebysilence) |
| Project Manager | [ibruxo](https://github.com/ibruxo)               |
