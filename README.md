# SafePath SF - Web Deployment Ready

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation
```bash
npm install --legacy-peer-deps
```

### Run Locally
```bash
# Web version
npm run web

# With Expo tunnel (for remote access)
npm run tunnel
```

### 🌐 Web Deployment

#### Deploy to Vercel
1. Connect your GitHub repo to Vercel
2. Select the `James` branch
3. Set build command: `npm run build:web`
4. Set output directory: `web-build`
5. Deploy!

#### Deploy to Netlify
1. Connect GitHub repo
2. Branch: `James`
3. Build command: `expo build:web`
4. Publish directory: `web-build`

### 📱 Mobile Development
```bash
# iOS
npm run ios

# Android  
npm run android
```

## 🛠️ Tech Stack
- **Frontend**: React Native Web + Expo
- **Navigation**: React Navigation
- **Maps**: React Native Maps
- **ML/AI**: Python scripts for safety analysis
- **Data**: San Francisco crime & safety datasets

## 📁 Project Structure
```
safepath-sf/
├── App.tsx                 # Main app component
├── src/
│   ├── screens/           # App screens (Map, Route, Safety, Settings)
│   ├── components/        # Reusable components
│   ├── services/          # ML/AI services
│   └── data/             # Mock data & datasets
├── assets/               # App icons and images
├── data/                 # Crime & safety datasets
└── *.py                  # Python ML scripts
```

## 🔧 Configuration Files
- `package.json` - Dependencies and scripts
- `app.json` - Expo configuration
- `tsconfig.json` - TypeScript settings
- `babel.config.js` - Babel preset for Expo
- `metro.config.js` - Metro bundler optimization
- `webpack.config.js` - Web-specific polyfills

## 🌟 Features
- Real-time safety mapping
- Smart route planning
- Crime data visualization
- ML-powered safety scoring
- Web, iOS, and Android support

## 📝 Environment Variables
Create a `.env` file:
```
GOOGLE_MAPS_API_KEY=your_key_here
DATASF_API_KEY=your_key_here
```

## 🚨 Troubleshooting

### File watching issues on macOS
```bash
brew install watchman
watchman watch-del-all
```

### Clear cache
```bash
npx expo start --clear
```

## 📄 License
MIT

---
Built for AWS Hackathon 2025 🏆