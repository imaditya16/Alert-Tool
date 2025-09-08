# 🚀 **Microsoft Teams Webhook Setup Guide**

## 📋 **What You Need:**
- Microsoft Teams account (personal or work)
- Access to a Teams channel where you want to receive notifications

## 🔧 **Step-by-Step Setup:**

### **Step 1: Create Teams Webhook**
1. **Open Microsoft Teams**
2. **Go to your desired channel** (e.g., #alerts, #monitoring, #database)
3. **Click the "..." (three dots) next to the channel name**
4. **Select "Connectors"**
5. **Find "Incoming Webhook" and click "Configure"**
6. **Give it a name** (e.g., "Database Monitor")
7. **Upload an icon** (optional - database icon recommended)
8. **Click "Create"**

### **Step 2: Copy the Webhook URL**
- **Copy the webhook URL** that Teams generates
- **It looks like:** `https://yourcompany.webhook.office.com/webhookb2/...`
- **Keep this URL secure** - anyone with it can post to your channel

### **Step 3: Update Your Configuration**
1. **Open your `config.env` file**
2. **Replace `YOUR_TEAMS_WEBHOOK_URL_HERE` with your actual webhook URL**
3. **Save the file**

### **Step 4: Test the Webhook**
```bash
python -c "from app.teams_notifier import send_teams_notification; import asyncio; asyncio.run(send_teams_notification('Test Alert', 'Testing Teams webhook connection'))"
```

## 🎯 **What You'll See in Teams:**

### **Inactivity Alert:**
- ⚠️ **Red warning card** with database icon
- **Detailed information** about the inactivity
- **Clickable button** to check database status
- **Timestamp** and threshold information

### **Activity Resumed:**
- 🟢 **Green success card** when database becomes active again

## 🔒 **Security Best Practices:**
1. **Keep webhook URLs private** - don't share them publicly
2. **Use dedicated channels** for monitoring alerts
3. **Regularly rotate webhook URLs** if possible
4. **Monitor webhook usage** for any unauthorized posts

## 🚨 **Troubleshooting:**

### **Webhook Not Working?**
1. **Check the URL** - make sure it's copied correctly
2. **Verify channel permissions** - you need to be a member
3. **Test with a simple message** first
4. **Check Teams status** - sometimes Teams has outages

### **Notifications Too Frequent?**
1. **Adjust `INACTIVITY_THRESHOLD_MINUTES`** in your config
2. **Adjust `ALERT_COOLDOWN_MINUTES`** to reduce frequency
3. **Use Teams channel settings** to mute if needed

## 📱 **Mobile Notifications:**
- **Enable Teams mobile app** to get push notifications
- **Set notification preferences** for the monitoring channel
- **Get instant alerts** even when away from your computer

## 🎉 **Benefits of Teams vs Email:**
- ✅ **More reliable** - no SMTP authentication issues
- ✅ **Instant delivery** - real-time notifications
- ✅ **Rich formatting** - cards with buttons and images
- ✅ **Mobile friendly** - push notifications on phone
- ✅ **Team collaboration** - everyone can see alerts
- ✅ **No password management** - just webhook URL

---

**Your database monitor will now send beautiful Teams notifications instead of email alerts!** 🎯
