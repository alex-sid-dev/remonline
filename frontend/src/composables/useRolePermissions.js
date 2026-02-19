import { computed } from 'vue';
import { ROLES, canManageEmployees, canManageParts, canCreateOrders, isManagerRole } from '../constants/roles';

export function useRolePermissions(userRole) {
  const canManageEmps = computed(() => canManageEmployees(userRole.value));
  const canManagePts = computed(() => canManageParts(userRole.value));
  const canCreateOrd = computed(() => canCreateOrders(userRole.value));
  const isManager = computed(() => isManagerRole(userRole.value));

  return {
    ROLES,
    canManageEmps,
    canManagePts,
    canCreateOrd,
    isManager,
  };
}
