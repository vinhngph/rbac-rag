import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useMemo, useState } from "react";

import { getDepartmentRoles } from "../../departments/services/department.service";
import { buildRoleMap, getRolePath } from "../utils/role.utils";
import { createRole, deleteRole, updateRole } from "../services/role.service";

function useRoles(departmentId: string) {
  const queryClient = useQueryClient();
  const [currentRoleId, setCurrentRoleId] = useState<string | null>(null);

  const { data, isLoading: isLoadingRoles } = useQuery({
    queryKey: ["roles", departmentId],
    queryFn: ()=> getDepartmentRoles(departmentId).then(res => res.data),
    enabled: !!departmentId
  });

  const allRoles = useMemo(() => data?.roles_chain ?? [], [data]);
  const userContextRole = useMemo(() => data?.current_user_role ?? null, [data]);

  const roleMap = useMemo(() => buildRoleMap(allRoles), [allRoles]);
  const rootRole = useMemo(() => allRoles.find((r) => r.parent_id === null) ?? null, [allRoles]);
  const currentRole = useMemo(() => currentRoleId ? allRoles.find((r) => r.id === currentRoleId) ?? null : userContextRole, [currentRoleId, allRoles, userContextRole]);
  const childRoles = useMemo(() => roleMap.get(currentRole?.id ?? null) ?? [], [roleMap, currentRole]);
  const breadcrumb = useMemo(() => currentRole ? getRolePath(allRoles, currentRole.id) : [], [currentRole, allRoles]);
  const isRoot = currentRole?.parent_id === null;

  const navigateRole = useCallback((roleId: string | null) => {
    setCurrentRoleId(roleId);
  }, []);

  const createRoleMut = useMutation({
    mutationFn: (name: string) => createRole({ name, parent_id: currentRole!.id }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["roles", departmentId] });
    }
  });

  const renameRoleMut = useMutation({
    mutationFn: ({ id, name } : {id: string, name: string}) => updateRole(id, { name }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["roles", departmentId] });
    }
  });

  const deleteRoleMut = useMutation({
    mutationFn: (id: string) => deleteRole(id),
    onSuccess: (_, deletedId) => {
      if (currentRoleId === deletedId && currentRole?.parent_id) {
        setCurrentRoleId(currentRole.parent_id);
      }
      queryClient.invalidateQueries({ queryKey: ["roles", departmentId] });
    }
  });

  return {
    allRoles,
    rootRole,
    currentRole,
    childRoles,
    breadcrumb,
    isRoot,
    isLoadingRoles,

    // Actions
    navigateRole,
    handleCreateRole: createRoleMut.mutateAsync,
    handleRenameRole: (id: string, name: string) => renameRoleMut.mutateAsync({ id, name }),
    handleDeleteRole: deleteRoleMut.mutateAsync
  };
}

export default useRoles;
