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
            # Search pattern for SQL
            search_pattern = f"%{search_text}%" if search_text else None
            
            # Base query parameters
            params = {
                "zid": zid,
                "search_pattern": search_pattern
            }
            
            # Simplified query to get all manufacturing orders
            query = text("""
            SELECT
                m.zid,
                m.xdatemo as xdate,
                m.xmoord,
                m.xitem,
                c.xdesc,
                m.xqtyprd,
                m.xunit,
                COALESCE(SUM(i.xqty * i.xsign), 0) AS stock,
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
                ) AS last_mo_number,
                ROUND(
                    COALESCE((
                        SELECT SUM(d.xqty * d.xrate)
                        FROM moodt d
                        WHERE d.xmoord = m.xmoord
                        AND d.zid = m.zid
                    ), 0) / NULLIF(m.xqtyprd, 0), 2
                ) AS mo_cost
            FROM 
                moord m
                LEFT JOIN caitem c ON m.xitem = c.xitem AND c.zid = m.zid
                LEFT JOIN imtrn i ON m.xitem = i.xitem AND i.zid = m.zid
            WHERE 
                m.zid = CAST(:zid AS INTEGER)
                AND (
                    CAST(:search_pattern AS TEXT) IS NULL
                    OR m.xmoord::text ILIKE CAST(:search_pattern AS TEXT)
                    OR m.xitem::text ILIKE CAST(:search_pattern AS TEXT)
                    OR c.xdesc::text ILIKE CAST(:search_pattern AS TEXT)
                    OR TO_CHAR(m.xdatemo, 'YYYY-MM-DD') ILIKE CAST(:search_pattern AS TEXT)
                )
            GROUP BY 
                m.zid, m.xdatemo, m.xmoord, m.xitem, c.xdesc, m.xqtyprd, m.xunit
            ORDER BY 
                m.xdatemo DESC, m.xmoord DESC
            """)
            
            # Count query with matching search pattern
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
            all_manufacturing_orders = [dict(row) for row in rows]
            
            # Use pure Python to deduplicate based on MO number
            if all_manufacturing_orders:
                # Create a dictionary to store unique MOs with xmoord as key
                unique_mos = {}
                
                # Keep only the first occurrence of each MO number
                for mo in all_manufacturing_orders:
                    mo_number = mo['xmoord']
                    if mo_number not in unique_mos:
                        unique_mos[mo_number] = mo
                
                # Sort by date and MO number (descending)
                sorted_mos = sorted(
                    unique_mos.values(), 
                    key=lambda x: (x['xdate'], x['xmoord']), 
                    reverse=True
                )
                
                # Apply pagination
                offset = (page - 1) * size
                end_idx = min(offset + size, len(sorted_mos))
                
                # Slice the sorted list to get the current page
                manufacturing_orders = sorted_mos[offset:end_idx]
            else:
                manufacturing_orders = []
            
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
