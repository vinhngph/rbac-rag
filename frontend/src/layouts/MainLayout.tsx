import React, { useState } from "react";
import { Bot, Building2, ChevronDown, LogOut, MessageSquare, PanelLeftClose, PanelLeftOpen, PanelRightClose, PanelRightOpen, Plus, Search, SquarePen, User } from "lucide-react";
import { Outlet, useLocation, useNavigate } from "react-router";

import { APP_CONFIG } from "../config";
import AuthModal from "../components/AuthModal";
import { useAuth } from "../modules/auth/useAuth";
import { logout } from "../modules/auth/auth.service";
import { createDepartment, type DepartmentRead } from "../modules/department/department.service";

const mockChats = [
  { id: 1, title: "What is RAG?" },
  { id: 2, title: "What is RAG?" },
  { id: 3, title: "What is RAG?" },
  { id: 4, title: "What is RAG?" },
  { id: 5, title: "What is RAG?" },
  { id: 6, title: "What is RAG?" },
];

function MainLayout() {
  const navigate = useNavigate();
  const location = useLocation();

  const [leftCollapsed, setLeftCollapsed] = useState<boolean>(false);
  const [rightCollapsed, setRightCollapsed] = useState<boolean>(false);
  const [activeChat, setActiveChat] = useState<number | null>(null);
  const [isUserMenu, setIsUserMenu] = useState<boolean>(false);

  const [isAddingDepartment, setIsAddingDepartment] = useState<boolean>(false);
  const [newDepartmentName, setNewDepartmentName] = useState<string>("");
  const [departments, setDepartments] = useState<DepartmentRead[]>([]);

  const { user, setUser } = useAuth();

  const isAuthOpen = location.pathname === "/auth";

  const handleLogout = async () => {
    try {
      await logout();
    } catch (err) {
      console.error(err);
    } finally {
      setUser(null);
      setIsUserMenu(false);
      navigate("/auth");
    }
  };

  const handleAddDepartment = async () => {
    const name = newDepartmentName.trim();
    if (!name) return;
    try {
      const res = await createDepartment({ name });
      setDepartments((prev) => [...prev, res.data]);
      setNewDepartmentName("");
      setIsAddingDepartment(false);
    } catch (e) {
      console.error(e);
    }
  };

  const handleNewDepartmentNameKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleAddDepartment();
    if (e.key === "Escape") {
      setIsAddingDepartment(false);
      setNewDepartmentName("");
    }
  };

  return (
    <div className="flex h-screen bg-bg text-text font-sans overflow-hidden">
      {/* LEFT SIDEBAR */}
      <aside className={`flex flex-col transition-all duration-300 ease-in-out bg-bg-sidebar border-r border-white/5 ${leftCollapsed ? "w-15" : "w-65"}`}>
        {/* Top bar */}
        <div className="flex items-center justify-between px-3 py-3 h-13">
          {!leftCollapsed && (
            <div className="flex items-center gap-2 px-1">
              <Bot className="w-5 h-5 text-emerald-400 shrink-0" />
              <span className="text-[15px] font-semibold tracking-tight text-zinc-300">{APP_CONFIG.APP_NAME}</span>
            </div>
          )}
          <div className={`flex items-center gap-1 ${leftCollapsed ? "mx-auto" : ""}`}>
            <button
              onClick={() => setLeftCollapsed(!leftCollapsed)}
              className="p-1.5 rounded-lg hover:bg-white/10 transition-colors cursor-pointer"
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

            {/* User profile | Login */}
            <div className="border-t border-white/5 p-2">
              {user
                // Logged in
                ? <div className="relative">
                  <button
                    onClick={() => setIsUserMenu(!isUserMenu)}
                    className="w-full flex items-center gap-2.5 px-2 py-2 rounded-xl hover:bg-white/10 transition-colors group cursor-pointer"
                  >
                    {/* User avatar */}
                    {user.avatar_url
                      ? <img
                        src={user.avatar_url}
                        alt={user.name}
                        className="w-8 h-8 rounded-full object-cover shrink-0"
                      />
                      : <div className="w-8 h-8 rounded-full bg-linear-to-br from-emerald-400 to-cyan-5000 flex items-center justify-center text-xs font-bold text-text shrink-0">
                        {user.name.charAt(0).toUpperCase()}
                      </div>
                    }

                    {/* User metadata */}
                    <div className="flex-1 text-left min-w-0">
                      <p className="text-sm font-medium text-text truncate">{user.name}</p>
                      <p className="text-[11px] text-text/40 truncate">{user.email}</p>
                    </div>

                    <ChevronDown
                      className={`w-3.5 h-3.5 text-text/40 group-hover:text-text/70 transition-all ${isUserMenu ? "rotate-180 " : ""
                      }`}
                    />
                  </button>

                  {isUserMenu && (
                    <div className="absolute bottom-full left-0 right-0 mb-1 bg-bg-menu border border-white/10 rounded-xl shadow-xl overflow-hidden">
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
                  className="w-full flex items-center gap-2.5 px-2 py-2 rounded-xl hover:bg-white/10 transition-colors cursor-pointer group"
                >
                  <div className="w-8 h-8 rounded-full bg-white/8 flex items-center justify-center shrink-0">
                    <User className="w-4 h-4 text-text/50 group-hover:text-text/80 transition-colors" />
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
              className="p-2.5 rounded-xl hover:bg-white/10 transition-colors cursor-pointer"
              title="New chat"
            >
              <SquarePen className="w-4 h-4 text-text/70" />
            </button>
          </div>
        )}
      </aside>

      {/* MAIN */}
      <main className="flex-1 overflow-hidden relative">
        <Outlet />
        {isAuthOpen && <AuthModal />}
      </main>

      {/* RIGHT SIDEBAR */}
      <aside className={`flex flex-col transition-all duration-300 ease-in-out bg-bg-sidebar border-l border-white/5 ${rightCollapsed ? "w-15" : "w-72"}`}>
        {/* Header */}
        <div className="flex items-center h-13 px-3 border-b border-white/5 gap-2">
          <button
            onClick={() => setRightCollapsed(!rightCollapsed)}
            className="p-1.5 rounded-lg hover:bg-white/10 transition-colors cursor-pointer shrink-0"
            title={rightCollapsed ? "Open departments" : "Close departments"}
          >
            {rightCollapsed
              ? <PanelRightOpen className="w-4 h-4 text-text/70" />
              : <PanelRightClose className="w-4 h-4 text-text/70" />}
          </button>

          {!rightCollapsed && (
            <>
              <Building2 className="w-4 h-4 text-text/40 shrink-0" />
              <span className="text-[12px] font-semibold text-text/50 tracking-widest uppercase flex-1">Departments</span>
              <button
                onClick={() => setIsAddingDepartment(true)}
                className="p-1.5 rounded-lg hover:bg-white/10 text-text/35 hover:text-text/75 transition-colors cursor-pointer"
                title="New department"
              >
                <Plus className="w-4 h-4" />
              </button>
            </>
          )}
        </div>

        {/* Collapsed icon strip */}
        {rightCollapsed && (
          <div className="flex flex-col items-center gap-1 px-2 pt-2">
            <button
              onClick={() => setRightCollapsed(false)}
              className="p-2 rounded-xl hover:bg-white/10 transition-colors cursor-pointer"
              title="Departments"
            >
              <Building2 className="w-4 h-4 text-text/40" />
            </button>
          </div>
        )}

        {!rightCollapsed && (
          <>
            {/* Add new department */}
            {isAddingDepartment && (
              <div className="px-3 py-2.5 border-b border-white/5">
                <input
                  autoFocus
                  type="text"
                  value={newDepartmentName}
                  onChange={(e) => setNewDepartmentName(e.target.value)}
                  onKeyDown={handleNewDepartmentNameKeyDown}
                  placeholder="Department name..."
                  className="w-full bg-white/5 border border-white/10 focus:border-emerald-400/40 rounded-xl px-3 py-2 text-sm text-text placeholder-text/25 outline-none transition-colors"
                />
                <div className="flex gap-1.5 mt-2">
                  <button
                    onClick={() => {
                      setIsAddingDepartment(false);
                      setNewDepartmentName("");
                    }}
                    className="flex-1 py-1.5 text-xs text-text/50 hover:text-text bg-white/5 hover:bg-white/10 rounded-lg transition-colors cursor-pointer"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleAddDepartment}
                    disabled={!newDepartmentName.trim()}
                    className="flex-1 py-1.5 text-xs text-text bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 rounded-lg transition-colors cursor-pointer disabled:cursor-not-allowed"
                  >
                    Create
                  </button>
                </div>
              </div>
            )}

            {/* Knowledge context badge */}
          </>
        )}
      </aside>
    </div>
  );
}

export default MainLayout;