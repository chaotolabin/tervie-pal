import { useState, useEffect, useCallback, useRef } from 'react';
import { getLocalDateString, getDaysAgoDateString } from '../utils/dateUtils';

interface UseDateParamOptions {
  /**
   * Whether URL synchronization should be active.
   * Only set to true for routes that need date in URL (e.g., /nutrition, /exercise)
   */
  enabled: boolean;
  /**
   * Initial date value if not found in URL
   */
  defaultDate?: string;
}

interface UseDateParamReturn {
  date: string;
  setDate: (newDate: string) => void;
  /**
   * Update URL with new date (only if enabled)
   */
  updateUrlDate: (newDate: string) => void;
}

/**
 * Custom hook for managing date state with optional URL synchronization.
 * Only syncs with URL when `enabled` is true (for specific routes like /nutrition, /exercise).
 * 
 * @param options - Configuration options
 * @returns Date state and update functions
 */
export function useDateParam(options: UseDateParamOptions): UseDateParamReturn {
  const { enabled, defaultDate } = options;
  const isMountedRef = useRef(true);

  // Initialize date from URL query params (if enabled) or use default
  const getInitialDate = (): string => {
    if (enabled) {
      const urlParams = new URLSearchParams(window.location.search);
      const dateParam = urlParams.get('date');
      if (dateParam) {
        // Validate date format (YYYY-MM-DD)
        const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
        if (dateRegex.test(dateParam)) {
          return dateParam;
        }
      }
    }
    return defaultDate || getLocalDateString();
  };

  const [date, setDateState] = useState(getInitialDate());

  // Update URL query parameter without page reload (only if enabled)
  const updateUrlDate = useCallback((newDate: string) => {
    if (!enabled) {
      // If URL sync is disabled, just update state
      setDateState(newDate);
      return;
    }

    const url = new URL(window.location.href);
    url.searchParams.set('date', newDate);
    // Use replaceState to avoid adding to history
    window.history.replaceState(
      { ...window.history.state, date: newDate },
      '',
      url.toString()
    );
    setDateState(newDate);
  }, [enabled]);

  // Clean up date param from URL on unmount (when component using this hook unmounts)
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
      // Cleanup on unmount - remove date param when component unmounts
      // This ensures date param is removed when navigating away from nutrition/exercise pages
      if (enabled) {
        const url = new URL(window.location.href);
        if (url.searchParams.has('date')) {
          url.searchParams.delete('date');
          window.history.replaceState(
            { ...window.history.state },
            '',
            url.toString()
          );
        }
      }
    };
  }, [enabled]); // Run cleanup when enabled changes or on unmount

  // Clean up date param from URL when disabled
  useEffect(() => {
    if (!enabled) {
      const url = new URL(window.location.href);
      if (url.searchParams.has('date')) {
        url.searchParams.delete('date');
        window.history.replaceState(
          { ...window.history.state },
          '',
          url.toString()
        );
      }
    }
  }, [enabled]);

  // Sync date with URL when it changes (only if enabled)
  useEffect(() => {
    if (enabled) {
      const url = new URL(window.location.href);
      const currentUrlDate = url.searchParams.get('date');
      
      // Only update URL if date state differs from URL
      if (currentUrlDate !== date) {
        url.searchParams.set('date', date);
        window.history.replaceState(
          { ...window.history.state, date },
          '',
          url.toString()
        );
      }
    }
  }, [date, enabled]);

  // Listen to browser back/forward navigation (only if enabled)
  useEffect(() => {
    if (!enabled) return;

    const handlePopState = () => {
      const urlParams = new URLSearchParams(window.location.search);
      const dateParam = urlParams.get('date');
      if (dateParam) {
        const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
        if (dateRegex.test(dateParam) && dateParam !== date) {
          setDateState(dateParam);
        }
      } else {
        // If no date param, default to today
        const today = getLocalDateString();
        if (today !== date) {
          setDateState(today);
        }
      }
    };

    window.addEventListener('popstate', handlePopState);
    return () => {
      window.removeEventListener('popstate', handlePopState);
    };
  }, [enabled, date]);

  // Re-initialize from URL when enabled changes to true
  useEffect(() => {
    if (enabled) {
      const urlParams = new URLSearchParams(window.location.search);
      const dateParam = urlParams.get('date');
      if (dateParam) {
        const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
        if (dateRegex.test(dateParam)) {
          setDateState(dateParam);
        }
      }
    }
  }, [enabled]);

  const setDate = useCallback((newDate: string) => {
    updateUrlDate(newDate);
  }, [updateUrlDate]);

  return {
    date,
    setDate,
    updateUrlDate,
  };
}

