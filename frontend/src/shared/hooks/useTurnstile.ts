import { useEffect, useRef, useState, useCallback } from "react";

interface TurnstileConfig {
  sitekey: string;
  theme?: "light" | "dark" | "auto";
  size?: "normal" | "compact";
  onSuccess?: (token: string) => void;
  onError?: (error: unknown) => void;
}

interface TurnstileOptions {
  sitekey: string;
  theme?: "light" | "dark" | "auto";
  size?: "normal" | "compact";
  callback: (token: string) => void;
  "error-callback"?: (error: unknown) => void;
}

declare global {
  interface Window {
    turnstile?: {
      ready: (callback: () => void) => void;
      render: (
        container: string | HTMLElement,
        options: TurnstileOptions,
      ) => string;
      remove: (widgetId: string) => void;
      reset: (widgetId: string) => void;
      getResponse: () => string | null;
    };
  }
}

export function useTurnstile(config: TurnstileConfig) {
  const containerRef = useRef<HTMLDivElement>(null);
  const widgetIdRef = useRef<string | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const configRef = useRef(config);

  useEffect(() => {
    configRef.current = config;
  }, [config]);

  useEffect(() => {
    let interval: number | null = null;

    const renderWidget = () => {
      const turnstile = window.turnstile;
      if (!turnstile || !containerRef.current || widgetIdRef.current) return;

      const currentConfig = configRef.current;
      if (!currentConfig.sitekey) return;

      turnstile.ready(() => {
        if (!containerRef.current || widgetIdRef.current) return;

        widgetIdRef.current = turnstile.render(containerRef.current, {
          sitekey: currentConfig.sitekey,
          theme: currentConfig.theme || "auto",
          size: currentConfig.size || "normal",
          callback: (t: string) => {
            setToken(t);
            if (currentConfig.onSuccess) currentConfig.onSuccess(t);
          },
          "error-callback": (e: unknown) => {
            if (currentConfig.onError) currentConfig.onError(e);
          },
        });
      });
    };

    if (window.turnstile) {
      renderWidget();
    } else {
      interval = setInterval(() => {
        if (window.turnstile) {
          if (interval) clearInterval(interval);
          renderWidget();
        }
      }, 100);
    }

    return () => {
      if (interval) clearInterval(interval);
      if (widgetIdRef.current) {
        window.turnstile?.remove(widgetIdRef.current);
        widgetIdRef.current = null;
      }
    };
  }, [config.sitekey]);

  const reset = useCallback(() => {
    if (widgetIdRef.current) {
      window.turnstile?.reset(widgetIdRef.current);
      setToken(null);
    }
  }, []);

  return { containerRef, token, reset };
}
