import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getRoleKnowledges, uploadKnowledge } from "../services/role.service";
import { deleteKnowledge, updateKnowledge } from "../../knowledge/services/knowledge.service";
import type React from "react";
import { useToast } from "../../../shared/toast";
import { useErrorHandler } from "../../../shared/hooks/useErrorHandler";

function useRoleKnowledges(roleId: string | undefined) {
  const queryClient = useQueryClient();
  const { handleCatch } = useErrorHandler();
  const { error } = useToast();

  const queryKeyStr = "role_knowledges";

  const { data: roleKnowledges = [], isLoading: isLoadingKnowledges } = useQuery({
    queryKey: [queryKeyStr, roleId],
    enabled: !!roleId,
    queryFn: () => getRoleKnowledges(roleId ?? "").then((res) => res.data),
  });

  const uploadMut = useMutation({
    mutationFn: (file: File) => uploadKnowledge(roleId ?? "", file),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: [queryKeyStr, roleId] }),
    onError: (err: unknown) => {
      error(handleCatch(err));
    }
  });

  const renameMut = useMutation({
    mutationFn: ({ knowledgeId, name } : {knowledgeId: string, name:string}) =>
      updateKnowledge(knowledgeId, { name }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: [queryKeyStr, roleId] }),
    onError: (err: unknown) => {
      error(handleCatch(err));
    }
  });

  const deleteMut = useMutation({
    mutationFn: (knowledgeId: string) => deleteKnowledge(knowledgeId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: [queryKeyStr, roleId] }),
    onError: (err: unknown) => {
      error(handleCatch(err));
    }
  });

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>, ref: React.RefObject<HTMLInputElement | null>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    await uploadMut.mutateAsync(file);
    if (ref.current) ref.current.value = "";
  };

  return {
    roleKnowledges,
    isLoadingKnowledges,
    isUploading: uploadMut.isPending,
    handleUpload,
    handleRenameKnowledge: (knowledgeId: string, name: string) => renameMut.mutateAsync({ knowledgeId, name }),
    handleDeleteKnowledge: deleteMut.mutateAsync
  };
}

export default useRoleKnowledges;
