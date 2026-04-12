import { AxiosError } from "axios";

export const useErrorHandler = () => {
  const handleCatch = (err: unknown) => {
    if (err instanceof AxiosError) {
      return err.message;
    }
    return (err as Error)?.message || "Something went wrong.";
  };
  return { handleCatch };
};
