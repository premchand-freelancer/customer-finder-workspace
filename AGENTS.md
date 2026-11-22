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

## CREASTO zero-investment qualification

CREASTO has $0 for discovery and applications. Apply the current profile and this check to every search and refresh, including “Find 10 new customers”, chat-only recommendations and manual drafts. Use free research sources only. Open the original public buyer request, confirm it is current, paid work, and verify that a freelancer or agency can use the specified reply or application method for free. Respect the buyer's instructions and platform contact restrictions. An uncertain cost, access rule or hiring status disqualifies the opportunity. Keep exclusions out of all recommendations and drafts. If three pass, return three. An empty shortlist is valid.

For CREASTO add an `eligibility` object to every v2 prospect in the local analysis. Record the following findings from inspected sources:

| Field | Qualification requirement |
| --- | --- |
| `buyer_request` | `website-development` for the default profile. Use `ai-ugc` only for an explicit UGC search under `creasto-ai-ugc`. Use the original buyer post as `source_url` and explain the requested deliverable and paid engagement in `evidence`. |
| `project_status` and `deadline` | Confirm `open` on the checked date. Record a published deadline as YYYY-MM-DD when available. For same-day deadlines check the time and time zone. Explain the current signal in `why_now`. |
| `compensation` and `applicant_access` | Confirm `paid` project work and `freelancer_or_agency_permitted`. Record who can apply and any platform or community restrictions in the contact route note. |
| `upfront_requirement` | Record `none` only after checking the entire submission path, including balances, deposits, credits, verification and memberships. |
| `cost_source_url` and `free_submission_evidence` | Link the original invitation or applicable official fee terms and describe what proves this exact route costs zero. A buyer inviting proposals by public thread reply or published business email can supply direct evidence. A missing price or a “free to join” claim is insufficient. |

Use the v2 verified `contact_route` for the exact application URL, allowed method (`label`), source of that permission, check date and note. For email, use the exact public page that invites proposals as the URL and identify the permitted business mailbox in the local route details. Never substitute an unrelated contact channel for a restricted one.

### Hard marketplace exclusion (CREASTO)

Never search for or recommend projects hosted by Freelancer.com, Freelancer.in,
Freelancer.co.uk, Freelancer.com.au, or Upwork, even when a page or a model claims
that applying is free. These sources are entirely excluded from CREASTO research,
chat summaries, outreach drafts, CSV, and Markdown prospect recommendations.
Do not include links to these platforms as actionable leads. This is an explicit
user preference, not a case-by-case cost assessment.

The deterministic validator `scripts/qualify_report.py` rejects excluded domains
in original buyer links, business URLs, contact routes, cost evidence, and source
labels. Run it **before any CREASTO report export or lead register update**, and
only summarize the qualified output. If Codex cannot validate its candidates,
return no qualified prospects instead of presenting unchecked results.

## Durable business-only lead register (not a CRM)

- Before each **new** search, run `python3 scripts/lead_register.py list --product '<project_key>'`, and read `data/lead-register.csv`. Exclude listed entity IDs/normalized URLs during discovery. Also run `python3 scripts/lead_register.py seed-state --product '<project_key>' --out 'outputs/<safe-slug>/state.json'` before report generation. The report generator uses `--state outputs/<safe-slug>/state.json --new-only` to ensure already-listed entities do not reappear.
- Reports and the raw `state.json` belong under `outputs/` and **must remain uncommitted**, as required by the original skill. For CREASTO, run the workspace qualification check first, even for chat-only results. Set `run` to the fresh run folder containing the analysis and seeded state, then run the following from the repository root.

  ```sh
  python3 scripts/qualify_report.py "$run/analysis.json" "$run/qualified.json" &&
    python3 .agents/skills/first-customer-finder/scripts/generate_report.py "$run/qualified.json" "$run/report.md" --csv "$run/prospects.csv" --state "$run/state.json" --new-only
  ```

  The qualifier defaults to the website project. Pass `--product creasto-ai-ugc` for an explicit UGC search. If validation fails, remove unsupported candidates, revise counts, verdict and plan, and rerun. Use the resulting qualified JSON for the register. For a refresh, recheck original sources and omit `--new-only` as directed by the skill. Other products use the original generator with their own analysis and history.
- After generating a real report, use `python3 scripts/lead_register.py record --product '<project_key>' --report-json <analysis.json> --id <id> [--id <other-id>...]` to add **only verified businesses, business projects, or organizational profiles** from that report. Never copy personal profiles, individual names or private details into GitHub. The record command deliberately requires explicit ID selections. For individual-only prospects, leave history in task-local output and explain they will not persist across tasks.
- Do **not** assume any prospect is approved, contacted, replied, rejected, or a customer; add only `seen` business records from a report. Save user-stated judgments by `python3 scripts/lead_register.py review --product ... --id ... --decision ...` or `status` as appropriate. Do not infer outreach status from a draft.
- Prepare a **pull request** for changes to `data/lead-register.csv` and product profile, not a silent merge. Tell the user to **review and merge it** for permanent history. A new task will not see changes that have not been merged. If GitHub commit/push/PR is unavailable, present the edited file and the exact manual save action. Never claim persistence until committed and merged.
- Never commit `state.json`, `outputs/`, full scraped text, sensitive personal data, access tokens, or unapproved external contact data. A private repository helps restrict access but is still cloud storage.

## Responses and task completion

Return a short chat summary: count actually verified, top few prospects, links to accessible Markdown/CSV artifacts, source limits, and whether the reviewed register update was pushed and merged or still awaiting the user's action. No follow-up sales messaging is sent. If the user asks simply to 'mark P1', resolve rank P1 to its stable prospect ID from the named report before updating. Don't start background monitors automatically.

## Diagnostics

Run `python3 scripts/check_workspace.py` for setup sanity; run `python3 -m unittest discover -s tests -v` for package tests. The original skill's upstream unit tests were bundled in its original source ZIP but are not required at runtime; this package includes a local integration smoke test.
