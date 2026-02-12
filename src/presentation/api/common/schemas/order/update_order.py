from typing import Optional
from pydantic import BaseModel

class UpdateOrderSchema(BaseModel):
    assigned_employee_id: Optional[int] = None
    status: Optional[str] = None
    problem_description: Optional[str] = None
    comment: Optional[str] = None
    price: Optional[float] = None
    is_active: Optional[bool] = None
