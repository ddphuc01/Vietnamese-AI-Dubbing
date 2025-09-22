# Vietnamese AI Dubbing Frontend

React + TypeScript frontend for Vietnamese AI Dubbing system.

## Features

- 🎨 **Modern UI** - Built with Mantine UI components
- ⚡ **Fast Performance** - React 19 with Vite
- 📱 **Responsive Design** - Works on all devices
- 🌙 **Dark Mode** - Built-in theme switching
- 🔄 **Real-time Updates** - Live progress tracking
- 📁 **File Upload** - Drag & drop video upload
- 🎯 **Job Management** - Track processing jobs
- 📊 **Statistics** - View processing statistics

## Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. **Navigate to frontend directory:**
   ```bash
   cd Vietnamese-AI-Dubbing-UI
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

The application will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Project Structure

```
Vietnamese-AI-Dubbing-UI/
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── Header.tsx
│   │   ├── VideoInput.tsx
│   │   ├── Settings.tsx
│   │   ├── ProgressBar.tsx
│   │   ├── Result.tsx
│   │   ├── VideoPreview.tsx
│   │   ├── TabSelector.tsx
│   │   └── ...
│   ├── pages/            # Page components
│   │   ├── HomePage.tsx
│   │   ├── JobsPage.tsx
│   │   ├── SettingsPage.tsx
│   │   └── AboutPage.tsx
│   ├── api/              # API client
│   │   └── client.ts
│   ├── store/            # State management
│   │   └── useAppStore.ts
│   ├── router/           # React Router config
│   │   └── index.tsx
│   ├── types.ts          # TypeScript types
│   ├── constants.ts      # Application constants
│   ├── App.tsx           # Main app component
│   ├── main.tsx          # App entry point
│   └── ...
├── public/               # Static assets
├── index.html           # HTML template
└── package.json         # Dependencies
```

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

### API Configuration

The frontend connects to the FastAPI backend at:
- **Development:** `http://localhost:8000/api/v1`
- **Production:** Configure via `VITE_API_URL` environment variable

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint (if configured)

### Code Quality

The project uses:
- **TypeScript** - Type checking
- **ESLint** - Code linting
- **Prettier** - Code formatting

### State Management

Uses **Zustand** for global state management:
- Job management
- User authentication
- UI state
- Processing status

## Components

### Core Components

- **Header** - Navigation and user menu
- **VideoInput** - File upload and URL input
- **Settings** - Processing configuration
- **ProgressBar** - Real-time progress tracking
- **Result** - Display processing results
- **TabSelector** - Tab navigation

### Page Components

- **HomePage** - Main video processing interface
- **JobsPage** - Job management and statistics
- **SettingsPage** - Application settings
- **AboutPage** - Project information

## API Integration

The frontend integrates with the FastAPI backend:

### Endpoints Used

- `GET /health` - Health check
- `POST /video/process` - Start video processing
- `GET /video/status/{job_id}` - Get processing status
- `GET /jobs` - List jobs
- `GET /jobs/stats/summary` - Job statistics

### Error Handling

- Network errors
- API errors
- File upload errors
- Processing errors

## Deployment

### Build

```bash
npm run build
```

### Serve

```bash
npm run preview
```

### Docker

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Follow the existing code style
2. Use TypeScript for new components
3. Add proper error handling
4. Write meaningful commit messages
5. Test on multiple browsers

## License

This project is licensed under the MIT License.