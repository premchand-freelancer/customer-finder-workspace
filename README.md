# First Customer Finder — beginner-friendly GitHub upload

This is the same prepared permanent workspace, repackaged **without hidden paths** to make GitHub browser upload easier. The original skill is under `skill-source/first-customer-finder/`. Codex will copy it into `.agents/skills/first-customer-finder/` during the first setup task.

## Upload from your browser
1. Create a **private** empty GitHub repository named `customer-finder-workspace`.
2. Unzip this download and open the inner folder called `customer-finder-workspace`.
3. On the empty repository's GitHub page, click `uploading an existing file` (or `Add file` → `Upload files`).
4. Drag all the files **and folders inside** `customer-finder-workspace` into the GitHub upload area, not the outer folder and not the ZIP.
5. You should see `AGENTS.md`, `README.md`, `skill-source/first-customer-finder/SKILL.md`, `products/main.md`, `data/lead-register.csv`, etc. Commit the upload.

## Configure Codex in browser
1. Visit https://chatgpt.com/codex and sign in. Connect GitHub, select this repo, create a Cloud environment. Confirm Python 3 and public internet access to research sources; publish the environment.
2. Start a task using the new environment with this prompt, filling in your actual product description:

> Set up my permanent customer-finding workspace. Read AGENTS.md and README.md. Copy the original skill from skill-source/first-customer-finder/ to .agents/skills/first-customer-finder/, preserving all files. Copy gitignore-template.txt to .gitignore. Verify installation by running python3 scripts/check_workspace.py and python3 -m unittest discover -s tests -v. My product is [PRODUCT URL OR DESCRIPTION]. Fill products/main.md accurately; do not invent unsupported facts. Prepare a pull request with all permanent setup changes. Do not research customers or contact anyone yet. Tell me how to merge the pull request.

3. Review and merge the PR in GitHub. For later tasks use the same repo and published environment. New searches use a one-sentence prompt such as `Find 10 new customers.`
4. After each research task, review and merge the **business-only** lead-register PR to preserve deduplication.

Do not store private contacts or the raw original skill `state.json` in GitHub. Sources must be verified; no automatic outreach.
