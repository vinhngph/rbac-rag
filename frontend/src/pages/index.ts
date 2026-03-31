import { lazy } from "react";

export const HomePage = lazy(() => import("./Home"));
export const DepartmentPage = lazy(() => import("./Department"));
export const NotFoundPage = lazy(() => import("./NotFound"));