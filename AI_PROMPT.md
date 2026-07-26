# AI Prompt - Create Instagram Email Scanner

## Prompt for AI (Copy and paste this to any AI to recreate the script)

```
Create a Python script called "geotagp_final_working.py" that scans Instagram user IDs to find accounts with available Gmail/AOL email addresses.

## Main Features:
1. Multi-threaded Instagram profile scanner (150 threads default)
2. Checks if email exists on Instagram using password reset flow
3. Checks if Gmail/AOL email is available for registration
4. Saves "hits" to hits.txt and sends to Telegram
5. Stylish console output with colors and boxes
6. Real-time statistics display

## Technical Requirements:

### Dependencies:
- requests
- httpx
- colorama
- threading
- concurrent.futures

### Instagram Integration:
1. **Profile Fetching**: Use GraphQL endpoint `https://www.instagram.com/api/graphql`
   - Query: PolarisProfilePageContentQuery
   - Returns: username, followers, following, posts, bio, verification status
   
2. **Email Existence Check**: Use password reset flow
   - Visit: `https://www.instagram.com/accounts/password/reset/`
   - Extract tokens: LSD, WebBloksVersioningID (from "versioningID":"[hex]"), server_revision
   - POST to: `https://www.instagram.com/async/wbloks/fetch/`
   - Check response for: 'com.bloks.www.caa.ar.auth_method' (means email exists)
   - Use Android Chrome user agent: "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36"

### Gmail Integration:
1. **Token Generation**: 
   - Visit: `https://accounts.google.com/signin/v2/usernamerecovery`
   - Extract TL token from page
   - Save to gmail_token.txt as "TL//HOST" format

2. **Email Availability Check**:
   - POST to: `https://accounts.google.com/_/signup/usernameavailability`
   - Check for '"gf.uar",1' (available) or '"gf.uar",0' (taken)
   - Use cookies: {'__Host-GAPS': host}

### AOL Integration:
- POST to: `https://i.instagram.com/api/v1/users/check_email/`
- Check for "allow_shared_email_registration": true
- Use Instagram mobile user agent

### User ID Ranges by Year:
```python
ALL_YEAR_RANGES = [
    (1, 5000000, 2010), (5000001, 17750000, 2011), (17750001, 279760000, 2012),
    (279760001, 900990000, 2013), (900990001, 1629010000, 2014),
    (1629010001, 2369359761, 2015), (2369359762, 4239516754, 2016),
    (4239516755, 6345108209, 2017), (6345108210, 10016232395, 2018),
    (10016232396, 27238602159, 2019), (27238602160, 35855338063, 2020),
    (35855338064, 43464475395, 2021), (43464475395, 50289297647, 2022),
    (50289297647, 57464707082, 2023), (57464707082, 63313426938, 2024),
    (63313426938, 70134323896, 2025)
]
```

### Console Output:
- Use colorama for colors (R, G, Y, C, M, W, RESET)
- Create stylish boxes with Unicode characters
- Display: HITS, GOOD, BAD, TAKEN, SCANNED, ERRORS
- Update every 1.5 seconds

### Telegram Integration:
- Send hits via Telegram Bot API
- Format: HTML with inline keyboard
- Include: username, email, followers, year, profile link

### Main Workflow:
1. Get user inputs: Bot token, Chat ID, domain filter, min followers, year range, threads
2. Setup Instagram session with cookies
3. Generate Google token
4. Start worker threads
5. Each worker:
   - Pick random user ID from year range
   - Fetch profile via GraphQL
   - Check if email exists on Instagram
   - Check if email is available on Gmail/AOL
   - If both conditions met → HIT!
   - Save to file and send to Telegram
6. Display real-time stats

### Hit Classification:
- **GOOD**: Email exists on Instagram + Available on Gmail/AOL → Save & Notify
- **TAKEN**: Email exists on Instagram + Not available on Gmail/AOL → Log only
- **BAD**: Email doesn't exist on Instagram → Skip

### Important Notes:
- Use ThreadPoolExecutor for multi-threading
- Use threading.Lock for shared statistics
- Add random delays (10-30ms) to avoid rate limits
- Handle 429 errors with retry logic
- Extract WebBloksVersioningID using regex: r'"versioningID":"([a-f0-9]{40,})"'
- Fallback to old BKV format if needed: r'__bkv=([a-f0-9]{40,})'
- Double-wrap params payload: {'params': json.dumps({"params": json.dumps(params_payload)})}

### File Output:
- hits.txt: Append each hit with timestamp, username, user_id, year, email, stats

### Example Console Output:
```
╔══════════════════════════════════╗
║  🔥 HIT #42  🔥                 ║
║  Channel: @geotagp dm  @geotagpy ║
║                                  ║
║  USERNAME  → @johndoe            ║
║  EMAIL     → johndoe@gmail.com   ║
║  FOLLOWERS → 15,234              ║
║  YEAR      → 2019                ║
╚══════════════════════════════════╝
```

Make it clean, simple, well-commented, and fully functional. Include error handling and make it production-ready.
```

## How to Use This Prompt:
1. Copy the entire prompt above
2. Paste it into any AI (Claude, ChatGPT, Gemini, etc.)
3. The AI will generate the complete working script
4. Save the output as `geotagp_final_working.py`
5. Install dependencies: `pip install requests httpx colorama`
6. Run: `python geotagp_final_working.py`

## What You'll Get:
- Complete working Python script
- Instagram email checking functionality
- Gmail availability checking
- AOL email checking
- Multi-threaded scanning
- Telegram notifications
- Stylish console output
- All features described in HOW_IT_WORKS.md

## Notes:
- The script requires valid Instagram session cookies (hardcoded in setup_session)
- You need a Telegram bot token and chat ID
- Google token is auto-generated on first run
- Adjust thread count based on your system and rate limits