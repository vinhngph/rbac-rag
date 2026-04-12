import { useEffect, useState } from "react";
import { useAuth } from "../../auth/hooks/useAuth";
import { createDepartment, deleteDepartment, getDepartments, updateDepartment, type DepartmentRead } from "../services/department.service";

function useDepartments() {
  const { user } = useAuth();
  const [departments, setDepartments] = useState<DepartmentRead[]>([]);
  const [checkedDepartments, setCheckedDepartments] = useState<Set<string>>(new Set());

  // Load active departments
  useEffect(() => {
    if (!user) return;

    getDepartments()
      .then((res) => setDepartments(res.data))
      .catch(console.error);
  }, [user]);

  const handleAddDepartment = async (name: string) => {
    if(!name.trim()) return;

    try {
      const res = await createDepartment({ name });
      setDepartments((prev) => [...prev, res.data]);
    } catch (e) {
      console.error(e);
    }
  };

  const handleUpdateDepartment = async (id: string, name: string) => {
    try {
      const res = await updateDepartment(id, { name });
      setDepartments((prev) => prev.map((d) => d.id === id ? res.data : d));
    } catch (e) {
      console.error(e);
    }
  };

  const handleDeleteDepartment = async (id: string) => {
    try {
      await deleteDepartment(id);
      setDepartments((prev) => prev.filter((d) => d.id !== id));
      setCheckedDepartments((prev) => {
        const n = new Set(prev);
        n.delete(id);
        return n;
      });
    } catch (e) {
      console.error(e);
      throw e;
    }
  };

  const handleToggleCheck = (id: string) => {
    setCheckedDepartments((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      }  else {
        next.add(id);
      }
      return next;
    });
  };

  return {
    departments, checkedDepartments, handleAddDepartment, handleUpdateDepartment, handleDeleteDepartment, handleToggleCheck
  };
}

export default useDepartments;
