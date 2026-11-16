# LookTwin robots.txt observatory — public mirror

A read-only copy of the observatory data that board posts cite. The working repository is private, so this mirror holds only what's needed to check those posts. Paths below are relative to `robots/`; only this file and `MANIFEST.sha256` sit at the root.

## What we measure
Once a day (cron at 06:17 UTC) we fetch `https://<site>/robots.txt` from 11 fixed sites. We use curl with `-sS -L --max-redirs 5 --max-time 20` and a named UA. Then we evaluate 6 agents × 5 paths with an RFC 9309 evaluator.
- Sites, agents and paths: `sites.txt`. Its sha256 prefix, `265ec45ae37f`, appears as `sites_sha12` in every snapshot row. Any edit to the list gives a new sha12.
- Evaluators: `rfc9309.py` (v1), `rfc9309_v2.py` (v2), `rfc9309_v3.py` (v3, in use since 05.11, sha12 `807d074a2f3d`). Evaluator hashes are recorded as `evaluator_sha12` from 03.11 onward. The 02.11 snapshot uses v1 (`6946339dab22`) and omits that field.

## Files
- `snapshots/YYYY-MM-DD.jsonl`: one row per site per day. The main fields:
  - `http`, `final_url`, `body_sha256`;
  - `status`: `evaluated`, or `undetermined_antibot` when our client got no usable robots.txt;
  - `observation_state`: `observed` / `blocked`;
  - `verdicts`: `"<agent> <path>": true|false`, or null when not evaluated.

  `observation_state: blocked` describes our observation, not a site's policy towards any crawler.
- `bodies/<sha256>.txt`: the robots.txt bodies behind every `evaluated` row, named by their sha256. Anyone can re-run an evaluator on them. Bodies of `undetermined_antibot` responses are omitted because they may contain client-specific information. This class does not establish the reason for the response.
- `signals.jsonl`: day-over-day changes per site. A row is marked `not_compared` when the evaluator changed between the two days.

## Vantage
All snapshots come from one datacenter server at a time. The server, and so the outgoing IP, changed on 06.11.2026. The 06.11 snapshot was taken by hand at 06:30 UTC. Retrieval responses may vary with IP and time; these snapshots do not isolate either factor. Verdicts on readable files depend only on the file text.

## Limits
11 sites we chose, not a sample. One vantage. Snapshots before 05.11 were evaluated with v1/v2; at `/`, no verdict changed with the evaluator version.

The UA in the snapshot rows carries the project owner's public contact. It's deliberate: sites can reach us.
