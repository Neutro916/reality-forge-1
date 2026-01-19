# REALITY FORGE - COMPLETE SETUP GUIDE

## WHAT YOU HAVE NOW

```
apps/528hz-reality-forge/
├── index.html          ← PWA Web App (works NOW in browser)
├── manifest.json       ← PWA manifest
├── sw.js               ← Service worker for offline
├── icons/              ← App icons folder
│   └── icon.svg        ← Base icon (generate others from this)
├── screenshots/        ← For app store (take these yourself)
├── APP_STORE_ASSETS.md ← All text for app store listings
├── CLAUDE.md           ← Developer documentation
├── SETUP_GUIDE.md      ← THIS FILE
└── mobile/             ← React Native project
    ├── package.json
    ├── app.json
    ├── App.tsx
    └── src/
        ├── screens/    ← All 5 screens
        └── stores/     ← State management
```

---

## STEP 1: TEST THE WEB APP NOW (5 minutes)

### On Computer:
1. Open file: `apps/528hz-reality-forge/index.html`
2. Or use a local server:
   ```bash
   cd apps/528hz-reality-forge
   python3 -m http.server 8000
   # Open http://localhost:8000
   ```

### On Phone:
1. Host the files (see Step 2)
2. Visit the URL on your phone
3. Tap "Install App" button or "Add to Home Screen"

---

## STEP 2: HOST AS PWA (Free - 10 minutes)

### Option A: GitHub Pages (Recommended)
1. Go to your repo settings on GitHub
2. Click "Pages" in the sidebar
3. Under "Source" select "Deploy from a branch"
4. Select `main` branch and `/apps/528hz-reality-forge` folder
5. Your app will be live at: `https://[username].github.io/reality-forge-1/apps/528hz-reality-forge`

### Option B: Vercel (Alternative)
1. Go to vercel.com
2. Sign in with GitHub
3. Import your repo
4. Set root directory to `apps/528hz-reality-forge`
5. Deploy

### Option C: Netlify (Alternative)
1. Go to netlify.com
2. Drag the `apps/528hz-reality-forge` folder to the upload area
3. Done - you get a URL instantly

---

## STEP 3: CREATE APP STORE ACCOUNTS

### Google Play Store ($25 one-time)

1. **Go to**: https://play.google.com/console/signup
2. **Sign in** with your Google account
3. **Pay** $25 registration fee
4. **Fill in** developer information:
   - Developer name: "Reality Forge" (or your name)
   - Email: your email
   - Phone: your phone
   - Website: your GitHub repo URL
5. **Verify identity** (required):
   - Upload government ID
   - Verify address
6. **Wait** 2-7 days for approval

### Apple App Store ($99/year)

1. **Go to**: https://developer.apple.com/programs/enroll/
2. **Sign in** with Apple ID (or create one)
3. **Choose** enrollment type:
   - Individual ($99/year)
   - Organization ($99/year, requires D-U-N-S number)
4. **Pay** $99 annual fee
5. **Wait** 24-48 hours for approval

---

## STEP 4: GENERATE APP ICONS

You need icons in multiple sizes. Use the SVG file:

### Using Online Tool (Easiest):
1. Go to: https://www.appicon.co/
2. Upload: `icons/icon.svg`
3. Click "Generate"
4. Download all icons
5. Put them in the `icons/` folder

### Icon Sizes Needed:

**For PWA:**
- 72x72, 96x96, 128x128, 144x144, 152x152, 192x192, 384x384, 512x512

**For Android:**
- 48x48, 72x72, 96x96, 144x144, 192x192, 512x512

**For iOS:**
- 20x20, 29x29, 40x40, 60x60, 76x76, 83.5x83.5, 1024x1024

---

## STEP 5: TAKE SCREENSHOTS

You need 6 screenshots for app stores.

### How to Take Screenshots:

