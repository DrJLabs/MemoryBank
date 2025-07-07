"use client";

import { StoreProvider } from "../store/providers";

export function Providers({ children }: { children: React.ReactNode }) {
  return <StoreProvider>{children}</StoreProvider>;
}
