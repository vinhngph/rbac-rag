import axios from "axios";

import { APP_CONFIG } from "../../config";

export const api = axios.create({
  baseURL: APP_CONFIG.APP_BE_API,
  withCredentials: true
});