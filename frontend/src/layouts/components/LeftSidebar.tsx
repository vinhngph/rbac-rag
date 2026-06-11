import { Bot, ChevronDown, Loader2, LogOut, MessageSquare, PanelLeftClose, PanelLeftOpen, SquarePen, User } from "lucide-react";
import { useState } from "react";
import { useLocation, useNavigate } from "react-router";
import { APP_CONFIG } from "../../core/config";
import { useAuth } from "../../features/auth/hooks/useAuth";
import { logout } from "../../features/auth/services/auth.service";
import UserAvatar from "../../shared/components/UserAvatar";
import { useToast } from "../../shared/toast";
import useChatSessions from "../../features/chat/hooks/useChatSessions";
import type { ChatSessionRead } from "../../features/chat/services/chat.service";
import ThemeToggleButton from "../../shared/components/ThemeToggleButton";
import { useQueryClient } from "@tanstack/react-query";
import { useDepartmentStore } from "../../features/departments/store/department.store";

function ChatSessionItems({ sessions, activeChatId }: { sessions: ChatSessionRead[], activeChatId: string | null }) {
  const navigate = useNavigate();

  return (
    (!Array.isArray(sessions) || sessions.length === 0)
      ? (
        <p className="text-center text-xs text-text-muted mt-4">No chats yet</p>
      )
      : (
        sessions.map((chat) => (
          <button
            onClick={() => navigate(`/chat/${chat.id}`)}
            key={chat.id}
            className={`w-full text-left px-3 py-2 rounded-xl text-sm transition-colors truncate cursor-pointer ${activeChatId === chat.id
              ? "bg-surface-active text-text"
              : "text-text/70 hover:bg-surface-hover "}`}
          >
            <div className="flex items-center gap-2">
              <MessageSquare className="w-3.5 h-3.5 shrink-0 opacity-50" />
              <span className="truncate">{chat.title}</span>
            </div>
          </button>
        ))
      )
  );
}

function LeftSidebar() {
  const [leftCollapsed, setLeftCollapsed] = useState<boolean>(false);
  const [isUserMenu, setIsUserMenu] = useState<boolean>(false);

  const { user, setUser } = useAuth();
  const { error: toastError } = useToast();

  const navigate = useNavigate();
  const location = useLocation();
  const queryClient = useQueryClient();

  const { sessions, isLoadingSessions } = useChatSessions();
  const { clearDepartments } = useDepartmentStore();

  const activeChatId = location.pathname.startsWith("/chat/") ? location.pathname.split("/")[2] : null;

  const handleLogout = async () => {
    try {
      await logout();

      queryClient.clear();
    } catch {
      toastError("Failed to loggout.");
    } finally {
      setUser(null);
      setIsUserMenu(false);
      clearDepartments();
      navigate("/auth");
    }
  };

  return (
    <aside className={`flex flex-col transition-all duration-300 ease-in-out bg-bg-sidebar border-r border-border-subtle ${leftCollapsed ? "w-15" : "w-70"}`}>
      {/* Top bar */}
      <div className="flex items-center justify-between px-3 py-3 h-13">
        {!leftCollapsed && (
          <div className="flex items-center gap-2 px-1">
            <button
              className="cursor-pointer"
              onClick={() => navigate("/")}
            >
              <Bot className="w-5 h-5 text-emerald-400 shrink-0" />
            </button>
            <span className="text-[15px] font-semibold tracking-tight text-text">{APP_CONFIG.APP_NAME}</span>
          </div>
        )}
        <div className={`flex items-center gap-1 ${leftCollapsed ? "mx-auto" : ""}`}>
          <button
            onClick={() => setLeftCollapsed(!leftCollapsed)}
            className="p-1.5 rounded-lg hover:bg-surface-hover transition-colors cursor-pointer"
            title={leftCollapsed ? "Open sidebar" : "Close sidebar"}
          >
            {leftCollapsed
              ? <PanelLeftOpen className="w-4 h-4 text-text/70" />
              : <PanelLeftClose className="w-4 h-4 text-text/70" />
            }
          </button>
        </div>
      </div>

      {!leftCollapsed && (
        <>
          {/* New chat button */}
          <div className="px-3 pb-3">
            <button
              onClick={() => navigate("/")}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-surface-hover transition-colors text-sm text-text/80 cursor-pointer"
            >
              <SquarePen className="w-4 h-4" />
              <span>New chat</span>
            </button>
          </div>

          {/* Search */}
          {/* <div className="px-3 pb-2">
            <button className="w-full flex items-center gap-2 px-3 py-2 rounded-xl bg-surface hover:bg-surface-hover transition-colors text-sm text-text/60 cursor-pointer">
              <Search className="w-3.5 h-3.5" />
              <span>Search chats</span>
            </button>
          </div> */}

          {/* Chat history */}
          <div className="flex-1 overflow-y-auto px-2 custom-scrollbar">
            {isLoadingSessions
              ? (
                <div className="flex justify-center p-4">
                  <Loader2 className="w-4 h-4 text-text-muted animate-spin" />
                </div>
              )
              : <ChatSessionItems sessions={sessions} activeChatId={activeChatId} />}
          </div>

          {/* User profile | Login */}
          <div className="border-t border-border-subtle p-2">
            {user
              // Logged in
              ? <div className="relative">
                <button
                  onClick={() => setIsUserMenu(!isUserMenu)}
                  className="w-full flex items-center gap-2.5 px-2 py-2 rounded-xl hover:bg-surface-hover transition-colors group cursor-pointer"
                >
                  {/* User avatar */}
                  <UserAvatar avatar_url={user.avatar_url} name={user.name} />

                  {/* User metadata */}
                  <div className="flex-1 text-left min-w-0">
                    <p className="text-sm font-medium text-text truncate">{user.name}</p>
                    <p className="text-[11px] text-text-muted truncate">{user.email}</p>
                  </div>

                  <ChevronDown
                    className={`w-3.5 h-3.5 text-text-muted group-hover:text-text/70 transition-all ${isUserMenu ? "rotate-180 " : ""
                    }`}
                  />
                </button>

                {isUserMenu && (
                  <div className="absolute bottom-full left-0 right-0 mb-1 bg-bg-menu border border-border-subtle rounded-xl shadow-xl overflow-hidden">
                    <ThemeToggleButton />
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center gap-2.5 px-3 py-2.5 text-sm text-red-400 hover:bg-red-500/10 transition-colors cursor-pointer"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Logout</span>
                    </button>
                  </div>
                )}
              </div>
              : // Guest
              <button
                onClick={() => navigate("/auth")}
                className="w-full flex items-center gap-2.5 px-2 py-2 rounded-xl hover:bg-surface-hover transition-colors cursor-pointer group"
              >
                <div className="w-8 h-8 rounded-full bg-surface flex items-center justify-center shrink-0">
                  <User className="w-4 h-4 text-text-muted group-hover:text-text/80 transition-colors" />
                </div>
                <div className="text-left"></div>
                <p className="text-sm font-medium text-text/70 group-hover:text-text transition-colors">Login</p>
              </button>
            }
          </div>
        </>
      )}

      {/* LeftCollapsed: icon-only buttons */}
      {leftCollapsed && (
        <div className="flex flex-col items-center gap-1 px-2 flex-1">
          <button
            onClick={() => navigate("/")}
            className="p-2.5 rounded-xl hover:bg-surface-hover transition-colors cursor-pointer"
            title="New chat"
          >
            <SquarePen className="w-4 h-4 text-text/70" />
          </button>
        </div>
      )}
    </aside>
  );
}

export default LeftSidebar;
