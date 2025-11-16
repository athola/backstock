# 90-Day Database Rotation Checklist

Use this checklist when rotating your Render free-tier PostgreSQL database.

## Pre-Rotation Information

- **Current Database Name:** _______________________
- **Database Created Date:** _______________________
- **Expiration Date (Created + 90 days):** _______________________
- **New Database Name:** _______________________

---

## Day 85: Create Final Backup

- [ ] Trigger backup via GitHub Actions
  - Go to: https://github.com/YOUR_USERNAME/backstock/actions
  - Select "Database Backup" workflow
  - Click "Run workflow" → "Run workflow"
  - Wait for completion (green checkmark)

- [ ] **OR** Create manual backup:
  ```bash
  export DATABASE_URL="your_current_database_url"
  ./scripts/backup_database.sh
  ```

- [ ] Verify backup exists
  - GitHub: Check Releases tab for new backup release
  - Local: Run `ls -lh backups/` to see backup file

- [ ] Download backup for safekeeping
  - Save to: _______________________

---

## Day 86: Create New Database

- [ ] Log into Render Dashboard: https://dashboard.render.com

- [ ] Create new PostgreSQL database
  - Click **New +** → **PostgreSQL**
  - Name: _______________________
  - Database: `backstock`
  - User: `backstock`
  - Region: Same as current
  - Plan: **Free**
  - Click **Create Database**

- [ ] Wait for provisioning (2-3 minutes)

- [ ] Copy **Internal Database URL**
  - Format: `postgresql://user:pass@host:port/dbname`
  - Save to: _______________________

---

## Day 87: Restore Backup

- [ ] Set new database URL:
  ```bash
  export DATABASE_URL="paste_new_database_url_here"
  ```

- [ ] Restore from backup:
  ```bash
  ./scripts/restore_database.sh backups/backstock_backup_YYYYMMDD_HHMMSS.sql.gz
  ```

- [ ] Confirm restore when prompted: Type `yes`

- [ ] Verify restoration:
  ```bash
  psql $DATABASE_URL -c "SELECT COUNT(*) FROM grocery_items;"
  ```
  - Expected count: _______________________

- [ ] Run any pending migrations:
  ```bash
  python manage.py db upgrade
  ```

---

## Day 88: Test New Database

### Local Testing

- [ ] Update local `.env` file with new DATABASE_URL

- [ ] Start application locally:
  ```bash
  python manage.py runserver
  ```

- [ ] Test critical features:
  - [ ] Search for items
  - [ ] Add new item
  - [ ] Upload CSV file
  - [ ] View all items

- [ ] Check for errors in logs

### Optional: Create Test Service

- [ ] Create temporary web service in Render
  - Point to new database
  - Deploy application
  - Test functionality

---

## Day 89: Update Production

- [ ] Update DATABASE_URL in Render
  - Dashboard → `backstock` web service
  - **Environment** tab
  - Edit `DATABASE_URL`
  - Paste new database URL
  - Click **Save Changes**

- [ ] Wait for automatic redeployment (5-10 min)

- [ ] Monitor deployment logs
  - Check for successful startup
  - Look for database connection confirmation

- [ ] Test production application:
  - [ ] Visit: https://backstock.onrender.com
  - [ ] Search items
  - [ ] Add item
  - [ ] Upload CSV
  - [ ] Verify data matches backup

- [ ] Update GitHub Secret (for backups):
  - GitHub repo → Settings → Secrets → Actions
  - Edit `RENDER_DATABASE_URL`
  - Update with new database URL
  - Click **Update secret**

---

## Day 90: Delete Old Database

**⚠️ ONLY proceed if new database is working correctly!**

- [ ] Final verification:
  - [ ] Application is accessible
  - [ ] Data is present and correct
  - [ ] No errors in logs
  - [ ] Backup is safely stored

- [ ] Delete old database:
  - Dashboard → Select old database
  - **Settings** tab
  - Scroll to **Danger Zone**
  - Click **Delete Database**
  - Type database name to confirm
  - Click **Delete**

- [ ] Confirm application still works:
  ```bash
  curl https://backstock.onrender.com/
  ```

---

## Post-Rotation

- [ ] Document new database information:
  - Created Date: _______________________
  - Next Expiration: _______________________
  - Set calendar reminder for Day 85

- [ ] Update this checklist with new dates for next rotation

- [ ] Store completed checklist in records

---

## Emergency Contacts

- **Render Support:** support@render.com
- **Documentation:** docs/RENDER_DEPLOYMENT.md
- **Backup Workflow:** .github/workflows/database-backup.yml

---

## Notes

Use this space to document any issues, special considerations, or lessons learned:

```
Date: _______________________
Notes:












```

---

**Next Rotation Date:** _______________________
**Reminder Set:** [ ] Yes  [ ] No
