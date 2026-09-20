# HealthTwin Mobile

Professional React Native app built with Expo, React Navigation, Zustand, and Flask API integration.

## Step 1: Best approach selection

- Selected approach: **Full React Native app**
- Reason:
  - Better performance, native UX, push notifications, offline handling, device APIs
  - Scalable architecture for long-term product growth
  - WebView is faster initially but poor for maintainability and native interactions

## Step 2: Project setup commands

From project root:

```powershell
cd C:\Users\preet\OneDrive\Desktop\healthtwin
.\venv\Scripts\python.exe run.py
```

From mobile folder:

```powershell
cd C:\Users\preet\OneDrive\Desktop\healthtwin\healthtwin-mobile
npm install
npx expo start
```

## Step 3: Folder structure

```text
healthtwin-mobile/
  App.js
  app.json
  eas.json
  src/
    components/
      AppButton.js
      AppInput.js
      Card.js
      MetricCard.js
    hooks/
      useNetworkStatus.js
    navigation/
      RootNavigator.js
      AuthNavigator.js
      AppTabs.js
    screens/
      auth/
        LoginScreen.js
        SignupScreen.js
      app/
        DashboardScreen.js
        PredictionsScreen.js
        ChatScreen.js
        HistoryScreen.js
        SettingsScreen.js
    services/
      api/
        client.js
        authApi.js
        healthApi.js
    store/
      authStore.js
      configStore.js
    theme/
      palette.js
```

## Step 4: Core screens included

- Login / Signup with Flask mobile auth APIs
- Dashboard (Analyze, Save Log, Watch snapshot)
- Predictions (Diabetes + Heart)
- AI Chat (advisor endpoint)
- History (pull-to-refresh)
- Settings (backend URL switch, connection status, logout)

## Step 5: API integration

Mobile API endpoints:

- `POST /api/mobile/auth/register`
- `POST /api/mobile/auth/login`
- `GET /api/mobile/auth/me`
- `POST /api/mobile/auth/logout`
- `POST /api/analyze`
- `POST /api/save_log`
- `GET /api/history`
- `GET /api/watch`
- `POST /api/advisor`
- `POST /api/predict/diabetes`
- `POST /api/predict/heart`

## Step 6: Build APK

One-time setup:

```powershell
npm install -g eas-cli
eas login
```

Build preview APK:

```powershell
cd C:\Users\preet\OneDrive\Desktop\healthtwin\healthtwin-mobile
eas build -p android --profile preview
```

## Notes

- Android emulator default API URL is `http://10.0.2.2:5000`
- On real device, set backend URL in Settings to your laptop LAN IP, e.g. `http://192.168.1.10:5000`
- Flask app now returns JSON `401` for `/api/*` unauthenticated calls, so mobile error handling works correctly
