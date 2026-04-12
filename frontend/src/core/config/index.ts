import { z } from "zod";

const envSchema = z.object({
  APP_NAME: z.string().min(1, { message: "APP_NAME cannot be null." }),
  APP_BE_API: z.url()
});

const runtimeEnv = globalThis.__ENV__ || {};

const parsedEnv = envSchema.safeParse(runtimeEnv);

if (!parsedEnv.success) {
  console.error("Runtime Config:", parsedEnv.error);
  throw new Error("App has been stopped!.");
}

export const APP_CONFIG = parsedEnv.data;
