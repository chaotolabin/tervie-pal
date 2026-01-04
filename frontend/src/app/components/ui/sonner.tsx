import { Toaster as Sonner, ToasterProps } from "sonner";

const Toaster = ({ ...props }: ToasterProps) => {
  // Detect theme from document or default to light
  const getTheme = (): ToasterProps["theme"] => {
    if (typeof window !== "undefined") {
      const isDark = document.documentElement.classList.contains("dark");
      return isDark ? "dark" : "light";
    }
    return "light";
  };

  return (
    <Sonner
      theme={getTheme()}
      className="toaster group"
      style={
        {
          "--normal-bg": "var(--popover)",
          "--normal-text": "var(--popover-foreground)",
          "--normal-border": "var(--border)",
        } as React.CSSProperties
      }
      {...props}
    />
  );
};

export { Toaster };
