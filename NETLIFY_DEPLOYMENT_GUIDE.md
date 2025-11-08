# OneSignal Push Notification - Netlify Deployment Guide

## 🚀 Quick Deployment Steps

### Option 1: Deploy via Git (Recommended)

1. **Push code to GitHub/GitLab**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - OneSignal Netlify Functions"
   git branch -M main
   git remote add origin YOUR_REPO_URL
   git push -u origin main
   ```

2. **Connect to Netlify**
   - Go to [Netlify](https://app.netlify.com/)
   - Click "Add new site" → "Import an existing project"
   - Connect your Git provider (GitHub/GitLab/Bitbucket)
   - Select your repository
   - Netlify auto-detects `netlify.toml` settings
   - Click "Deploy site"

3. **Configure Environment Variables**
   - In Netlify dashboard, go to: **Site settings** → **Environment variables**
   - Add these variables:
     ```
     ONESIGNAL_APP_ID = 9c2479b0-028d-4467-bc12-d1609b7d2879
     ONESIGNAL_REST_API_KEY = NDNjM2Y0ZjUtMGVkYS00MjliLWFmOWUtNGE2NjUwMTE4NTBh
     WORDPRESS_SITE_URL = https://ccodelearner.com
     ```

4. **Enable Scheduled Functions**
   - In Netlify dashboard, go to: **Site settings** → **Functions** → **Scheduled functions**
   - Enable scheduled functions
   - The function will run daily at 9:00 AM UTC (configured in netlify.toml)

### Option 2: Deploy via Netlify Drop (Drag & Drop)

1. **Create a ZIP file**
   - Compress these files/folders into a ZIP:
     - `netlify.toml`
     - `netlify/` folder
     - `package.json`

2. **Upload to Netlify**
   - Go to [Netlify Drop](https://app.netlify.com/drop)
   - Drag and drop your ZIP file
   - Wait for deployment

3. **Configure Environment Variables** (same as Option 1, step 3)

4. **Enable Scheduled Functions** (same as Option 1, step 4)

---

## 📅 Schedule Configuration

The notification schedule is configured in `netlify.toml`:

```toml
[[functions."send-notification".schedule]]
  cron = "0 9 * * *"  # Daily at 9:00 AM UTC
```

### Common Schedule Examples:

| Schedule | Cron Expression | Description |
|----------|----------------|-------------|
| Every 15 mins (testing) | `*/15 * * * *` | Good for testing |
| Hourly | `0 * * * *` | Every hour |
| Every 6 hours | `0 */6 * * *` | 4 times per day |
| Daily at 9 AM UTC | `0 9 * * *` | Once per day |
| Daily at 3 PM UTC | `0 15 * * *` | Once per day |
| Twice daily | `0 9,21 * * *` | 9 AM and 9 PM UTC |

**Cron Format:** `minute hour day month day-of-week`

---

## 🧪 Testing Your Function

### Method 1: Manual Trigger via URL

Once deployed, test immediately using the manual trigger endpoint:

```bash
https://YOUR-SITE-NAME.netlify.app/.netlify/functions/manual-trigger
```

Just visit this URL in your browser to send a test notification.

### Method 2: Netlify Functions Dashboard

1. Go to **Functions** tab in Netlify dashboard
2. Click on `send-notification` function
3. View logs to see execution history

### Method 3: Check Logs

- In Netlify dashboard: **Functions** → **send-notification** → **Function logs**
- You'll see:
  - When function runs
  - Which post was selected
  - Notification send status
  - Recipient count

---

## 🔒 Security Notes

✅ **Secure:**
- API keys stored in Netlify environment variables (never in code)
- Not visible in browser or frontend
- Only server-side functions can access them

⚠️ **Important:**
- Never commit `.env` files with real API keys
- Never expose keys in frontend JavaScript
- Netlify environment variables are encrypted

---

## 📊 Monitoring

### Check if scheduled function is working:

1. **Netlify Dashboard**
   - Functions → send-notification → Logs
   - You'll see execution history

2. **OneSignal Dashboard**
   - Go to [OneSignal Dashboard](https://app.onesignal.com/)
   - Check "Messages" tab for sent notifications

3. **Email Notifications**
   - Netlify can email you about function failures
   - Configure in: Site settings → Functions → Notifications

---

## 🐛 Troubleshooting

### Function not running on schedule?

1. **Check if scheduled functions are enabled:**
   - Site settings → Functions → Enable scheduled functions

2. **Verify environment variables:**
   - Site settings → Environment variables
   - All three variables must be set

3. **Check function logs:**
   - Functions tab → send-notification → Logs
   - Look for error messages

### No subscribers receiving notifications?

- Recipient count showing 0 is normal if no one has subscribed yet
- Test with OneSignal test device:
  - Install OneSignal SDK on a test website
  - Subscribe to notifications
  - Run manual trigger to test

### Common Errors:

**"OneSignal credentials not configured"**
- Solution: Add environment variables in Netlify dashboard

**"Failed to fetch posts"**
- Solution: Check WORDPRESS_SITE_URL is correct
- Verify WordPress REST API is accessible

**"Function timeout"**
- Solution: Netlify functions have 10-second limit on free tier
- Should be sufficient for this use case

---

## 💰 Pricing

**Netlify Free Tier includes:**
- ✅ Scheduled functions
- ✅ 125K function requests/month
- ✅ 100 hours compute time/month
- ✅ More than enough for daily notifications

**For this use case:**
- Daily notification = 30 requests/month
- Well within free tier limits ✅

---

## 📝 File Structure

```
.
├── netlify.toml                          # Netlify configuration
├── package.json                          # Dependencies
├── netlify/
│   └── functions/
│       ├── send-notification.js          # Main scheduled function
│       └── manual-trigger.js             # Manual test endpoint
└── NETLIFY_DEPLOYMENT_GUIDE.md           # This file
```

---

## 🎯 Next Steps

1. ✅ Deploy to Netlify
2. ✅ Set environment variables
3. ✅ Enable scheduled functions
4. ✅ Test with manual trigger
5. ✅ Monitor logs for first scheduled run
6. ✅ Adjust schedule if needed (edit netlify.toml)

---

## 📚 Resources

- [Netlify Functions Documentation](https://docs.netlify.com/functions/overview/)
- [Netlify Scheduled Functions](https://docs.netlify.com/functions/scheduled-functions/)
- [OneSignal REST API](https://documentation.onesignal.com/reference/create-notification)
- [WordPress REST API](https://developer.wordpress.org/rest-api/)
- [Cron Expression Generator](https://crontab.guru/)

---

## ✅ Success!

Once deployed, your WordPress posts will automatically be sent as push notifications to your OneSignal subscribers every day at 9:00 AM UTC! 🎉