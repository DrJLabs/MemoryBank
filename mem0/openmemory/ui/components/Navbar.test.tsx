import React from 'react';
import { render, screen } from '@testing-library/react';
import { configureStore } from '@reduxjs/toolkit';
import { Provider } from 'react-redux';
import { Navbar } from './Navbar';
import '@testing-library/jest-dom';

// Mock child components that are not relevant to this test
jest.mock('@/app/memories/components/CreateMemoryDialog', () => ({
  CreateMemoryDialog: () => <div>CreateMemoryDialog Mock</div>,
}));

// Mock Redux slices
const mockProfileSlice = {
  name: 'profile',
  initialState: { userId: 'test-user', user: { id: 'test-user', name: 'Test User' } },
  reducers: {},
};
const mockMemoriesSlice = {
    name: 'memories',
    initialState: { memories: [], selectedMemory: null },
    reducers: {},
};

// Create a mock store for testing
const mockStore = configureStore({
  reducer: {
    profile: (state = mockProfileSlice.initialState) => state,
    memories: (state = mockMemoriesSlice.initialState) => state,
  },
});

// Mock hooks
jest.mock('next/navigation', () => ({
  usePathname: () => '/',
}));
jest.mock('next-themes', () => ({
  useTheme: () => ({ setTheme: jest.fn(), theme: 'light' }),
}));
jest.mock('@/hooks/useMemoriesApi', () => ({
    useMemoriesApi: () => ({
        memories: [],
        loading: false,
        error: null,
        hasUpdates: 0,
        createMemory: jest.fn(),
        updateMemory: jest.fn(),
        deleteMemory: jest.fn(),
    })
}));
jest.mock('@/hooks/useAppsApi', () => ({
    useAppsApi: () => ({
        apps: [],
        loading: false,
        error: null,
    })
}));
jest.mock('@/hooks/useStats', () => ({
    useStats: () => ({
        stats: {},
        loading: false,
        error: null,
    })
}));
jest.mock('@/hooks/useConfig', () => ({
    useConfig: () => ({
        config: {},
        loading: false,
        error: null,
    })
}));


const renderWithProviders = (ui, { store = mockStore, ...renderOptions } = {}) => {
  function Wrapper({ children }) {
    return <Provider store={store}>{children}</Provider>;
  }
  return render(ui, { wrapper: Wrapper, ...renderOptions });
};

describe('Navbar Component', () => {
  it('renders the navbar with navigation links', () => {
    renderWithProviders(<Navbar />);
    
    // Check for the presence of the main header element (which has a 'banner' role)
    const navElement = screen.getByRole('banner');
    expect(navElement).toBeInTheDocument();

    // Check for a specific link
    const dashboardLink = screen.getByRole('link', { name: /dashboard/i });
    expect(dashboardLink).toBeInTheDocument();
    expect(dashboardLink).toHaveAttribute('href', '/');
  });
}); 