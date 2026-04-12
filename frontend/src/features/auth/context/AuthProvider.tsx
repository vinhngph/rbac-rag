import { useEffect, useMemo, useState, type ReactNode } from "react";
import { getMe } from "../services/auth.service";
import { AuthContext, type User } from "./auth.context";

interface AuthProviderProps {
  readonly children: ReactNode
}

function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const init = async () => {
      try {
        const res = await getMe();
        setUser(res.data);
      } catch {
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    init();
  }, []);;

  const valueObj = useMemo(() => ({ user, setUser, loading }), [user, loading]);

  return (
    <AuthContext.Provider value={valueObj}>
      {children}
    </AuthContext.Provider>
  );
}

export default AuthProvider;
