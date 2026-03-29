import { createBrowserRouter } from "react-router";

import MainLayout from "../layouts/MainLayout";
import SuspenseWrapper from "../components/SuspenseWrapper";
import { HomePage, NotFoundPage } from "../pages";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <MainLayout />,
    children: [
      { index: true, element: <SuspenseWrapper><HomePage /></SuspenseWrapper> },
      { path: "auth", element: <SuspenseWrapper><HomePage /></SuspenseWrapper> }
    ]
  },
  {
    path: "*",
    element: <SuspenseWrapper><NotFoundPage /></SuspenseWrapper>
  }
]);