import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { addMember, getRoleMembers, removeMember, updateMemberRolePermissions, type MemberCreate, type MemberRead } from "../services/role.service";

function useRoleMembers(roleId?: string) {
  const queryClient = useQueryClient();
  const queryKeyStr = "role_members";

  const { data: roleMembers = [], isLoading: isLoadingMembers } = useQuery({
    queryKey: [queryKeyStr, roleId],
    queryFn: () => getRoleMembers(roleId?? "").then((res) => res.data),
    enabled: !!roleId
  });

  const togglePermissionMut = useMutation({
    mutationFn: ({ id, permissions }: {id: string, permissions: ("view" | "edit")[]}) =>
      updateMemberRolePermissions(roleId ?? "", { id, permissions }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [queryKeyStr, roleId] });
    }
  });

  const removeMemberMut = useMutation({
    mutationFn: (memberId: string) => removeMember(roleId ?? "", memberId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [queryKeyStr, roleId] });
    }
  });

  const addMemberMut = useMutation({
    mutationFn: ({ email, permissions }:MemberCreate) =>
      addMember(roleId ?? "", { email, permissions }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [queryKeyStr, roleId] });
    }
  });

  const handleTogglePermission = (member: MemberRead, permission: "view" | "edit") => {
    const perms = member.permissions ?? [];
    let next: ("view" | "edit")[];
    if (perms.includes(permission)) {
      if (perms.length === 1) return;
      next = perms.filter((p) => p !== permission);
    } else {
      next = [...perms, permission];
    }
    togglePermissionMut.mutate({ id: member.id, permissions: next });
  };

  return {
    roleMembers,
    isLoadingMembers,
    handleTogglePermission,
    handleRemoveMember: removeMemberMut.mutateAsync,
    handleAddMember: addMemberMut.mutateAsync
  };
}

export default useRoleMembers;
