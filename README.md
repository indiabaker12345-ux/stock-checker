# Stock Checker - Meaco Air Conditioner

Checks 3 product pages every 5 minutes and emails you the moment one comes back in stock:

- John Lewis - Meaco Cirro 12000 BTU
- AO.com - Meaco Cirro 14000 BTU Inverter
- Currys - Meaco MeacoCool 14kBTU Inverter

It runs entirely on GitHub's free servers, nothing needs to stay on your laptop.

## Setup (about 10 minutes, one-time)

### 1. Create a free GitHub account
If you don't have one already: https://github.com/join

### 2. Create a new repository
- Go to https://github.com/new
- Name it something like `stock-checker`
- Set it to **Public**. This matters: public repos get unlimited free GitHub Actions minutes, whereas private repos are capped at 2,000 free minutes/month. Checking 3 pages every 5 minutes would blow past that cap on a private repo within a few days. Nothing in these files is sensitive (your email credentials stay safe as encrypted Secrets either way, never exposed in code or logs).
- Click "Create repository"

### 3. Upload these files
On the new repo's page, click "uploading an existing file" and drag in all the files from this folder (keeping the `.github/workflows` folder structure intact). Commit them to the `main` branch.

### 4. Create a Gmail App Password
Regular Gmail passwords won't work for this - you need an "app password":
1. Go to https://myaccount.google.com/security
2. Make sure **2-Step Verification** is turned on (required for app passwords)
3. Go to https://myaccount.google.com/apppasswords
4. Create a new app password (name it "stock checker")
5. Copy the 16-character password it gives you - you won't see it again

### 5. Add secrets to your GitHub repo
In your repo: **Settings → Secrets and variables → Actions → New repository secret**

Add these three:
| Name | Value |
|---|---|
| `EMAIL_ADDRESS` | Your Gmail address (the one sending the alert) |
| `EMAIL_APP_PASSWORD` | The 16-character app password from step 4 |
| `TO_EMAIL` | The email address you want alerts sent TO (can be the same Gmail address) |

### 6. Test it
Go to the **Actions** tab in your repo → click "Stock Check" on the left → click "Run workflow" → "Run workflow" button. Watch it run (takes about a minute). Check the logs to confirm it's finding the pages correctly.

That's it - it'll now run automatically every 20 minutes, forever, for free.

## Adjusting the check frequency

Open `.github/workflows/check-stock.yml` and change the cron line. It's currently set to every 5 minutes - GitHub's shortest reliably-honoured interval. Some other options:
- Every 10 minutes: `*/10 * * * *`
- Every 15 minutes: `*/15 * * * *`
- Every hour: `0 * * * *`

Note: 5-minute checks only stay free if the repo is **public** (see setup step 2). On a private repo you'd exhaust the 2,000 free monthly minutes in a few days at this frequency.

GitHub also disables scheduled workflows automatically if a repo has been inactive for 60 days, so if you stop getting emails after a couple of months, just visit the Actions tab and re-enable it.

## If a site's stock detection isn't working

Retail sites occasionally redesign their pages, which can throw off the text-matching. If you notice a product SHOULD say in-stock but the checker isn't catching it (or vice versa), let me know what the page actually says near the "add to basket" button and I'll adjust the detection phrases in `check_stock.py`.
