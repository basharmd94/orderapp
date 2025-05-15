from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Dict, Any, Optional, Tuple
from fastapi import HTTPException, status
from logs import setup_logger

logger = setup_logger()

class ManufacturingDBController:
    """Controller for handling manufacturing-related database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_mo(
        self, zid: int, search_text: Optional[str] = None, page: int = 1, size: int = 10
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get manufacturing orders with pagination and filtering.
        
        Args:
            zid: Company ID
            search_text: Optional text to search in item code, item name, date, or MO number
            page: Page number (1-based)
            size: Number of items per page
            
        Returns:
            Tuple containing list of manufacturing orders and total count
        """
        if self.db is None:
            raise Exception("Database session not initialized.")

        try:
            # Calculate offset
            offset = (page - 1) * size
            
            # Base query parameters with type hints
            params = {
                "zid": zid,
                "limit": size,
                "offset": offset,
                "search_pattern": f"%{search_text}%" if search_text else None
            }            # Completely revised query to eliminate duplicates - guaranteed one row per MO number
            query = text("""
            WITH UniqueMOs AS (
                -- First, get exactly one row per MO number (using DISTINCT ON)
                SELECT DISTINCT ON (m.xmoord)
                    m.zid,
                    m.xdatemo,
                    m.xmoord,
                    m.xitem,
                    m.xqtyprd,
                    m.xunit,
                    c.xdesc
                FROM 
                    moord m
                    LEFT JOIN caitem c ON m.xitem = c.xitem AND c.zid = m.zid
                WHERE 
                    m.zid = CAST(:zid AS INTEGER)
                    AND (
                        CAST(:search_pattern AS TEXT) IS NULL
                        OR m.xmoord::text ILIKE CAST(:search_pattern AS TEXT)
                        OR m.xitem::text ILIKE CAST(:search_pattern AS TEXT)
                        OR c.xdesc::text ILIKE CAST(:search_pattern AS TEXT)
                        OR TO_CHAR(m.xdatemo, 'YYYY-MM-DD') ILIKE CAST(:search_pattern AS TEXT)
                    )
                ORDER BY 
                    m.xmoord, m.xdatemo DESC
            ),
            RankedMOs AS (
                -- Add row numbers for pagination
                SELECT
                    *,
                    ROW_NUMBER() OVER (ORDER BY xdatemo DESC, xmoord DESC) AS rnum
                FROM
                    UniqueMOs
            ),
            PagedMOs AS (
                -- Apply pagination
                SELECT 
                    *
                FROM
                    RankedMOs
                WHERE
                    rnum > :offset AND rnum <= (:offset + :limit)
            ),
            StockInfo AS (
                -- Get stock information for items in our page
                SELECT
                    i.xitem,
                    COALESCE(SUM(i.xqty * i.xsign), 0) AS stock
                FROM
                    imtrn i
                WHERE
                    i.zid = CAST(:zid AS INTEGER)
                    AND i.xitem IN (SELECT xitem FROM PagedMOs)
                GROUP BY
                    i.xitem
            ),
            CostInfo AS (
                -- Calculate costs for MOs in our page
                SELECT
                    d.xmoord,
                    ROUND(SUM(d.xqty * d.xrate) / NULLIF(m.xqtyprd, 0), 2) AS mo_cost
                FROM
                    moord m
                    JOIN moodt d ON m.xmoord = d.xmoord AND m.zid = d.zid
                WHERE
                    m.zid = CAST(:zid AS INTEGER)
                    AND m.xmoord IN (SELECT xmoord FROM PagedMOs)
                GROUP BY
                    d.xmoord, m.xqtyprd
            ),
            LastMOInfo AS (
                -- Find previous MO for each item
                SELECT
                    curr.xitem,
                    prev.xqtyprd AS last_mo_qty,
                    prev.xdatemo AS last_mo_date,
                    prev.xmoord AS last_mo_number
                FROM
                    PagedMOs curr
                    LEFT JOIN LATERAL (
                        SELECT
                            mo.xqtyprd,
                            mo.xdatemo,
                            mo.xmoord
                        FROM
                            moord mo
                        WHERE
                            mo.zid = CAST(:zid AS INTEGER)
                            AND mo.xitem = curr.xitem
                            AND mo.xdatemo < curr.xdatemo
                        ORDER BY
                            mo.xdatemo DESC, mo.xmoord DESC
                        LIMIT 1
                    ) prev ON true
            )
            -- Final result combining all data
            SELECT
                p.zid,
                p.xdatemo AS xdate,
                p.xmoord,
                p.xitem,
                p.xdesc,
                p.xqtyprd,
                p.xunit,
                COALESCE(s.stock, 0) AS stock,
                l.last_mo_qty,
                l.last_mo_date,
                l.last_mo_number,
                COALESCE(c.mo_cost, 0) AS mo_cost
            FROM
                PagedMOs p
                LEFT JOIN StockInfo s ON p.xitem = s.xitem
                LEFT JOIN CostInfo c ON p.xmoord = c.xmoord
                LEFT JOIN LastMOInfo l ON p.xitem = l.xitem
            ORDER BY
                p.xdatemo DESC, p.xmoord DESC
            """)
              # Optimized count query with matching search pattern
            count_query = text("""
            SELECT 
                COUNT(DISTINCT m.xmoord) as total
            FROM 
                moord m
                LEFT JOIN caitem c ON m.xitem = c.xitem AND c.zid = m.zid
            WHERE 
                m.zid = CAST(:zid AS INTEGER)
                AND (
                    CAST(:search_pattern AS TEXT) IS NULL
                    OR m.xmoord::text ILIKE CAST(:search_pattern AS TEXT)
                    OR m.xitem::text ILIKE CAST(:search_pattern AS TEXT)
                    OR c.xdesc::text ILIKE CAST(:search_pattern AS TEXT)
                    OR TO_CHAR(m.xdatemo, 'YYYY-MM-DD') ILIKE CAST(:search_pattern AS TEXT)
                )
            """)
            
            # Execute queries
            result = await self.db.execute(query, params)
            rows = result.mappings().all()
            count_result = await self.db.execute(count_query, params)
            total = count_result.scalar()
            
            # Convert to list of dictionaries
            manufacturing_orders = [dict(row) for row in rows]
            
            return manufacturing_orders, total
            
        except Exception as e:
            logger.error(f"Error getting manufacturing orders: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting manufacturing orders: {str(e)}",
            )

    async def get_mo_detail(self, zid: int, mo_number: str) -> List[Dict[str, Any]]:
        """
        Get detailed information about a specific manufacturing order.
        
        Args:
            zid: Company ID
            mo_number: Manufacturing Order Number
            
        Returns:
            List of dictionaries containing MO detail items
        """
        if self.db is None:
            raise Exception("Database session not initialized.")

        try:
            # Parameter dictionary for SQL query
            params = {
                "zid": zid,
                "mo_number": mo_number
            }            # Optimized query to get MO details with raw materials, rates, and costs
            query = text("""
            WITH item_stock AS (
                SELECT 
                    xitem,
                    COALESCE(SUM(xqty * xsign), 0) AS stock
                FROM 
                    imtrn
                WHERE 
                    zid = CAST(:zid AS INTEGER)
                GROUP BY 
                    xitem
            )
            SELECT 
                moodt.xitem, 
                caitem.xdesc, 
                moodt.xqty AS raw_qty, 
                moodt.xrate AS rate, 
                ROUND(moodt.xqty * moodt.xrate, 2) AS total_amt,
                moord.xunit,
                ROUND(
                    (SELECT COALESCE(SUM(od.xqty * od.xrate), 0)
                     FROM moodt od
                     WHERE od.xmoord = moord.xmoord AND od.zid = CAST(:zid AS INTEGER)) 
                    / NULLIF(moord.xqtyprd, 0), 2
                ) AS cost_per_item,
                COALESCE(ist.stock, 0) AS stock
            FROM 
                moord
                JOIN moodt ON moord.xmoord = moodt.xmoord AND moord.zid = moodt.zid
                JOIN caitem ON moodt.xitem = caitem.xitem AND caitem.zid = CAST(:zid AS INTEGER)
                LEFT JOIN item_stock ist ON moodt.xitem = ist.xitem
            WHERE 
                moord.zid = CAST(:zid AS INTEGER)
                AND moodt.zid = CAST(:zid AS INTEGER)
                AND moord.xmoord = :mo_number
            ORDER BY
                moodt.xitem, moodt.xqty DESC
            """)            # Execute query
            result = await self.db.execute(query, params)
            rows = result.mappings().all()
            
            # Convert to list of dictionaries
            mo_details = [dict(row) for row in rows]
            
            if not mo_details:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Manufacturing order '{mo_number}' not found for company {zid}"
                )
            
            return mo_details
            
        except HTTPException:
            # Re-raise HTTP exceptions without modifying them
            raise
        except Exception as e:
            logger.error(f"Error getting manufacturing order details: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting manufacturing order details: {str(e)}"
            )
