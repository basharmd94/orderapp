from sqlalchemy import func, select, or_,  extract, Integer, Numeric, cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.functions import sum, coalesce
from datetime import datetime, timedelta

# Models
from models.orders_model import Opord, Opodt, Imtemptrn, Imtemptdt, Opcrn, Opcdt
from models.customers_model import Cacus
# Schema
from schemas.sales_return_schema import NetSalesWithAllReturnsResponse

class SalesReturnDBController:
    def __init__(self, db: AsyncSession):
        self.db = db  # Use the session passed in from the route handler

    async def get_net_sales_with_all_returns(
        self, zid: int, customer_id: str
    ) -> "NetSalesWithAllReturnsResponse":
        """
        Calculate Net Sales = Gross Sales – (Imtemptrn Returns + Opcrn Returns)
        Also calculates:
          - This month net sales
          - Target (avg_monthly_net_sales + 1000)
          - Gap = target – this_month_net_sales
          - Offer from Cacus.xcreditr if gap <= 0, else motivational message
        """

        now = datetime.now()
        from_date = datetime(now.year - 1, 1, 1)  # Jan 1 of last year
        to_date = datetime(now.year, now.month, 1) - timedelta(days=1)  # Last day of previous month

        # This month date range
        this_month_start = datetime(now.year, now.month, 1)
        this_month_end = (
            datetime(now.year, now.month + 1, 1) - timedelta(days=1)
            if now.month < 12 else datetime(now.year, 12, 31)
        )

        # --- CUSTOMER INFO ---
        cacus_query = select(Cacus.xcus, Cacus.xorg, Cacus.xadd1, Cacus.xcreditr).where(
            Cacus.zid == zid,
            Cacus.xcus == customer_id
        ).limit(1)

        cacus_result = await self.db.execute(cacus_query)
        customer_info = cacus_result.first()

        # If no customer found, return early
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

        # Number of months between from_date and to_date
        num_months_expr = (
            extract("year", func.age(to_date, from_date)) * 12
            + extract("month", func.age(to_date, from_date))
            + 1
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
            num_months_expr.cast(Integer).label("number_of_months"),
            (
                (
                    coalesce(gross_sales_subq, 0)
                    - coalesce(imtemp_return_subq, 0)
                    - coalesce(opcrn_return_subq, 0)
                ) / cast(num_months_expr, Numeric)
            ).label("avg_monthly_net_sales"),
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

            # Compute target and gap
            avg_monthly_net_sales = float(row.avg_monthly_net_sales) if row.avg_monthly_net_sales else 0.0
            this_month_net_sales = float(row.this_month_net_sales) if row.this_month_net_sales else 0.0

            target_sales = avg_monthly_net_sales + 1000
            sales_gap = target_sales - this_month_net_sales

            # Get base offer from Cacus.xcreditr with fallback
            base_offer = "Free T-Shirt"  # Default fallback
            if customer_info.xcreditr and customer_info.xcreditr.strip():
                base_offer = customer_info.xcreditr.strip()

            # Build offer message
            if sales_gap <= 0:
                offer_value = base_offer
            else:
                offer_value = f"You are Tk- {abs(round(sales_gap))} away from getting {base_offer}"

            return NetSalesWithAllReturnsResponse(
                # Customer Info
                xcus=customer_info.xcus,
                xorg=customer_info.xorg,
                xadd1=customer_info.xadd1,

                # Sales & Returns
                gross_sales=float(row.gross_sales),
                imtemp_returns=float(row.imtemp_returns),
                opcrn_returns=float(row.opcrn_returns),
                net_sales=float(row.net_sales),

                # Monthly Metrics
                number_of_months=int(row.number_of_months),
                avg_monthly_net_sales=round(avg_monthly_net_sales, 2),

                # This Month
                this_month_net_sales=round(this_month_net_sales, 2),
                target_sales=round(target_sales, 2),
                sales_gap=round(sales_gap, 2),

                # Offer
                offer=offer_value
            )
        except Exception as e:
            raise e