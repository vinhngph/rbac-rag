import { useEffect, useState } from "react";
import { useAuth } from "../../auth/hooks/useAuth";
import { createDepartment, deleteDepartment, getDepartments, updateDepartment, type DepartmentRead } from "../services/department.service";
import { useToast } from "../../../shared/toast";

function useDepartments() {
  const { user } = useAuth();
  const { success, error } = useToast();

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
      success("Department created successfully.");
    } catch {
      error("Failed to create department.");
    }
  };

  const handleUpdateDepartment = async (id: string, name: string) => {
    try {
      const res = await updateDepartment(id, { name });
      setDepartments((prev) => prev.map((d) => d.id === id ? res.data : d));
    } catch {
      error("Failed to update department");
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
    } catch {
      error("Failed to delete department.");
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
