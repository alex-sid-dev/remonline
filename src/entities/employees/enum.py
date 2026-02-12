from enum import Enum


class EmployeePosition(str, Enum):
    MASTER = "master"
    MANAGER = "manager"
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
