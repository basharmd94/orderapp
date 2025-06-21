from pydantic import BaseModel
from typing import Optional

class NetSalesWithAllReturnsResponse(BaseModel):
        # Customer Info
   # Customer Info
    xcus: Optional[str] = None
    xorg: Optional[str] = None
    xadd1: Optional[str] = None

    # Sales & Returns
    gross_sales: float = 0.0
    imtemp_returns: float = 0.0
    opcrn_returns: float = 0.0
    net_sales: float = 0.0

    # Monthly Metrics
    number_of_months: int = 0
    avg_monthly_net_sales: float = 0.0

    # This Month
    this_month_net_sales: float = 0.0
    target_sales: float = 0.0
    sales_gap: float = 0.0

    # Offer Message
    offer: Optional[str] = None