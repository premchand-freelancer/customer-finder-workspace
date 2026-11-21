# First-time setup (applies before any customer research)

If `.agents/skills/first-customer-finder/SKILL.md` does not exist, the repository has not yet been installed. The original skill is temporarily staged at `skill-source/first-customer-finder/` for browser-compatible uploading. Before doing any customer research, copy that directory into `.agents/skills/first-customer-finder/` without changing its content, copy `gitignore-template.txt` to `.gitignore`, run `python3 scripts/check_workspace.py` and `python3 -m unittest discover -s tests -v`, then propose a PR for these changes. Do not remove `skill-source/` until installation has been confirmed and committed. After installation use the full operating instructions below.

# Customer Finder Workspace — permanent Codex project instructions

This repository is for ongoing, evidence-based discovery of **potential** customers. Its verified public-signal research is provided by the original `first-customer-finder` skill at `.agents/skills/first-customer-finder/SKILL.md` (license included). Follow that skill's rules, and the additional rules here, for every relevant task.

## Natural-language trigger: zero technical prompts required

When the user asks to **find customers**, **find leads/prospects**, **find beta users**, **find design partners**, **find more/new customers**, **refresh leads**, or **review/mark leads**, automatically follow this workflow without requiring `$first-customer-finder` or the user to repeat setup instructions. Interpret simple messages like **"Find 10 new customers"** as: use the primary product profile, research up to ten genuinely new evidence-backed prospects, create Markdown/CSV results, propose an update to the approved business-only history, and do not send outreach. If the user asks for a different size, segment, or location, honor that request. Default is the skill's **standard** mode (up to 10), with quick for <=5 and deep for >10 up to 20.

## Product profile

Read `products/main.md` before each search. This is the **single source of truth** for the primary product, ICP, geography, exclusions, and feedback preferences. If the profile has `NOT_SET` for its product URL/description, ask the user **once** for their URL or product description and save it; do not hallucinate a product. For a different product, create a separate profile and use a distinct `project_key`, never blend histories. Interpret the default product key as the stable canonical product URL or explicit slug in the profile. Update these files only with the user's facts or clearly labeled inferences.

## Accuracy and research safety

- Read `.agents/skills/first-customer-finder/SKILL.md` and the referenced research and report-artifact files before any search.
- Use available browsing/search tools and **open original public evidence**; a search snippet or stale unconfirmed claim cannot qualify a lead. If browsing is blocked, say so and do not invent contacts. Observe website access and community rules.
- Show original signal URL, published date (or explicitly unknown), checked date, target role basis, source-backed rationale, verified appropriate public contact route (or none), caution, and manual outreach draft. A numerical score is not a sales probability. Never pad the list to reach a quota.
- Restrict to intentionally public, professional/business information. No data brokers, scraped contact lists, personal phone/email enrichment, sensitive traits, private groups, or bypassing access controls. No outreach or external actions without separate explicit authorization.

## Durable business-only lead register (not a CRM)

- Before each **new** search, run `python3 scripts/lead_register.py list --product '<project_key>'`, and read `data/lead-register.csv`. Exclude listed entity IDs/normalized URLs during discovery. Also run `python3 scripts/lead_register.py seed-state --product '<project_key>' --out 'outputs/<safe-slug>/state.json'` before report generation. The original generator can then run with `--state outputs/<safe-slug>/state.json --new-only` to ensure already-listed entities do not reappear.
- Reports and the raw `state.json` belong under `outputs/` and **must remain uncommitted**, as required by the original skill. Use a fresh report run folder and the original generator syntax: `python3 .agents/skills/first-customer-finder/scripts/generate_report.py <analysis.json> <report.md> --csv <prospects.csv> --state <state.json> --new-only`.
- After generating a real report, use `python3 scripts/lead_register.py record --product '<project_key>' --report-json <analysis.json> --id <id> [--id <other-id>...]` to add **only verified businesses, business projects, or organizational profiles** from that report. Never copy personal profiles, individual names or private details into GitHub. The record command deliberately requires explicit ID selections. For individual-only prospects, leave history in task-local output and explain they will not persist across tasks.
- Do **not** assume any prospect is approved, contacted, replied, rejected, or a customer; add only `seen` business records from a report. Save user-stated judgments by `python3 scripts/lead_register.py review --product ... --id ... --decision ...` or `status` as appropriate. Do not infer outreach status from a draft.
- Prepare a **pull request** for changes to `data/lead-register.csv` and product profile, not a silent merge. Tell the user to **review and merge it** for permanent history. A new task will not see changes that have not been merged. If GitHub commit/push/PR is unavailable, present the edited file and the exact manual save action. Never claim persistence until committed and merged.
- Never commit `state.json`, `outputs/`, full scraped text, sensitive personal data, access tokens, or unapproved external contact data. A private repository helps restrict access but is still cloud storage.

## Responses and task completion

Return a short chat summary: count actually verified, top few prospects, links to accessible Markdown/CSV artifacts, source limits, and whether the reviewed register update was pushed and merged or still awaiting the user's action. No follow-up sales messaging is sent. If the user asks simply to 'mark P1', resolve rank P1 to its stable prospect ID from the named report before updating. Don't start background monitors automatically.

## Diagnostics

Run `python3 scripts/check_workspace.py` for setup sanity; run `python3 -m unittest discover -s tests -v` for package tests. The original skill's upstream unit tests were bundled in its original source ZIP but are not required at runtime; this package includes a local integration smoke test.