1. Open the web app on your phone (or use browser's phone emulation)
2. Take screenshots of:
   - Home tab (daily greeting, tasks)
   - Breathe tab (during a session)
   - Freestyle tab (7-phase builder)
   - Notes tab (journal)
   - Mind tab (neuro skills)
   - Pattern selection

### Screenshot Sizes:
- **iPhone**: 1290 x 2796 pixels (iPhone 14 Pro Max)
- **Android**: 1080 x 1920 pixels

### Tips:
- Use clean, filled-in data (not empty states)
- Show the app during an active breath session
- Put screenshots in the `screenshots/` folder

---

## STEP 6: SET UP REACT NATIVE (For Native Apps)

### Install Prerequisites:

1. **Node.js** (if not installed):
   - Download from: https://nodejs.org
   - Choose LTS version
   - Install it

2. **Verify installation**:
   ```bash
   node --version   # Should show v18+ or v20+
   npm --version    # Should show 9+ or 10+
   ```

3. **Install Expo CLI**:
   ```bash
   npm install -g expo-cli eas-cli
   ```

4. **Install EAS CLI** (for building):
   ```bash
   npm install -g eas-cli
   ```

### Set Up the Mobile Project:

```bash
# Navigate to mobile folder
cd apps/528hz-reality-forge/mobile

# Install dependencies
npm install

# Start development server
npx expo start

# Scan QR code with Expo Go app on your phone
```

### Create Expo Account:

1. Go to: https://expo.dev/signup
2. Create free account
3. Login in terminal:
   ```bash
   eas login
   ```

---

## STEP 7: BUILD FOR APP STORES

### Build for Android:

```bash
cd apps/528hz-reality-forge/mobile

# Configure EAS
eas build:configure

# Build APK (for testing)
eas build --platform android --profile preview

# Build AAB (for Play Store)
eas build --platform android --profile production
```

### Build for iOS:

```bash
# Build for App Store
eas build --platform ios --profile production

# Note: You need Apple Developer account connected
```

---

## STEP 8: SUBMIT TO STORES

### Google Play Store:

1. Log into Play Console
2. Click "Create app"
3. Fill in:
   - App name: Reality Forge - 528 Hz Breathwork
   - Default language: English
   - App type: App
   - Free or paid: Free
4. Complete all sections:
   - Store listing (use APP_STORE_ASSETS.md)
   - Content rating questionnaire
   - Target audience
   - Privacy policy URL
5. Upload AAB file from EAS build
6. Submit for review

### Apple App Store:

1. Log into App Store Connect
2. Click "+" to create new app
3. Fill in:
   - Platform: iOS
   - Name: Reality Forge - 528 Hz
   - Primary language: English
   - Bundle ID: com.realityforge.breathwork528
   - SKU: realityforge528
4. Complete all sections
5. Upload build via EAS or Transporter app
6. Submit for review

---

## STEP 9: CREATE PRIVACY POLICY

You need a privacy policy URL. Create a simple page:

### Option 1: GitHub Pages
Create file `privacy.html` in your repo with this content:

```html
<!DOCTYPE html>
<html>
<head><title>Privacy Policy</title></head>
<body>
<h1>Reality Forge Privacy Policy</h1>
<p><strong>Data Collection:</strong> None. We do not collect any personal data.</p>
<p><strong>Data Storage:</strong> All data is stored locally on your device only.</p>
<p><strong>Third Parties:</strong> We do not share any data with third parties.</p>
<p><strong>Contact:</strong> [your email]</p>
<p>Last updated: [date]</p>
</body>
</html>
```

### Option 2: Use a Privacy Policy Generator
- https://www.freeprivacypolicy.com
- https://www.privacypolicygenerator.info

---

## TIMELINE ESTIMATE

| Task | Time |
|------|------|
| Test web app | 5 min |
| Host as PWA | 10 min |
| Create Google account | 15 min + 2-7 day wait |
| Create Apple account | 15 min + 24-48 hr wait |
| Generate icons | 10 min |
| Take screenshots | 20 min |
| Set up React Native | 30 min |
| Build apps | 20-40 min |
| Submit to stores | 1-2 hours |
| **Total active time** | **~3-4 hours** |
| **Total with waiting** | **~1 week** |

---

## COST SUMMARY

| Item | Cost |
|------|------|
| Web hosting (GitHub Pages) | FREE |
| Expo account | FREE |
| Google Play Developer | $25 (one-time) |
| Apple Developer | $99/year |
| **Total to publish** | **$124** |

---

## QUICK REFERENCE URLS

- **Google Play Console**: https://play.google.com/console
- **Apple Developer**: https://developer.apple.com
- **Expo**: https://expo.dev
- **App Icon Generator**: https://www.appicon.co
- **Privacy Policy Generator**: https://www.freeprivacypolicy.com

---

## NEED HELP?

1. **Expo Documentation**: https://docs.expo.dev
2. **Google Play Help**: https://support.google.com/googleplay/android-developer
3. **Apple Developer Help**: https://developer.apple.com/support

---

## WHAT'S NEXT?

After publishing App 1 (528 Hz), you can create:
- **App 2**: 373 Hz (Cyan theme)
- **App 3**: 639 Hz (Pink theme)

All three apps will follow the same structure!
