import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useToast } from "../../../shared/toast";
import { useErrorHandler } from "../../../shared/hooks/useErrorHandler";
import { chatService } from "../services/chat.service";

export const CHAT_SESSIONS_QUERY_KEY = ["chat_sessions"];

function useChatSessions() {
  const queryClient = useQueryClient();

  const { error } = useToast();
  const { handleCatch } = useErrorHandler();

  const { data: sessions = [], isLoading: isLoadingSessions } = useQuery({
    queryKey: CHAT_SESSIONS_QUERY_KEY,
    queryFn: () => chatService.getSessions().then((res) => res.data)
  });

  const createSessionMut = useMutation({
    mutationFn: ({ department_ids, title }: { department_ids: string[], title?: string }) =>
      chatService.createSessions(department_ids, title).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CHAT_SESSIONS_QUERY_KEY });
    },
    onError: (err: unknown) => {
      error(handleCatch(err));
    }
  });

  return {
    sessions,
    isLoadingSessions,
    handleCreateSession: createSessionMut.mutateAsync
  };
}

export default useChatSessions;
