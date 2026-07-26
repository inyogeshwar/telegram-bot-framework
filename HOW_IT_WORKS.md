# GEOTAGP FAST HITS - How It Works

## 📋 Overview
This script scans Instagram user IDs to find accounts with available Gmail/AOL email addresses. It's a multi-threaded tool that checks millions of Instagram accounts and identifies "hits" where the email can be registered.

## 🎯 What It Does

### Main Workflow:
1. **Generate Instagram User IDs** - Creates random user IDs based on year ranges (2010-2025)
2. **Fetch Profile** - Uses Instagram's GraphQL API to get user details (username, followers, etc.)
3. **Check Email on Instagram** - Verifies if the email is already registered on Instagram
4. **Check Email Availability** - Checks if the email is available on Gmail/AOL
5. **Save Hits** - If email exists on Instagram AND is available on Gmail → HIT!

## 🔑 Key Components

### 1. Instagram Profile Fetcher
- **Endpoint**: `https://www.instagram.com/api/graphql`
- **Method**: GraphQL query with user ID
- **Returns**: Username, followers, following, posts, bio, verification status
- **Speed**: ~100-200ms per request

### 2. Instagram Email Checker (lookup_instagram)
- **Endpoint**: `https://www.instagram.com/accounts/password/reset/`
- **Purpose**: Check if email exists on Instagram
- **How it works**:
  1. Visits password reset page
  2. Extracts tokens (LSD, WebBloksVersioningID, server_revision)
  3. Sends bloks fetch request with email
  4. Parses response for account existence
- **Speed**: 3-6 seconds per check

### 3. Gmail Availability Checker (check_gmail)
- **Endpoint**: `https://accounts.google.com/_/signup/usernameavailability`
- **Purpose**: Check if Gmail address is available for registration
- **How it works**:
  1. Uses Google's signup API
  2. Sends username availability request
  3. Checks response for "available" or "taken"
- **Speed**: ~500ms per check

### 4. AOL Email Checker (check_aol_email)
- **Endpoint**: `https://i.instagram.com/api/v1/users/check_email/`
- **Purpose**: Check if AOL email is available on Instagram
- **How it works**:
  1. Uses Instagram's mobile API
  2. Checks if email can be registered
- **Speed**: ~1 second per check

## 📊 Hit Classification

### GOOD HIT ✅
- Email exists on Instagram
- Email is available on Gmail/AOL
- **Action**: Save to hits.txt and send to Telegram

### TAKEN ⚠️
- Email exists on Instagram
- Email is NOT available on Gmail/AOL
- **Action**: Log as taken (someone has this email)

### BAD ❌
- Email doesn't exist on Instagram
- **Action**: Skip and continue scanning

## 🚀 Performance

### Multi-Threading
- Uses ThreadPoolExecutor with 150 threads (default)
- Each thread independently scans profiles
- Shared statistics with thread-safe locking

### Speed Estimates
- **Profile fetch**: ~100ms
- **Instagram email check**: ~4 seconds
- **Gmail check**: ~500ms
- **Total per user**: ~5 seconds
- **With 150 threads**: ~750 users/second theoretical max

### Realistic Performance
- Instagram rate limiting: ~30-50 requests/second
- Google rate limiting: ~10-20 requests/second
- **Realistic speed**: 100-300 scans/minute

## 🎨 Features

### Stylish Console Output
- Color-coded statistics (HITS, GOOD, BAD, TAKEN, SCANNED)
- Pixel-style hit boxes
- Real-time updates every 1.5 seconds

### Telegram Integration
- Sends hits to Telegram bot
- Includes profile link, stats, and user info
- Inline keyboard for quick actions

### Smart Filtering
- **Year range**: Filter by account creation year (2010-2025)
- **Min followers**: Only check accounts with X+ followers
- **Domain filter**: Gmail only, AOL only, or all domains

### Auto Token Management
- Automatically generates Google tokens
- Regenerates tokens when expired
- Caches tokens to file (gmail_token.txt)

## 🔧 Technical Details

