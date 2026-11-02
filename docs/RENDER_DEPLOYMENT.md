# Complete Render Deployment Guide for Home Budget

This guide explains step-by-step how to deploy this **Flask + MySQL** project on **Render** (Render.com).

---

## Architecture on Render

```
[ User Browser (HTTPS) ]
         │
         ▼
[ Render Web Service (Free Tier) ]
   └── Gunicorn (WSGI) -> run:app (Flask)
         │
         ▼  (Remote MySQL Connection)
[ Cloud MySQL 8 Database ]
   └── (e.g. Aiven / TiDB Cloud / Clever Cloud / Railway)
```

---

## Step 1: Set Up a Free Cloud MySQL Database

Render's native free database is PostgreSQL, but our project uses MySQL 8.
You can get a free, permanent MySQL 8 cloud database in 2 minutes from any of these providers:

### Option A: TiDB Cloud (Recommended - Free Tier, Serverless MySQL)
1. Go to [https://tidbcloud.com/](https://tidbcloud.com/) and sign up (Free).
2. Create a **Serverless Cluster** (Free).
3. Under cluster overview, click **Connect**.
4. Note your:
   - **Host** (e.g., `gateway01.us-east-1.prod.aws.tidbcloud.com`)
   - **Port** (e.g., `4000` or `3306`)
   - **User** (e.g., `xxxx.root`)
   - **Password**
   - **Database Name** (e.g., `home_budget_db` or `test`)

### Option B: Aiven for MySQL (Free Trial) or Clever Cloud
1. Create a free MySQL database on [https://aiven.io/](https://aiven.io/) or [https://www.clever-cloud.com/](https://www.clever-cloud.com/).
2. Copy the connection credentials: **Host, Port, User, Password, Database Name**.

---

## Step 2: Initialize Database Tables & Seed Demo User

From your local machine (PowerShell), point your `.env` temporarily to your cloud database credentials:
```powershell
# In your local project directory:
python database/init_db.py
python database/seed_sample_data.py
python database/create_demo_user.py
```
*(This creates the tables `users`, `categories`, `transactions`, `monthly_budgets`, populates the default categories & transactions, and sets up `demo@example.com` with `Demo@1234`).*

---

## Step 3: Push Code to GitHub

If you haven't pushed your code to GitHub yet:
1. Initialize git and commit:
   ```powershell
   git init
   git add .
   git commit -m "Initial commit for Render deployment"
   ```
2. Create a new repository on [https://github.com/new](https://github.com/new) (e.g. `home-budget-tracker`).
3. Push your repository:
   ```powershell
   git remote add origin https://github.com/<your-username>/home-budget-tracker.git
   git branch -M main
   git push -u origin main
   ```

*(Note: Your local `.env` is in `.gitignore`, so your local database passwords will never be exposed on GitHub).*

---

## Step 4: Create a Web Service on Render

1. Log in to [https://render.com/](https://render.com/).
2. On your Render Dashboard, click **New +** -> **Web Service**.
3. Select **Build and deploy from a Git repository**.
4. Connect your GitHub account and select your repository (`home-budget-tracker`).
5. Configure the deployment settings:
   - **Name:** `home-budget-tracker` (or your preferred name)
   - **Region:** Choose the region closest to your cloud database (e.g., *Singapore*, *Oregon*, or *Frankfurt*)
   - **Branch:** `main`
   - **Root Directory:** Leave blank (default)
   - **Runtime:** `Python 3`
   - **Build Command:** 
     ```bash
     pip install --upgrade pip && pip install -r requirements.txt
     ```
   - **Start Command:**
     ```bash
     gunicorn run:app
     ```
   - **Instance Type:** `Free`

---

## Step 5: Configure Environment Variables on Render

Scroll down to the **Environment Variables** section on the same page (or under the **Environment** tab of your service) and add the following keys:

| Key | Value | Description |
|:---|:---|:---|
| `SECRET_KEY` | *(A long random secret string)* | Flask session encryption |
| `FLASK_ENV` | `production` | Production mode |
| `DB_HOST` | `your-cloud-mysql-host.com` | Hostname from Step 1 |
| `DB_PORT` | `3306` (or `4000` for TiDB) | Port from Step 1 |
| `DB_NAME` | `home_budget_db` | Database name from Step 1 |
| `DB_USER` | `your_db_username` | Database user from Step 1 |
| `DB_PASSWORD` | `your_db_password` | Database password from Step 1 |
| `CURRENCY_SYMBOL` | `₹` | Currency symbol |

---

## Step 6: Deploy & Verify!

1. Click **Create Web Service** (or **Deploy Latest Commit**).
2. Render will run:
   - Dependency installation (`pip install -r requirements.txt`)
   - Start the WSGI server (`gunicorn run:app`)
3. Once the build finishes and shows **"Your service is live 🎉"**, click your Render URL (e.g., `https://home-budget-tracker.onrender.com`).
4. Log in using your demo credentials:
   - **Email:** `demo@example.com`
   - **Password:** `Demo@1234`
5. Test adding a transaction, checking monthly budgets, viewing charts, and downloading a CSV report.

---

## Free Tier Note
On Render's Free tier, if there are no visits for 15 minutes, the service will "spin down" to save energy. When someone visits the URL, it will take about 30–50 seconds for the first page to spin back up, after which it runs smoothly!
