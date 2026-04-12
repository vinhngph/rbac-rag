import { Outlet, useLocation, useMatch } from "react-router";

import AuthModal from "../features/auth/components/AuthModal";
import DepartmentModal from "../features/departments/components/DepartmentModal";
import LeftSidebar from "./components/LeftSidebar";
import RightSidebar from "./components/RightSidebar";

function MainLayout() {
  const location = useLocation();

  const isAuthOpen = location.pathname === "/auth";
  const departmentOpen = useMatch("/department/:id");

  return (
    <div className="flex h-screen bg-bg text-text font-sans overflow-hidden">
      <LeftSidebar />

      {/* MAIN */}
      <main className="flex-1 overflow-hidden relative">
        <Outlet />

        {isAuthOpen && <AuthModal />}
        {departmentOpen?.params.id && <DepartmentModal id={departmentOpen.params.id} />}
      </main>

      <RightSidebar />
    </div>
  );
}

export default MainLayout;
