from sqlalchemy import func, select, or_, cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.functions import sum, coalesce
from datetime import datetime, timedelta
from typing import Optional
# Models
from models.orders_model import Opord, Opodt, Imtemptrn, Imtemptdt, Opcrn, Opcdt
from models.customers_model import Cacus

# Schema
from schemas.sales_return_schema import NetSalesWithAllReturnsResponse


class SalesReturnDBController:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_net_sales_with_all_returns(
        self, zid: int, customer_id: str
    ) -> "NetSalesWithAllReturnsResponse":
        """
        Calculate Net Sales = Gross Sales – (Imtemptrn Returns + Opcrn Returns)
        Also calculates:
          - Avg per order net sales = Yearly Net Sales / Total Order Count
          - Target Sales = Net Sales * (1 + xmonper / 100)
          - Gap = target – this_month_net_sales
          - Offer from Cacus.xcreditr if gap <= 0, else motivational message
        """

        now = datetime.now()
        from_date = datetime(now.year - 1, 1, 1)
        to_date = datetime(now.year, now.month, 1) - timedelta(days=1)

        # This month date range
        this_month_start = datetime(now.year, now.month, 1)
        this_month_end = (
            datetime(now.year, now.month + 1, 1) - timedelta(days=1)
            if now.month < 12 else datetime(now.year, 12, 31)
        )

        # --- CUSTOMER INFO ---
        cacus_query = select(
            Cacus.xcus, Cacus.xorg, Cacus.xadd1,
            Cacus.xcreditr, Cacus.xmonper, Cacus.xmondiscper,
            Cacus.xisgotdefault, Cacus.xisgotmon
        ).where(
            Cacus.zid == zid,
            Cacus.xcus == customer_id
        ).limit(1)

        cacus_result = await self.db.execute(cacus_query)
        customer_info = cacus_result.first()

        if not customer_info:
            return NetSalesWithAllReturnsResponse()

        # --- GROSS SALES ---
        gross_sales_subq = (
            select(func.sum(Opodt.xlineamt))
            .join(Opord, Opord.xordernum == Opodt.xordernum)
            .where(
                Opord.zid == zid,
                Opodt.zid == zid,
                Opord.xcus == customer_id,
                Opord.xdate.between(from_date, to_date),
            )
            .scalar_subquery()
        )

        # --- RETURNS: imtemptrn ---
        imtemp_return_subq = (
            select(func.sum(Imtemptdt.xlineamt))
            .join(Imtemptrn, Imtemptrn.ximtmptrn == Imtemptdt.ximtmptrn)
            .where(
                Imtemptrn.zid == zid,
                Imtemptdt.zid == zid,
                Imtemptrn.xcus == customer_id,
                Imtemptrn.xdate.between(from_date, to_date),
                or_(
                    Imtemptrn.ximtmptrn.like('%RECA%'),
                    Imtemptrn.ximtmptrn.like('%SRE-%'),
                    Imtemptrn.ximtmptrn.like('%RECT-%'),
                    Imtemptrn.ximtmptrn.like('%DSR-%')
                )
            )
            .scalar_subquery()
        )

        # --- RETURNS: opcrn ---
        opcrn_return_subq = (
            select(func.sum(Opcdt.xlineamt))
            .join(Opcrn, Opcrn.xcrnnum == Opcdt.xcrnnum)
            .where(
                Opcrn.zid == zid,
                Opcdt.zid == zid,
                Opcrn.xcus == customer_id,
                Opcrn.xdate.between(from_date, to_date)
            )
            .scalar_subquery()
        )

        # --- THIS MONTH NET SALES ---
        this_month_gross_sales = (
            select(func.sum(Opodt.xlineamt))
            .join(Opord, Opord.xordernum == Opodt.xordernum)
            .where(
                Opord.zid == zid,
                Opodt.zid == zid,
                Opord.xcus == customer_id,
                Opord.xdate.between(this_month_start, this_month_end),
            )
            .scalar_subquery()
        )

        this_month_imtemp_return = (
            select(func.sum(Imtemptdt.xlineamt))
            .join(Imtemptrn, Imtemptrn.ximtmptrn == Imtemptdt.ximtmptrn)
            .where(
                Imtemptrn.zid == zid,
                Imtemptdt.zid == zid,
                Imtemptrn.xcus == customer_id,
                Imtemptrn.xdate.between(this_month_start, this_month_end),
                or_(
                    Imtemptrn.ximtmptrn.like('%RECA%'),
                    Imtemptrn.ximtmptrn.like('%SRE-%'),
                    Imtemptrn.ximtmptrn.like('%RECT-%'),
                    Imtemptrn.ximtmptrn.like('%DSR-%')
                )
            )
            .scalar_subquery()
        )

        this_month_opcrn_return = (
            select(func.sum(Opcdt.xlineamt))
            .join(Opcrn, Opcrn.xcrnnum == Opcdt.xcrnnum)
            .where(
                Opcrn.zid == zid,
                Opcdt.zid == zid,
                Opcrn.xcus == customer_id,
                Opcrn.xdate.between(this_month_start, this_month_end)
            )
            .scalar_subquery()
        )

        # --- CUSTOMER ORDER COUNT ---
        customer_order_count = (
            select(func.count(Opord.xordernum))
            .join(Opodt, Opodt.xordernum == Opord.xordernum)
            .where(
                Opord.zid == zid,
                Opodt.zid == zid,
                Opord.xcus == customer_id,
                Opord.xdate.between(from_date, to_date)
            )
            .scalar_subquery()
        )

        # Final query for metrics
        stmt = select(
            coalesce(gross_sales_subq, 0).label("gross_sales"),
            coalesce(imtemp_return_subq, 0).label("imtemp_returns"),
            coalesce(opcrn_return_subq, 0).label("opcrn_returns"),
            (
                coalesce(gross_sales_subq, 0)
                - coalesce(imtemp_return_subq, 0)
                - coalesce(opcrn_return_subq, 0)
            ).label("net_sales"),
            coalesce(customer_order_count, 0).label("customer_order_count"),
            (
                (
                    coalesce(gross_sales_subq, 0)
                    - coalesce(imtemp_return_subq, 0)
                    - coalesce(opcrn_return_subq, 0)
                ) / func.nullif(customer_order_count, 0)
            ).label("avg_per_order_net_sales"),
            (
                coalesce(this_month_gross_sales, 0)
                - coalesce(this_month_imtemp_return, 0)
                - coalesce(this_month_opcrn_return, 0)
            ).label("this_month_net_sales")
        )

        try:
            result = await self.db.execute(stmt)
            row = result.first()

            if not row:
                return NetSalesWithAllReturnsResponse(
                    xcus=customer_info.xcus,
                    xorg=customer_info.xorg,
                    xadd1=customer_info.xadd1
                )

            # Extract values safely
            net_sales = float(row.net_sales)
            this_month_net_sales = float(row.this_month_net_sales)
            customer_order_count = int(row.customer_order_count)
            avg_per_order_net_sales = float(row.avg_per_order_net_sales) if row.avg_per_order_net_sales is not None else 0.0

            # Get xmonper with fallback
            xmonper = float(customer_info.xmonper) if customer_info.xmonper not in (None, '') else 0.0
            xmondiscper = float(customer_info.xmondiscper) if customer_info.xmondiscper not in (None, '') else 0.0

            # Boolean conversion for flags
            # Convert string flags safely
            xisgotdefault = None
            if customer_info.xisgotdefault not in (None, '', 'null', 'None'):
                xisgotdefault = customer_info.xisgotdefault.lower() == 'true'

            xisgotmon = None
            if customer_info.xisgotmon not in (None, '', 'null', 'None'):
                xisgotmon = customer_info.xisgotmon.lower() == 'true'


            # Calculate monthly target: avg + percentage increase
            this_month_target_sales = avg_per_order_net_sales * (1 + xmonper / 100)
            # Compare actual vs target
            sales_gap = this_month_target_sales - this_month_net_sales

            # Build offers using private methods
            default_offer = self._build_default_offer(customer_info.xcreditr, xisgotdefault)
            monitory_offer = self._build_monitory_offer(xmondiscper, xisgotmon)

            # Final offer logic
            if sales_gap <= 0:
                offer_value = default_offer if xisgotdefault else monitory_offer if xisgotmon else "No offer"
            else:
                offer_value = f"You are Tk- {abs(round(sales_gap))} away from getting {default_offer if xisgotdefault else monitory_offer if xisgotmon else 'an offer'}"

            return NetSalesWithAllReturnsResponse(
                # Customer Info
                xcus=customer_info.xcus,
                xorg=customer_info.xorg,
                xadd1=customer_info.xadd1,
                xmonper=xmonper,
                xcreditr=customer_info.xcreditr,
                xmondiscper=xmondiscper,
                xisgotdefault=xisgotdefault,
                xisgotmon=xisgotmon,

                # Sales & Returns
                yearly_gross_sales=round(float(row.gross_sales), 2),
                yearly_imtemp_returns=round(float(row.imtemp_returns), 2),
                yearly_opcrn_returns=round(float(row.opcrn_returns), 2),
                yearly_net_sales=round(net_sales, 2),

                # Order Metrics
                yearly_customer_order_count=int(row.customer_order_count),
                avg_per_order_net_sales=round(avg_per_order_net_sales, 2),

                # This Month
                this_month_net_sales=round(this_month_net_sales, 2),
                this_month_target_sales=round(this_month_target_sales, 2),
                sales_gap=round(sales_gap, 2),

                # Offers
                default_offer=default_offer,
                monitory_offer=monitory_offer,
                offer=offer_value
            )
        except Exception as e:
            raise e
        
    def _build_default_offer(self, xcreditr: str, is_received: Optional[bool]) -> str:
        if is_received is True:
            return f"You already got the {xcreditr.strip()}" if xcreditr and xcreditr.strip() else "You already got the default offer"
        elif is_received is False:
            return xcreditr.strip() if xcreditr and xcreditr.strip() else "No default offer"
        else:  # is_received is None
            return "No default offer"
        
    def _build_monitory_offer(self, xmondiscper: float, is_received: Optional[bool]) -> str:
        if is_received is True:
            return f"You already got the {xmondiscper:.0f}% discount" if xmondiscper > 0 else "You already got the monitory offer"
        elif is_received is False:
            return f"You will get {xmondiscper:.0f}% discount on your next purchase" if xmondiscper > 0 else "No monitory offer"
        else:  # is_received is None
            return "No monitory offer"