import axios, { AxiosError } from "axios";

import { APP_CONFIG } from "../config";

export interface FastAPIError {
  detail?: string | Array<{ msg: string; type: string; loc: string[] }>
}

export const api = axios.create({
  baseURL: APP_CONFIG.APP_BE_API,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json"
  }
});

api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error: AxiosError<FastAPIError>) => {
    let errorMessage = "An unexpected error occurred.";

    if (error.response) {
      const data = error.response.data;

      if (data && Array.isArray(data.detail)) {
        errorMessage = data.detail[0]?.msg || "Invalid data.";
      }
      else if (data && typeof data.detail === "string") {
        errorMessage = data.detail;
      }

      // HTTP Error code
      switch (error.response.status) {
      case 401:
        break;
      case 500:
        break;
      }
    } else if (error.request) {
      errorMessage = "Cannot connect to the server. Please check your internet.";
    }

    error.message = errorMessage;

    return Promise.reject(error);
  }
);
