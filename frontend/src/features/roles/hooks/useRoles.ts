import { useCallback, useEffect, useMemo, useState } from "react";
import { createRole, deleteRole, updateRole, type RoleRead } from "../services/role.service";
import { getDepartmentRoles } from "../../departments/services/department.service";
import { buildRoleMap, getRolePath } from "../utils/role.utils";

function useRoles(departmentId: string | undefined) {
  const [allRoles, setAllRoles] = useState<RoleRead[]>([]);
  const [currentRoleId, setCurrentRoleId] = useState<string | null>(null);
  const [loadingRoles, setLoadingRoles] = useState(true);

  useEffect(() => {
    if (!departmentId) return;

    const fetchRoles = async () => {
      setLoadingRoles(true);

      try {
        const res = await getDepartmentRoles(departmentId);
        setAllRoles(res.data);
        const root = res.data.find((r) => r.parent_id === null);
        setCurrentRoleId(root?.id ?? null);
      } catch (e) {
        console.error(e);
      } finally {
        setLoadingRoles(false);
      }
    };
    fetchRoles();
  }, [departmentId]);

  const roleMap = useMemo(() => buildRoleMap(allRoles), [allRoles]);
  const rootRole = useMemo(() => allRoles.find((r) => r.parent_id === null) ?? null, [allRoles]);

  const currentRole = useMemo(() => currentRoleId ? allRoles.find((r) => r.id === currentRoleId) ?? null : rootRole, [currentRoleId, allRoles, rootRole]);
  const childRoles = useMemo(() => roleMap.get(currentRole?.id ?? null) ?? [], [roleMap, currentRole]);
  const breadcrumb = useMemo(() => currentRole ? getRolePath(allRoles, currentRole.id) : [], [currentRole, allRoles]);
  const isRoot = currentRole?.parent_id === null;

  const handleNavigateRole = useCallback((roleId: string | null) => {
    setCurrentRoleId(roleId);
  }, []);

  const handleCreateRole = async (name: string) => {
    if (!name || !currentRole) return;

    try {
      const res = await createRole({ name: name, parent_id: currentRole.id });
      setAllRoles((prev) => [...prev, res.data]);
    } catch (e) {
      console.error(e);
      throw e;
    }
  };

  const handleRenameRole = async (roleId: string, name: string) => {
    try {
      const res = await updateRole(roleId, { name: name });
      setAllRoles((prev) => prev.map((r) => r.id === roleId ? res.data : r));
    } catch (e) {
      console.error(e);
      throw e;
    }
  };

  const handleDeleteRole = async (roleId: string) => {
    if (currentRoleId === roleId && currentRole?.parent_id) {
      setCurrentRoleId(currentRole.parent_id);
    }
    try {
      await deleteRole(roleId);
      setAllRoles((prev) => prev.filter((r) => r.id !== roleId));
    } catch (e) {
      console.error(e);
      throw e;
    }
  };

  return { allRoles, currentRole, childRoles, breadcrumb, isRoot, rootRole, loadingRoles, handleNavigateRole, handleCreateRole, handleRenameRole, handleDeleteRole };
}

export default useRoles;
