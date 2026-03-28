import { useState } from "react";
import { useNavigate } from "react-router";

import { login, getMe } from "../modules/auth/auth.service";
import { useAuth } from "../modules/auth/useAuth";

function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");

  const { setUser } = useAuth();

  const handleLogin = async () => {
    await login({
      email,
      plain_text_password: password
    });

    const res = await getMe();

    setUser(res.data);
    navigate("/");
  };

  return (
    <div>
      <input
        type="email"
        placeholder="Email"
        onChange={(e) => setEmail(e.target.value)}
      />

      <input
        type="password"
        placeholder="Password"
        onChange={(e) => setPassword(e.target.value)}
      />

      <button onClick={handleLogin}>
        Login
      </button>
    </div>
  );
}

export default Login;