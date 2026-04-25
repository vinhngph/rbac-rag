import { useState } from "react";
import { useAuth } from "../../auth/hooks/useAuth";
import { createDepartment, deleteDepartment, getDepartments, updateDepartment } from "../services/department.service";
import { useToast } from "../../../shared/toast";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useErrorHandler } from "../../../shared/hooks/useErrorHandler";

function useDepartments() {
  const { user } = useAuth();
  const { error } = useToast();
  const { handleCatch } = useErrorHandler();

  const queryClient = useQueryClient();
  const queryKeyName = ["departments"];

  const [checkedDepartments, setCheckedDepartments] = useState<Set<string>>(new Set());

  const { data: departments = [] } = useQuery({
    queryKey: queryKeyName,
    queryFn: () => getDepartments().then((res) => res.data),
    enabled: !!user
  });

  const createDepartmentMut = useMutation({
    mutationFn: (name: string) => createDepartment({ name }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeyName });
    },
    onError: (err: unknown) => {
      error(handleCatch(err));
    }
  });

  const renameDepartmentMut = useMutation({
    mutationFn: ({ id, name }: { id: string, name: string }) => updateDepartment(id, { name }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeyName });
    },
    onError: (err: unknown) => {
      error(handleCatch(err));
    }
  });

  const deleteDepartmentMut = useMutation({
    mutationFn: (id: string) => deleteDepartment(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeyName });
    },
    onError: (err: unknown) => {
      error(handleCatch(err));
    }
  });

  const handleToggleCheck = (id: string) => {
    setCheckedDepartments((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  return {
    departments,
    checkedDepartments,
    handleAddDepartment: createDepartmentMut.mutateAsync,
    handleUpdateDepartment: (id: string, name: string) => renameDepartmentMut.mutateAsync({ id, name }),
    handleDeleteDepartment: deleteDepartmentMut.mutateAsync,
    handleToggleCheck
  };
}

export default useDepartments;
