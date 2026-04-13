import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getRoleKnowledges, uploadKnowledge } from "../services/role.service";
import { deleteKnowledge, updateKnowledge } from "../../knowledge/services/knowledge.service";
import type React from "react";

function useRoleKnowledges(roleId: string | undefined) {
  const queryClient = useQueryClient();

  const queryKeyStr = "role_knowledges";

  const { data: roleKnowledges = [], isLoading: isLoadingKnowledges } = useQuery({
    queryKey: [queryKeyStr, roleId],
    enabled: !!roleId,
    queryFn: () => getRoleKnowledges(roleId ?? "").then((res) => res.data),
  });

  const uploadMut = useMutation({
    mutationFn: (file: File) => uploadKnowledge(roleId ?? "", file),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: [queryKeyStr, roleId] })
  });

  const renameMut = useMutation({
    mutationFn: ({ knowledgeId, name } : {knowledgeId: string, name:string}) =>
      updateKnowledge(knowledgeId, { name }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: [queryKeyStr, roleId] })
  });

  const deleteMut = useMutation({
    mutationFn: (knowledgeId: string) => deleteKnowledge(knowledgeId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: [queryKeyStr, roleId] })
  });

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>, ref: React.RefObject<HTMLInputElement>) => {
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
