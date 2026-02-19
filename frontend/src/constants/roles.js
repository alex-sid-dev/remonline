export const ROLES = {
  SUPERVISOR: 'supervisor',
  ADMIN: 'admin',
  MANAGER: 'manager',
  MASTER: 'master',
};

export function canManageEmployees(role) {
  return [ROLES.SUPERVISOR, ROLES.ADMIN].includes(role);
}

export function canManageParts(role) {
  return [ROLES.SUPERVISOR, ROLES.ADMIN, ROLES.MASTER].includes(role);
}

export function canCreateOrders(role) {
  return [ROLES.SUPERVISOR, ROLES.ADMIN, ROLES.MANAGER].includes(role);
}

export function isManagerRole(role) {
  return [ROLES.MANAGER, ROLES.ADMIN, ROLES.SUPERVISOR].includes(role);
}

export function isMaster(role) {
  return role === ROLES.MASTER;
}
