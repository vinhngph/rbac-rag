import { createBrowserRouter } from "react-router";

import MainLayout from "../layouts/MainLayout";
import SuspenseWrapper from "../components/SuspenseWrapper";
import { HomePage, NotFoundPage, LoginPage } from "../pages";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <MainLayout />,
    children: [
      { index: true, element: <SuspenseWrapper><HomePage /></SuspenseWrapper> },
      { path: "/login", element: <SuspenseWrapper><LoginPage /></SuspenseWrapper> }
    ]
  },
  {
    path: "*",
    element: <SuspenseWrapper><NotFoundPage /></SuspenseWrapper>
  }
]);