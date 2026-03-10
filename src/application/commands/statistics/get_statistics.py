from uuid import UUID

import structlog
from pydantic import BaseModel

from src.application.ports.employee_reader import EmployeeReader
from src.application.ports.statistics_reader import OrderStatRow, StatisticsReader
from src.entities.employees.enum import EmployeePosition
from src.entities.employees.models import Employee

logger = structlog.get_logger("get_statistics").bind(service="statistics")


class EmployeeStatisticsResponse(BaseModel):
    uuid: UUID
    full_name: str
    position: str
    orders_count: int
    revenue: float
    expenses: float
    net_profit: float
    base_salary: float
    profit_percent: float
    bonus: float
    total_salary: float


class StatisticsResponse(BaseModel):
    total_orders: int
    total_revenue: float
    total_expenses: float
    net_profit: float
    employees: list[EmployeeStatisticsResponse]


class GetStatisticsCommandHandler:
    def __init__(
        self,
        statistics_reader: StatisticsReader,
        employee_reader: EmployeeReader,
    ) -> None:
        self._statistics_reader = statistics_reader
        self._employee_reader = employee_reader

    async def run(self, current_employee: Employee) -> StatisticsResponse:
        order_rows = await self._statistics_reader.get_closed_orders_stats(
            organization_id=current_employee.organization_id,
        )
        employees, _ = await self._employee_reader.read_all_active(
            organization_id=current_employee.organization_id,
            limit=1000,
            offset=0,
        )

        total_revenue = sum(r.works_revenue + r.parts_revenue for r in order_rows)
        total_expenses = sum(r.parts_cost for r in order_rows)
        total_profit = total_revenue - total_expenses

        employee_stats: list[EmployeeStatisticsResponse] = []
        for emp in employees:
            emp_rows = self._filter_orders_for_employee(emp, order_rows)

            emp_revenue = sum(r.works_revenue + r.parts_revenue for r in emp_rows)
            emp_expenses = sum(r.parts_cost for r in emp_rows)
            emp_profit = emp_revenue - emp_expenses

            base_salary = emp.salary or 0.0
            profit_pct = emp.profit_percent or 0.0
            bonus = (profit_pct / 100.0) * emp_profit
            total_salary = base_salary + bonus

            employee_stats.append(
                EmployeeStatisticsResponse(
                    uuid=emp.uuid,
                    full_name=emp.full_name,
                    position=emp.position.value
                    if isinstance(emp.position, EmployeePosition)
                    else str(emp.position),
                    orders_count=len(emp_rows),
                    revenue=round(emp_revenue, 2),
                    expenses=round(emp_expenses, 2),
                    net_profit=round(emp_profit, 2),
                    base_salary=round(base_salary, 2),
                    profit_percent=round(profit_pct, 2),
                    bonus=round(bonus, 2),
                    total_salary=round(total_salary, 2),
                )
            )

        logger.info(
            "Statistics calculated",
            total_orders=len(order_rows),
            total_revenue=round(total_revenue, 2),
            employees_count=len(employee_stats),
        )

        return StatisticsResponse(
            total_orders=len(order_rows),
            total_revenue=round(total_revenue, 2),
            total_expenses=round(total_expenses, 2),
            net_profit=round(total_profit, 2),
            employees=employee_stats,
        )

    @staticmethod
    def _filter_orders_for_employee(
        employee: Employee, rows: list[OrderStatRow]
    ) -> list[OrderStatRow]:
        pos = employee.position
        if pos in (EmployeePosition.SUPERVISOR, EmployeePosition.ADMIN):
            return rows
        if pos == EmployeePosition.MANAGER:
            return [r for r in rows if r.creator_id == employee.id]
        if pos == EmployeePosition.MASTER:
            return [r for r in rows if r.assigned_employee_id == employee.id]
        return []
