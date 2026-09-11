
## 📦 Step 0: The Universal Setup (Everyone Must Do)

   1. Download Expo Go: Download the free Expo Go app from the App Store onto your physical iPhone.
   2. Determine Your Machine's Local IP Address: Since your mobile app runs on your physical phone, it cannot connect to your backend via localhost (as localhost on the phone means the phone itself). It must call your computer's local IP address.
   * Windows: Open Command Prompt, type ipconfig, and find your IPv4 Address (e.g., 192.168.1.50).
      * Mac: Open Terminal, type ipconfig getifaddr en0, and copy the resulting IP address.
   3. Configure Your Frontend Environment Variables: In your frontend React Native repository, create an .env file (or whatever config file your app uses) and point your API base URLs to your computer's local IP address:
   
   BACKEND_URL=http://192.168.1.50:8000  # Replace with your actual local IP and backend port
   AI_SERVICE_URL=http://192.168.1.50:8001 # Replace with your actual local IP and AI service port
   
   
------------------------------
## 🪟 Step-by-Step for Windows Developers
Windows developers will spin up all three services locally and stream the frontend directly to their physical iPhone.

   1. Network Check: Ensure your Windows PC and your iPhone are connected to the exact same Wi-Fi network.
   2. Start the Backend and AI Services:
   * Open your Backend repo in a VS Code window and run your start command python -m app.main (or python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload)
      * Open your AI-Service repo in another VS Code window and spin it up. Make sure both are configured to accept connections from your local network (e.g., binding to host 0.0.0.0 if necessary). python main.py (or python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload)
   3. Open the Frontend Project: Open your Frontend React Native repository in VS Code.
   4. Install Dependencies: Open the built-in VS Code terminal and run:
   
   npm install
   
   (Or yarn install / pnpm install depending on what package manager your frontend uses).
   5. Start Expo: In your frontend terminal, run:
   
   npx expo start
   
   6. Scan the QR Code: A large QR code will appear inside your VS Code terminal.
   * Open the native Camera app on your iPhone.
      * Scan the QR code on your screen and tap "Open in Expo Go".
   7. Test & Live-Edit: The frontend app will load on your iPhone and successfully make API requests to your local backend and AI service repos. Every time you save changes in your frontend VS Code window, your phone screen will update instantly!

💡 Windows Firewall Quick-Fix: If your phone opens the app but cannot connect to your backend or AI service, Windows Firewall is likely blocking incoming local traffic. To bypass this quickly without messing with firewall settings, run your frontend using a secure cloud tunnel:

npx expo start --tunnel

------------------------------
## 🍎 Step-by-Step for Mac Developers
Mac developers have the option to test on their physical iPhone or use the on-screen macOS iOS Simulator while running the other services.
## Method A: Testing on a Physical iPhone (Same as Windows)

   1. Network Check: Connect your Mac and your iPhone to the same Wi-Fi network.
   2. Start Backend & AI Services: Open their respective repositories in VS Code and turn them on.
   3. Open Frontend Project: Launch your frontend repo in VS Code and install packages: npm install.
   4. Start Expo: Run npx expo start in your frontend terminal.
   5. Scan the QR Code: Open your iPhone’s Camera app, scan the QR code in the terminal, and tap "Open in Expo Go".

## Method B: Testing on the macOS Virtual Simulator
If a Mac developer prefers to test directly on their computer screen without picking up their phone:

   1. Ensure Xcode is installed from the Mac App Store. Open it once, navigate to Settings > Platforms, and ensure an iOS Simulator version is fully downloaded.
   2. Start your Backend and AI Service repos locally in VS Code.
   3. Open your Frontend repo in VS Code, open the terminal, and run:
   
   npx expo start
   
   4. Once the server starts up, simply press the i key on your keyboard. Expo will automatically launch the Mac's virtual iPhone simulator on your desktop and open your frontend app inside it.
   (Bonus: Since the simulator runs on the exact same computer as your services, it can safely use http://localhost or your local IP address to talk to the backend/AI repos).