import { AlertCircle, Bot, Eye, EyeOff, Loader2, X } from "lucide-react";
import React, { useState } from "react";
import { useNavigate } from "react-router";
import { APP_CONFIG } from "../../../core/config";

import { getMe, login, register } from "../services/auth.service";
import { useAuth } from "../hooks/useAuth";
import { useErrorHandler } from "../../../shared/hooks/useErrorHandler";

type Tab = "login" | "register";

function AuthModal() {
  const navigate = useNavigate();

  const [tab, setTab] = useState<Tab>("login");
  const [name, setName] = useState<string>("");
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [isShowPassword, setIsShowPassword] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const { setUser } = useAuth();
  const { handleCatch } = useErrorHandler();

  const handleClose = () => { navigate("/"); };

  const handleDisable = () => {
    if (tab === "login")
      return !(email && password && !loading);
    else
      return !(name && email && password && !loading);
  };

  const handleSubmit = async () => {
    setError(null);
    setLoading(true);

    try {
      if (tab === "login") {
        await login({ email: email, plain_text_password: password });
      } else {
        await register({ email: email, name: name, plain_text_password: password });
      }

      const res = await getMe();
      setUser(res.data);
      navigate("/");
    } catch (err) {
      setError(handleCatch(err));
    } finally {
      setLoading(false);
    }
  };

  const handleOnSubmit = async (e: React.SubmitEvent) => {
    e.preventDefault();

    await handleSubmit();
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
    >
      {/* Button - Blur overlay */}
      <button
        className="absolute inset-0 bg-black/60 backdrop-blur-sm w-full h-full border-none"
        onClick={handleClose}
      />

      {/* Modal card */}
      <div className="relative z-10 w-full max-w-sm mx-4 bg-bg-modal border border-white/10 rounded-2xl shadow-2xl shadow-black/60 overflow-hidden"
      >
        {/* Close button */}
        <button
          onClick={handleClose}
          className="absolute top-3.5 right-3.5 p-1.5 rounded-lg hover:bg-white/10 text-text/40 hover:text-text/70 transition-colors cursor-pointer"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Header */}
        <div className="flex flex-col items-center pt-8 pb-6 px-6">
          <div className="w-10 h-10 rounded-xl bg-emerald-400/10 border border-emerald-400/20 flex items-center justify-center mb-3">
            <Bot className="w-5 h-5 text-emerald-400" />
          </div>
          <h2 className="text-lg font-semibold text-text tracking-tight">
            {APP_CONFIG.APP_NAME}
          </h2>
          <p className="text-xs text-text/40 mt-1">
            {tab === "login" ? "Welcome back" : `Start using ${APP_CONFIG.APP_NAME}`}
          </p>
        </div>

        {/* Tabs */}
        <div className="flex mx-6 mb-5 bg-white/5 rounded-xl p-1 gap-1">
          {(["login", "register"] as Tab[]).map((t) => (
            <button
              key={t}
              onClick={() => {
                setTab(t);
              }}
              className={`flex-1 py-1.5 text-sm rounded-lg transition-all font-medium cursor-pointer ${tab === t
                ? "bg-white/12 text-text shadow-sm"
                : "text-text/40 hover:text-text/60"
              }`}
            >
              {t === "login" ? "Login" : "Register"}
            </button>
          ))}
        </div>

        {/* Form */}
        <form
          className="px-6 pb-6 space-y-3"
          onSubmit={handleOnSubmit}
        >
          {/* Name */}
          {tab === "register" && (
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-text/50 uppercase tracking-wide">
                Full name
                {/*  */}
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Your name"
                  className="w-full bg-white/5 border border-white/8 hover:border-white/15 focus:border-emerald-400/40 rounded-xl px-3.5 py-2.5 text-sm text-text placeholder-white/25 outline-none transition-colors"
                />
              </label>
            </div>
          )}

          {/* Email */}
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-text/50 uppercase tracking-wide">
              Email
              {/*  */}
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full bg-white/5 border border-white/8 hover:border-white/15 focus:border-emerald-400/40 rounded-xl px-3.5 py-2.5 text-sm text-text placeholder-white/25 outline-none transition-colors"
                autoFocus
              />
            </label>
          </div>

          {/* Password */}
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-text/50 uppercase tracking-wide">
              Password
              {/*  */}
              <div className="relative">
                <input
                  type={isShowPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••"
                  className="w-full bg-white/5 border border-white/8 hover:border-white/15 focus:border-emerald-400/40 rounded-xl px-3.5 py-2.5 text-sm text-text placeholder-white/25 outline-none transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setIsShowPassword(!isShowPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-text/30 hover:text-text/60 transition-colors cursor-pointer"
                >
                  {isShowPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </label>
          </div>

          {/* Error */}
          {error && (
            <div className="flex items-start gap-2 px-3 py-2.5 bg-red-500/10 border border-red-500/20 rounded-xl">
              <AlertCircle className="w-3.5 h-3.5 text-red-400 shrink-0 mt-0.5" />
              <p className="text-xs text-red-400 leading-relaxed">{error}</p>
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={handleDisable()}
            className="w-full mt-1 bg-emerald-500 hover:bg-emerald-400 disabled:bg-emerald-500/40 text-text disabled:text-text/50 font-medium text-sm py-2.5 rounded-xl transition-all flex items-center justify-center gap-2 cursor-pointer disabled:cursor-not-allowed"
          >
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            {tab === "login" ? "Login" : "Register"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default AuthModal;
