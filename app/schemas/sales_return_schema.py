from pydantic import BaseModel
from typing import Optional

class NetSalesWithAllReturnsResponse(BaseModel):
    # Customer Info
    xcus: Optional[str] = None
    xorg: Optional[str] = None
    xadd1: Optional[str] = None

    # Percentage Fields
    xmonper: Optional[float] = 0.0          # Target % (e.g., 10 for 10%)
    xmondiscper: Optional[float] = 0.0     # Monetary discount %
    xcreditr: Optional[str] = None         # Default Offer Text

    # Boolean Flags
    xisgotdefault: Optional[bool] = False  # Got default offer?
    xisgotmon: Optional[bool] = False      # Got monetary offer?

    # Yearly Metrics
    yearly_gross_sales: float = 0.0
    yearly_imtemp_returns: float = 0.0
    yearly_opcrn_returns: float = 0.0
    yearly_net_sales: float = 0.0
    yearly_customer_order_count: int = 0
    avg_per_order_net_sales: float = 0.0   # Net sales ÷ order count

    # Monthly Metrics
    this_month_net_sales: float = 0.0
    this_month_target_sales: float = 0.0   # Based on avg + xmonper%
    sales_gap: float = 0.0                 # Difference between actual vs target

    # Offers
    default_offer: Optional[str] = "No default offer"
    monitory_offer: Optional[str] = "No monitory offer"
    offer: Optional[str] = "No offer"