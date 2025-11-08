# How to Enable Scheduled Functions in Netlify

## 📍 Step-by-Step Guide

### After Deploying Your Site to Netlify:

---

## Step 1: Access Your Site Dashboard

1. Go to [Netlify Dashboard](https://app.netlify.com/)
2. Click on your deployed site (the one you just created)

---

## Step 2: Navigate to Site Settings

1. Look at the top navigation bar
2. Click on **"Site settings"** (or **"Site configuration"**)

```
[Site overview] [Deploys] [Functions] [Site settings] ← Click here
```

---

## Step 3: Find Functions Settings

Once in Site Settings:

1. Look at the left sidebar menu
2. Scroll down to find **"Functions"** section
3. Click on **"Functions"**

**Left Sidebar Menu:**
```
├─ General
├─ Build & deploy
├─ Domain management
├─ Identity
├─ Forms
├─ Functions          ← Click here
├─ Environment variables
└─ ...
```

---

## Step 4: Enable Scheduled Functions

In the Functions settings page:

1. Look for section: **"Scheduled functions"**
2. You'll see a toggle switch or button
3. Click to **Enable scheduled functions**

**What you'll see:**
```
┌─────────────────────────────────────────────┐
│ Scheduled Functions                          │
│                                              │
│ Run functions on a schedule using cron      │
│ expressions in netlify.toml                 │
│                                              │
│ [ ] Disabled    [Enable] ← Click this       │
└─────────────────────────────────────────────┘
```

4. After enabling, it should show:
```
✅ Scheduled functions enabled
```

---

## Alternative Method: Check if Already Enabled

### Via Netlify UI (Newer Interface):

Some Netlify accounts have scheduled functions **automatically enabled** when you use the `netlify.toml` configuration.

**To verify if it's working:**

1. Go to your site dashboard
2. Click **"Functions"** tab (top navigation)
3. You should see your function: `send-notification`
4. Click on it to see details
5. Look for **"Triggers"** section
6. It should show: `Scheduled: 0 9 * * *`

---

## Step 5: Verify Installation

### Check Plugin Installation:

The scheduled functions plugin should auto-install from your `netlify.toml` configuration:

```toml
[[plugins]]
  package = "@netlify/plugin-scheduled-functions"
```

**If it doesn't auto-install:**

1. Go to **Site settings** → **Build & deploy** → **Build plugins**
2. Look for "Scheduled Functions" plugin
3. Click **"Install"** if not already installed

---

## Step 6: Check Function Deployment

After enabling, verify your function is scheduled:

### Method 1: Functions Tab
```
1. Dashboard → Your Site → Functions tab
2. Click "send-notification"
3. Check for "Next invocation" time
```

### Method 2: Deploy Logs
```
1. Dashboard → Your Site → Deploys
2. Click latest deploy
3. Check deploy logs for:
   "✓ Scheduled function detected: send-notification"
```

---

## 🚨 Troubleshooting

### Issue 1: "Scheduled Functions" option not visible

**Solution A: Redeploy**
```bash
# Make a small change and redeploy
git commit --allow-empty -m "Trigger redeploy"
git push
```

**Solution B: Check Team Plan**
- Scheduled functions are available on **ALL Netlify plans** (including free)
- If you can't see the option, try logging out and back in

### Issue 2: Function not running on schedule

**Checklist:**
- ✅ Environment variables set (ONESIGNAL_APP_ID, etc.)
- ✅ netlify.toml has correct schedule configuration
- ✅ Function deployed successfully (check Functions tab)
- ✅ Wait at least 1 scheduled run time to verify

**View Function Logs:**
```
Dashboard → Functions → send-notification → Function log
```

### Issue 3: Plugin not installing

**Manual fix:**

1. Add to `package.json` devDependencies:
```json
{
  "devDependencies": {
    "@netlify/plugin-scheduled-functions": "^1.0.0"
  }
}
```

2. Redeploy

---

## ✅ Confirmation Checklist

You'll know scheduled functions are working when:

- [ ] "Scheduled functions" shows as enabled in settings
- [ ] Function appears in Functions tab with schedule icon
- [ ] Deploy logs show: "Scheduled function detected"
- [ ] Function logs show execution at scheduled times
- [ ] Manual trigger works: `/.netlify/functions/manual-trigger`

---

## 🔄 Quick Test

Don't want to wait for scheduled run? Test immediately:

1. **Via Browser:**
   Visit: `https://YOUR-SITE.netlify.app/.netlify/functions/manual-trigger`

2. **Via curl:**
   ```bash
   curl https://YOUR-SITE.netlify.app/.netlify/functions/manual-trigger
   ```

3. **Check Logs:**
   ```
   Functions → send-notification → Function log
   ```

You should see:
```
🚀 Starting scheduled notification job...
✅ Post fetched: [Post Title]
✅ Notification sent successfully!
```

---

## 📞 Still Having Issues?

**Contact Netlify Support:**
- Dashboard → Site → Support → "Contact support"
- Include: "Need help enabling scheduled functions"

**Common Questions to Answer:**
- Have you set all environment variables?
- Does manual trigger work?
- What do function logs show?

---

## 🎯 Expected Behavior After Setup

Once everything is configured:

1. **Immediate:** Manual trigger works via URL
2. **Next scheduled time:** Function runs automatically (e.g., 9:00 AM UTC)
3. **Daily:** Notification sent every day at scheduled time
4. **Logs:** Execution history visible in Functions tab

---

## Next Steps After Enabling

1. ✅ Test manual trigger
2. ✅ Check function logs
3. ✅ Wait for first scheduled run
4. ✅ Verify in OneSignal dashboard that notification was sent
5. ✅ Adjust schedule if needed (edit `netlify.toml` cron expression)

