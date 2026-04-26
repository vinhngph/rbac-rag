import { create } from "zustand";

interface DepartmentState {
    checkedDepartments: string[]
    toggleDepartment: (id: string) => void
    clearDepartments: () => void
    setDepartments: (ids: string[]) => void
}

export const useDepartmentStore = create<DepartmentState>((set) => ({
  checkedDepartments: [],

  toggleDepartment: (id) => set((state) => {
    const isChecked = state.checkedDepartments.includes(id);
    if (isChecked) {
      return { checkedDepartments: state.checkedDepartments.filter(deptId => deptId !== id) };
    } else {
      return { checkedDepartments: [...state.checkedDepartments, id] };
    }
  }),
  clearDepartments: () => set({ checkedDepartments:[] }),
  setDepartments: (ids: string[]) => set({ checkedDepartments: ids }),
}));
