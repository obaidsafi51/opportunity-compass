import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Global API_BASE resolved dynamically through Vite environment variables.
// Fallback logic keeps proxy intact manually without breaking existing proxy devs
// Strip trailing slash to prevent double-slash URLs (e.g., "//api/skills")
export const API_BASE = (import.meta.env.VITE_API_URL || "").replace(/\/+$/, "");
