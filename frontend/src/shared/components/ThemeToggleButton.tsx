import { Moon, Sun } from "lucide-react";
import { useThemeStore } from "../store/theme.store";

function ThemeToggleButton() {
  const { isDarkMode, toggleTheme } = useThemeStore();

  return (
    <button
      className="w-full flex items-center gap-2.5 px-3 py-2.5 text-sm bg-bg-menu text-text hover:opacity-80 transition-opacity cursor-pointer"
      onClick={toggleTheme}
    >
      {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
      <span>{isDarkMode ? "Dark" : "Light"}</span>
    </button>
  );
}

export default ThemeToggleButton;