### Instagram User ID Structure
Instagram user IDs are sequential numbers that can be estimated by year:
- 2010: 1 - 5,000,000
- 2011: 5,000,001 - 17,750,000
- 2012: 17,750,001 - 279,760,000
- ...and so on

### Token Extraction
The script extracts these tokens from Instagram's password reset page:
- **LSD**: Login session token
- **WebBloksVersioningID**: Bloks framework version (replaces old BKV token)
- **server_revision**: Server version number
- **__dyn, __csr, __hs, __hsi, __s**: Instagram internal parameters

### Request Headers
Uses realistic browser headers:
- Android Chrome user agent
- Proper sec-ch-ua headers
- Correct origin and referer headers
- Mimics real browser behavior

## 📁 File Structure

```
geotagp_final_working.py  - Main script
hits.txt                  - Output file with all hits
gmail_token.txt          - Cached Google authentication token
```

## ⚙️ Configuration

### Required Inputs
1. **Telegram Bot Token** - From @BotFather
2. **Telegram Chat ID** - Your chat/channel ID
3. **Domain Filter** - Gmail/AOL/All
4. **Min Followers** - Minimum follower count (0 = all)
5. **Year Range** - Account creation years (e.g., 2013-2021)
6. **Thread Count** - Number of worker threads (default: 150)

### Example Configuration
```
Bot Token: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz
Chat ID: -1001234567890
Domain: Gmail only
Min Followers: 1000
Year Range: 2015-2023
Threads: 150
```

## 🛡️ Safety Features

### Rate Limiting
- Random delays between requests (10-30ms)
- Automatic retry on 429 (rate limit) errors
- Session rotation to avoid blocks

### Error Handling
- Try-except blocks on all network requests
- Graceful fallbacks for missing tokens
- Continues scanning even if individual checks fail

### Session Management
- Separate sessions for Instagram and Google
- Cookie persistence for Google authentication
- Automatic token regeneration

## 🎓 How to Use

### 1. Install Dependencies
```bash
pip install requests httpx colorama
```

### 2. Get Telegram Credentials
1. Message @BotFather on Telegram
2. Create new bot with `/newbot`
3. Copy the bot token
4. Message @userinfobot to get your Chat ID
5. Add bot to your channel as admin

### 3. Run the Script
```bash
python geotagp_final_working.py
```

### 4. Enter Configuration
- Paste Telegram bot token
- Paste Telegram chat ID
- Select domain filter (1-3)
- Enter minimum followers
- Enter year range
- Enter thread count

### 5. Monitor Hits
- Watch the console for real-time stats
- Check hits.txt for saved hits
- Receive Telegram notifications for each hit

## 🔍 Example Output

```
╔══════════════════════════════════╗
║  🔥 HIT #42  🔥                 ║
║  Channel: @geotagp | Owner: @geotagpy ║
║                                  ║
║  USERNAME  → @johndoe           ║
║  EMAIL     → johndoe@gmail.com  ║
║  FOLLOWERS → 15,234             ║
║  YEAR      → 2019               ║
╚══════════════════════════════════╝
```

## ⚠️ Important Notes

### Legal & Ethical
- This tool is for educational purposes only
- Respect Instagram's Terms of Service
- Don't abuse the API (use reasonable thread counts)
- Don't spam or harass users

### Limitations
- Instagram may block IPs with high request rates
- Google may rate-limit email checks
- Not all emails will be available (most are taken)
- Requires valid Instagram session cookies

### Maintenance
- Instagram changes their API frequently
- Tokens may need updates every few weeks
- User agents may need rotation
- Check for updates regularly

## 🐛 Troubleshooting

### No hits found
- Increase thread count
- Widen year range
- Lower minimum followers
- Check if gmail_token.txt exists

### Rate limited
- Reduce thread count
- Add more delays
- Use proxy rotation

### Token errors
- Delete gmail_token.txt and restart
- Check internet connection
- Verify Google services are accessible

## 📞 Support
- Channel: https://t.me/geotagp
- Owner: https://t.me/geotagpy