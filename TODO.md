# Blood Bowl League App: Todo

Done and still to do, in the order planned. The detail behind each finished item is in HANDOFF.md.
Updated 2026-11-05.

## Done

### Backend (FastAPI, PostgreSQL)
- [x] Reference data from the spreadsheet: races, positions, skills, star players, mercenaries,
      inducements, Dungeon Bowl. Read-only endpoints.
- [x] Accounts: signup (coach or commissioner), login, Argon2 passwords, JWT access tokens.
      Super admin is created once by the host with a script.
- [x] Leagues: create (commissioners), join by code, search, request to join, approve or reject,
      join code view and regenerate.
- [x] Seasons: create (league owner), starting treasury.
- [x] Teams: create (one per coach per season), treasury copied from the season.
- [x] Players: hire (cost from the treasury, automatic shirt numbers, position limits,
      journeymen only while fewer than 11 players are available), edit name and number, fire.
- [x] Extras: re-rolls, assistant coaches, cheerleaders, apothecary and dedicated fans, with prices
      from the spreadsheet. A shop endpoint shows prices before buying.
- [x] Team value, using the spreadsheet's rules, including Low Cost Linemen.
- [x] Permissions on every endpoint: outsiders get 404, members without the right get 403.
- [x] Hardening: rate limits, production mode (docs off, CORS allowlist, security headers),
      pagination, pinned and audited dependencies.
- [x] Coach names: unique (ignoring case), 3 to 32 safe characters.
- [x] 148 automated tests.

### Frontend (React, TypeScript, Vite)
- [x] Login and logout. The token is kept in memory only.
- [x] Signup with a random orcish coach name suggested.
- [x] My leagues, join by code, league page (seasons and members).
- [x] Season page, team page (roster, staff and extras, team value).
- [x] Create season, create team, hire, fire, edit player, buy extras.
- [x] Commissioner panel: join code (copy, new code), join requests (approve, reject).

## Next

1. [x] **Search and join leagues** from the app, following each league's join policy
       (open: join now; approval: request; invite only: code needed).
2. [x] **Rename the 16s format to 11s.** Migration to rename the database enum value
       (`SIXTEENS` to `ELEVENS`), plus the API, tests and season form.
3. [x] **Coach name at signup** with a random Blood Bowl / orcish name suggested, and a button to
       roll a new one. The coach can keep it or type their own.
       - Names are unique (ignoring case), 3 to 32 characters, letters, digits, spaces,
         hyphens and apostrophes only, so no one can copy another coach's name.
       - The suggestion is made in the browser, so there is no new public endpoint.
       - The dev database has several accounts called "string"; rename them before the unique
         index migration.
4. [x] **Roster table like the Print Roster sheet.** Remove the Notes column. Columns as on the sheet:
       #, Name, Position, MA, ST, AG+, PA+, AV+, Skills and Improvements, Miss Next Game, Niggling
       Injuries, Comp, TD, Int, Cas, MVP, SPP, Total Value. Team info block (team, coach, race,
       treasury, TV), then re-rolls, staff and extras.
5. [x] **Look and feel from the sheet.** White, red and cream:
       - red `#A61C00` with white text for headings and table headers;
       - cream `#F2E2D2` for label cells;
       - white for the body, Arial or a similar sans-serif.
       Self-hosted fonts only (see SECURITY.md).
6. [x] **Printable roster.** A print stylesheet so the team page prints like the Print Roster sheet.

## Design (agreed 2026-11-05, from the owner's sketches)

Sketches and the sheet's print-out are in `backend/data/` (git-ignored; phone photos can carry GPS data).

A. [ ] **App shell.** Top bar on every page: logo top-left (links home), Teams and Leagues in the
       middle, burger menu on the right (account name, log out). Replaces "Logged in as".
       Placeholder logo until the owner supplies an SVG or PNG.
B. [ ] **Teams page and Leagues page.** Teams: each of my teams (current and past) with a strip of
       relevant info (race, league, season, TV, record); choosing one opens the Print Roster layout.
       Leagues: each league with relevant info; choosing one shows the season (league) table.
       Needs a new `GET /me/teams` endpoint.
C. [ ] **Roster in the full Print Roster layout**: 16 numbered slots and SP1-SP3 always shown,
       6 advancement boxes under the skills, "135,000 GP" money, centred cells, full team info
       (games, W/D/L, league points, TV/CTV, fans), inducements and special rules blocks. Parts that
       need games or advancements stay blank until those exist.
D. [ ] **Save as PDF**: `GET /teams/{id}/roster.pdf` built by the API with ReportLab, one A4
       landscape page, member check (outsiders 404), rate limited, names escaped.
E. [ ] **Home page** (the dashboard), in sections:
       - **Recent games**: a snapshot of the latest results (and injuries) in my leagues.
       - **My teams**: a short info card for each of my teams (race, league, season, TV, record),
         linking to its roster.
       - **Current leagues and tournaments** I'm in, with a link to each table.
       - **FAQ**: how the app works (joining a league, hiring, treasury, printing a roster).
         Static text written in the app, no database needed.
       - **Commissioners** also see snapshots of the leagues they run, pending join requests
         and issues raised by coaches.
       Layout first, with "No games yet" / "No tournaments yet" until games and results (item 7)
       and tournaments (item 16) exist.
F. [ ] **Issues raised by coaches** (new): a coach reports an issue to their league's commissioner,
       who sees and closes it. Needs its own small backend with permission checks.

## After that

7. [ ] **Games and results**: fixtures (GameList), scores, casualties, SPP, MVP, injuries
       (miss next game, niggling, dead), dedicated fans +/-, winnings.
8. [ ] **League table** from the results.
9. [ ] **Skills and advancements**: spend SPP, primary or secondary, random or chosen, with value
       changes feeding team value.
10. [ ] **Roster cap**: 16 players, with a separate limit for 7s.
11. [ ] **Redraft a team from a previous season** with the standard redraft rules.
        - The owner provides the rule text, as was done for Low Cost Linemen.
        - The spreadsheet's "Cost to Re-Draft" is the player's value, plus 20,000 per season
          completed for players who want to retire.
        - New data needed: seasons completed and "wants to retire" per player, and a finished
          season.
        - Only the coach of the old team can redraft it, into a season of a league they belong
          to. The budget is always worked out by the API.
12. [ ] **Inducements, star players and mercenaries** in games and team value (CTV), special
        balls, upkeep, ranks.
13. [ ] **Admin console** (`/admin`, super admin only) with an audit log of every change:
        suspend or restore accounts, grant or revoke commissioner, transfer league ownership,
        data fixes.
14. [ ] **League management**: leave league, remove member, transfer ownership, change name or
        join policy, audit log of treasury changes.
15. [ ] **Accounts**: refresh token in an httpOnly cookie (stay logged in across page reloads),
        logout that revokes it, email verification, password reset.
16. [ ] **Tournaments**, 7s section, Dungeon Bowl play.
17. [ ] **Real-time updates** with WebSockets (short-lived ticket, never a token in the URL).

## Before deploying
See the checklist in SECURITY.md. Nothing goes on a public server until every box there is ticked.
