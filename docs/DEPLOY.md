# Deploy: GitHub, then Streamlit Community Cloud

Every command runs from the repo root, in the virtual environment. Nothing here needs a paid account.

## 0. Before you start

Publish at least two or three briefings, or the live site will greet visitors with "No briefings are published yet." See `docs/REVIEW_PACK.md`, then:

```bash
python -m scripts.review list
python -m scripts.review publish --briefing "CPS 230 Operational Risk"
```

Check it locally before anyone else sees it:

```bash
streamlit run frontend/Briefing_library.py
```

You should see only what you published, the comparison page showing "Under review" for unreviewed cells, and the self-assessment.

## 1. Create the GitHub repository

### Option A: no git installed, upload in the browser

This is the fastest route the first time. It gives you a real repository; you can switch to git later without losing anything.

1. **Make a GitHub account** at github.com. Use a username you would put on a resume (`yograjgarg` rather than a nickname). Verify the email.
2. **Extract the zip.** Right-click `risk-intel-v0.9.zip`, Extract All. Inside the extracted folder is a folder named `risk-intel`. That inner folder is the repository.
3. **Show hidden files in File Explorer** before you upload anything: View, then tick Hidden items. Three items are hidden by default and all three matter:
   - `.github` holds the workflow that runs the tests and the weekly source check
   - `.streamlit` holds the theme config
   - `.gitignore` keeps the database file and caches out of the repo
4. **Create the repository.** On github.com, New repository. Name `risk-intel`, Public, and do **not** add a README, .gitignore or licence: the folder already has all three.
5. **Upload.** On the empty repository page, click "uploading an existing file". Open the `risk-intel` folder, select everything inside it (Ctrl+A), and drag it into the browser. Drag the **contents**, not the folder itself: if a `risk-intel/` folder appears inside the repository, every path shifts down one level and the Streamlit main file path below stops matching.
6. Check the file list in the browser shows `.github`, `.streamlit`, `app`, `data`, `docs`, `frontend`, `ingestion`, `scripts`, `tests`, `README.md`, `requirements.txt`, `LICENSE`. If the dot folders are missing, you skipped step 3.
7. Commit message: `Model and market risk intelligence platform`. Commit directly to `main`.

To update the site later, open the file on GitHub, click the pencil, paste the new content and commit. That works for a JSON edit after publishing a briefing. Once you are doing it often, install git and use Option B.

### Option B: with git installed


Name it `risk-intel`, public, no README (this repo already has one).

```bash
git init
git add .
git commit -m "Model and market risk intelligence platform"
git branch -M main
git remote add origin https://github.com/<your-username>/risk-intel.git
git push -u origin main
```

On the repository page, set the About description to: *Comparing how the US, UK, Canada and Australia regulate model risk, with a searchable briefing library and a governance self-assessment.* Add topics: `model-risk`, `market-risk`, `apra`, `regulatory-technology`, `fastapi`, `streamlit`.

The `Tests` workflow runs pytest on every push. A green tick on the repo is worth having before you link it anywhere.

## 2. Deploy the app

1. Sign in at share.streamlit.io with the same GitHub account.
2. Create app, from the existing repo `risk-intel`, branch `main`.
3. Main file path: `frontend/Briefing_library.py`.
4. Deploy. Leave `SHOW_DRAFTS` unset: drafts must stay invisible publicly.
5. Set a memorable subdomain in Settings, for example `model-risk-intel`.

The app builds its database from the seed JSON on startup, so there is nothing to upload. After you publish more content, push the change and use Reboot app so it rebuilds.

## 3. Schedule the source checks (optional, after deploying)

1. Repository Settings, Secrets and variables, Actions, New repository secret: name `RISK_INTEL_CONTACT`, value your email. The scraper sends it in the User-Agent so the regulators can reach you.
2. Actions tab, enable workflows.
3. Run `Check regulator sources` manually once. It is a dry run and prints candidates to the job log.
4. The weekly schedule is `0 21 * * 0`, which is Monday 07:00 Brisbane time. GitHub disables schedules on repos with 60 days of no activity.

Before scheduling it, read the terms of use and robots.txt for apra.gov.au, rba.gov.au and bis.org.

## 4. Once it is live

- Add the link to the README at the top.
- Then, and only then, the resume bullet in the build plan becomes usable.
- Re-check the dates in each published briefing every quarter, and refresh `last_reviewed_by_you` with `python -m scripts.review publish --briefing "<name>"`.
