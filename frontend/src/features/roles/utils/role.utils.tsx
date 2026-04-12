import type { RoleRead } from "../services/role.service";

export function buildRoleMap(roles: RoleRead[]): Map<string | null, RoleRead[]> {
  const map = new Map<string | null, RoleRead[]>();
  for (const role of roles) {
    const key = role.parent_id ?? null;

    let roleGroup = map.get(key);

    if (!roleGroup) {
      roleGroup = [];
      map.set(key, roleGroup);
    }

    roleGroup.push(role);
  }
  return map;
}

export function getRolePath(roles: RoleRead[], targetId: string): RoleRead[] {
  const byId = new Map(roles.map((r) => [r.id, r]));
  const path: RoleRead[] = [];
  let cur = byId.get(targetId);
  while (cur) {
    path.unshift(cur);
    cur = cur.parent_id ? byId.get(cur.parent_id) : undefined;
  }
  return path;
}
