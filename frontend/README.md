# HomzDoctor Frontend

React + TypeScript frontend for the HomzDoctor AI Healthcare Platform.

## Features

- **Patient Portal**: Upload medical data, view reports, chat with AI assistant
- **Doctor Dashboard**: Review AI findings, approve/reject/modify, prescribe medications
- **Pharmacy Interface**: Search pharmacies, check inventory, manage orders
- **Admin Panel**: User management, system monitoring

## Technology Stack

- **Framework**: React 18+
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand / Redux Toolkit
- **API Client**: TanStack Query (React Query) + Axios
- **UI Components**: shadcn/ui
- **Charts**: Recharts / Chart.js
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 18+
- npm 9+ or yarn 1.22+

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Environment Variables

Create a `.env` file:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint issues
- `npm run type-check` - Run TypeScript compiler
- `npm run test` - Run tests
- `npm run test:watch` - Run tests in watch mode

## Project Structure

```src
├── components/        # Reusable UI components
│   ├── ui/           # shadcn/ui components
│   └── common/       # Shared components
├── pages/            # Page components
│   ├── patient/      # Patient-facing pages
│   └── doctor/       # Doctor-facing pages
├── hooks/            # Custom React hooks
├── store/             # State management (Zustand)
├── services/         # API service functions
├── types/            # TypeScript type definitions
├── utils/            # Utility functions
└── tests/            # Test files
```

## API Integration

The frontend uses Axios for API requests and TanStack Query for state management.

Example:

```typescript
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
});

export const useMedicalRecords = () => {
  return useQuery({
    queryKey: ['medical-records'],
    queryFn: async () => {
      const { data } = await api.get('/medical/records');
      return data;
    },
  });
};
```

## Key Components

### Patient Portal

- **UploadScreen**: Medical data upload (images, DICOM, PDFs)
- **ReportsList**: View and manage medical reports
- **ChatInterface**: Interactive AI assistant for Q&A
- **AdherenceTracker**: Medication adherence monitoring

### Doctor Dashboard

- **ReviewQueue**: Pending AI findings for review
- **ReportViewer**: Detailed medical image and report viewer
- **PrescriptionEditor**: Medication prescription interface
- **PatientList**: Managed patients overview

## Authentication

The frontend uses JWT tokens stored in `localStorage`:

- On login: Store token
- On API request: Add `Authorization: Bearer <token>` header
- On logout: Clear token and redirect to login

## Responsive Design

The application is fully responsive with breakpoints:

- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance

- Lazy loading for routes
- Image optimization with Next.js Image
- Code splitting with dynamic imports
- Service worker for offline support

## Testing

This project uses [Vitest](https://vitest.dev/) for unit testing.

```bash
# Run tests
npm run test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details.
