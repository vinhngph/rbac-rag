import { useState } from "react";
import { Bot, ChevronDown, MessageSquare, PanelLeftClose, PanelLeftOpen, Search, SquarePen } from "lucide-react";
import { Outlet } from "react-router";
import { APP_CONFIG } from "../config";

const mockChats = [
  { id: 1, title: "What is RAG?" },
  { id: 2, title: "What is RAG?" },
  { id: 3, title: "What is RAG?" },
  { id: 4, title: "What is RAG?" },
  { id: 5, title: "What is RAG?" },
  { id: 6, title: "What is RAG?" },
];

function MainLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const [activeChat, setActiveChat] = useState<number | null>(null);

  const user = { name: "Nguyễn Phúc Vinh", email: "vinh@example.com" };

  return (
    <div className="flex h-screen bg-bg text-text font-sans overflow-hidden">
      {/* SIDEBAR */}
      <aside className={`flex flex-col transition-all duration-300 ease-in-out bg-bg-sidebar border-r border-white/5 ${collapsed ? "w-15" : "w-65"}`}>
        {/* Top bar */}
        <div className="flex items-center justify-between px-3 py-3 h-13">
          {!collapsed && (
            <div className="flex items-center gap-2 px-1">
              <Bot className="w-5 h-5 text-emerald-400 shrink-0" />
              <span className="text-[15px] font-semibold tracking-tight text-zinc-300">{APP_CONFIG.APP_NAME}</span>
            </div>
          )}
          <div className={`flex items-center gap-1 ${collapsed ? "mx-auto" : ""}`}>
            <button
              onClick={() => setCollapsed(!collapsed)}
              className="p-1.5 rounded-lg hover:bg-white/10 transition-colors cursor-pointer"
              title={collapsed ? "Open sidebar" : "Close sidebar"}
            >
              {collapsed
                ? <PanelLeftOpen className="w-4 h-4 text-text/70" />
                : <PanelLeftClose className="w-4 h-4 text-text/70" />
              }
            </button>
          </div>
        </div>

        {!collapsed && (
          <>
            {/* New chat button */}
            <div className="px-3 pb-3">
              <button
                className="w-full flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-white/8 transition-colors text-sm text-text/80 cursor-pointer"
              >
                <SquarePen className="w-4 h-4" />
                <span>New chat</span>
              </button>
            </div>

            {/* Search */}
            <div className="px-3 pb-2">
              <button className="w-full flex items-center gap-2 px-3 py-2 rounded-xl bg-white/5 hover:bg-white/10 transition-colors text-sm text-text/60 cursor-pointer">
                <Search className="w-3.5 h-3.5" />
                <span>Search chats</span>
              </button>
            </div>

            {/* Chat history */}
            <div className="flex-1 overflow-y-auto px-2">
              {mockChats.map((chat) => (
                <button
                  onClick={() => setActiveChat(chat.id)}
                  key={chat.id}
                  className={`w-full text-left px-3 py-2 rounded-xl text-sm transition-colors truncate cursor-pointer ${activeChat === chat.id
                    ? "bg-white/12 text-text"
                    : "text-text/70 hover:bg-white/8 "}`}
                >
                  <div className="flex items-center gap-2">
                    <MessageSquare className="w-3.5 h-3.5 shrink-0 opacity-50" />
                    <span className="truncate">{chat.title}</span>
                  </div>
                </button>
              ))}
            </div>

            {/* User profile */}
            <div className="border-t border-white/5 p-2">
              <button className="w-full flex items-center gap-2.5 px-2 py-2 rounded-xl hover:bg-white/10 transition-colors group cursor-pointer">
                <div className="w-8 h-8 rounded-full bg-linear-to-br from-emerald-400 to-cyan-500 flex items-center justify-center text-xs font-bold text-text shrink-0">
                  {user.name.charAt(0)}
                </div>
                <div className="flex-1 text-left min-w-0">
                  <p className="text-sm font-medium text-text truncate">{user.name}</p>
                  <p className="text-[11px] text-text/40 truncate">{user.email}</p>
                </div>
                <ChevronDown className="w-3.5 h-3.5 text-text/40 group-hover:text-text/70 transition-colors" />
              </button>
            </div>
          </>
        )}

        {/* Collapsed: icon-only buttons */}
        {collapsed && (
          <div className="flex flex-col items-center gap-1 px-2 flex-1">
            <button
              className="p-2.5 rounded-xl hover:bg-white/10 transition-colors cursor-pointer"
              title="New chat"
            >
              <SquarePen className="w-4 h-4 text-text/70" />
            </button>
          </div>
        )}
      </aside>

      {/* MAIN */}
      <main className="flex-1 overflow-hidden">
        <Outlet />
      </main>
    </div>
  );
}

export default MainLayout;