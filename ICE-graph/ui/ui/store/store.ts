import { configureStore } from '@reduxjs/toolkit';
import memoriesReducer from './memoriesSlice';
import profileReducer from './profileSlice';
import appsReducer from './appsSlice';
import uiReducer from './uiSlice';
import filtersReducer from './filtersSlice';
import configReducer from './configSlice';

export const makeStore = () => {
  return configureStore({
    reducer: {
      memories: memoriesReducer,
      profile: profileReducer,
      apps: appsReducer,
      ui: uiReducer,
      filters: filtersReducer,
      config: configReducer,
    },
  });
};

// Create store instance for compatibility
export const store = makeStore();

// Infer the `RootState` and `AppDispatch` types from the store itself
export type AppStore = ReturnType<typeof makeStore>;
export type RootState = ReturnType<AppStore['getState']>;
export type AppDispatch = AppStore['dispatch']; 