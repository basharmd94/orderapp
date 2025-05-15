from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from models.manufacturing_model import Moord
from schemas.manufacturing_schema import ManufacturingOrderSchema
from typing import List, Dict, Any, Optional, Tuple
from fastapi import Depends, HTTPException, status
from logs import setup_logger
import math

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
            }            # Main query with explicit type casting and ILIKE for search
            query = text("""
            WITH FilteredMO AS (
                SELECT DISTINCT
                    m.zid,
                    m.xdatemo, 
                    m.xmoord, 
                    m.xitem, 
                    m.xqtyprd, 
                    m.xunit
                FROM 
                    moord m
                    LEFT JOIN caitem c ON m.xitem = c.xitem AND c.zid = m.zid
                WHERE 
                    m.zid = CAST(:zid AS INTEGER)
                    AND (
                        CAST(:search_pattern AS TEXT) IS NULL
                        OR m.xmoord::text ILIKE CAST(:search_pattern AS TEXT)
                        OR m.xitem::text ILIKE CAST(:search_pattern AS TEXT)
                        OR c.xdesc::text ILIKE CAST(:search_pattern AS TEXT)                        OR TO_CHAR(m.xdatemo, 'YYYY-MM-DD') ILIKE CAST(:search_pattern AS TEXT)
                    )
                ORDER BY 
                    m.xdatemo DESC, m.xmoord DESC
            ),
            MO_With_Stock AS (
                SELECT
                    m.zid,
                    m.xdatemo,
                    m.xmoord,
                    m.xitem,
                    m.xqtyprd,
                    m.xunit,
                    c.xdesc,
                    COALESCE(SUM(i.xqty * i.xsign), 0) AS stock
                FROM 
                    FilteredMO m
                    LEFT JOIN caitem c ON m.xitem = c.xitem AND c.zid = m.zid
                    LEFT JOIN imtrn i ON m.xitem = i.xitem AND i.zid = m.zid
                GROUP BY 
                    m.zid, m.xdatemo, m.xmoord, m.xitem, c.xdesc, m.xqtyprd, m.xunit
            ),
            MO_Costs AS (
                SELECT
                    moord.xmoord,
                    ROUND(COALESCE(SUM(moodt.xqty * moodt.xrate), 0) / NULLIF(moord.xqtyprd, 0), 2) AS mo_cost
                FROM 
                    moord
                    LEFT JOIN moodt ON moord.xmoord = moodt.xmoord AND moord.zid = moodt.zid
                WHERE 
                    moord.zid = CAST(:zid AS INTEGER)
                GROUP BY 
                    moord.xmoord, 
                    moord.xqtyprd
            ),
            LastMO AS (
                SELECT
                    m.*,
                    (
                        SELECT mo2.xqtyprd
                        FROM moord mo2
                        WHERE mo2.zid = m.zid
                        AND mo2.xitem = m.xitem
                        AND mo2.xdatemo < m.xdatemo
                        ORDER BY mo2.xdatemo DESC
                        LIMIT 1
                    ) AS last_mo_qty,
                    (
                        SELECT mo2.xdatemo
                        FROM moord mo2
                        WHERE mo2.zid = m.zid
                        AND mo2.xitem = m.xitem
                        AND mo2.xdatemo < m.xdatemo
                        ORDER BY mo2.xdatemo DESC
                        LIMIT 1
                    ) AS last_mo_date,
                    (
                        SELECT mo2.xmoord
                        FROM moord mo2
                        WHERE mo2.zid = m.zid
                        AND mo2.xitem = m.xitem
                        AND mo2.xdatemo < m.xdatemo
                        ORDER BY mo2.xdatemo DESC
                        LIMIT 1
                    ) AS last_mo_number
                FROM
                    MO_With_Stock m
            ),            -- Add row numbers for pagination
            NumberedMO AS (
                SELECT
                    m.*,
                    mc.mo_cost,
                    ROW_NUMBER() OVER (ORDER BY m.xdatemo DESC, m.xmoord DESC) as row_num
                FROM
                    LastMO m
                    LEFT JOIN MO_Costs mc ON m.xmoord = mc.xmoord
            )
            SELECT 
                zid,
                xdatemo as xdate,
                xmoord,
                xitem,
                xdesc,
                xqtyprd,
                xunit,
                stock,
                last_mo_qty,
                last_mo_date,
                last_mo_number,
                mo_cost            FROM 
                NumberedMO
            WHERE
                row_num > :offset AND row_num <= (:offset + :limit)
            ORDER BY 
                xdate DESC, xmoord DESC
            """)
            
            # Count query with matching search pattern
            count_query = text("""
            SELECT COUNT(DISTINCT m.xmoord) as total
            FROM moord m
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
            logger.error("Error getting manufacturing orders: from manufacturing_db_controller")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error getting manufacturing orders: from manufacturing_db_controller",
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
            }

            # Query to get MO details with raw materials, rates, and costs
            query = text("""
            WITH mo_query AS (
                SELECT 
                    moodt.xitem, 
                    caitem.xdesc, 
                    moodt.xqty AS raw_qty, 
                    moodt.xrate AS rate, 
                    ROUND(SUM(moodt.xqty * moodt.xrate), 2) AS total_amt,
                    moord.xunit,
                    ROUND(SUM(moodt.xqty * moodt.xrate) / NULLIF(moord.xqtyprd, 0), 2) AS cost_per_item,
                    COALESCE((
                        SELECT SUM(imtrn.xqty * imtrn.xsign)
                        FROM imtrn
                        WHERE imtrn.xitem = moodt.xitem AND imtrn.zid = CAST(:zid AS INTEGER)
                    ), 0) AS stock
                FROM 
                    moord
                    JOIN moodt ON moord.xmoord = moodt.xmoord
                    JOIN caitem ON moodt.xitem = caitem.xitem
                WHERE 
                    moord.zid = CAST(:zid AS INTEGER)
                    AND moodt.zid = CAST(:zid AS INTEGER)
                    AND caitem.zid = CAST(:zid AS INTEGER)
                    AND moord.xmoord = :mo_number
                GROUP BY 
                    moord.xdatemo, 
                    moodt.xitem, 
                    moodt.xqty, 
                    moodt.xrate, 
                    caitem.xdesc, 
                    moord.xqtyprd, 
                    moord.xunit
            )
            SELECT 
                xitem, 
                xdesc,
                xunit, 
                raw_qty, 
                rate, 
                total_amt, 
                cost_per_item,
                stock            FROM 
                mo_query
            ORDER BY
                xitem, raw_qty DESC
            """)
            
            # Execute query
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
