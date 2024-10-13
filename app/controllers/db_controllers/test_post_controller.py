from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from models.test_model import Abdef
from controllers.db_controllers.database_controller import DatabaseController
from schemas.test_post_schema import AbdefSchema
import logging
import traceback


class TestPostController(DatabaseController):
    def __init__(self, db: AsyncSession):
        super().__init__()
        self.db = db  # Use the session passed in from the route handler

    async def create_order_abdef(self, zid: int, order: AbdefSchema):
        new_order = Abdef(
            ztime=datetime.utcnow(),
            zutime=datetime.utcnow(),
            zid=zid,
            xtitleord=order.xtitleord,
            xtitledor=order.xtitledor,
            xtitleinv=order.xtitleinv,
            xtitlerec=order.xtitlerec,
            xtitleart=order.xtitleart,
        )

        try:
            self.db.add(new_order)
            await self.db.commit()
            await self.db.refresh(new_order)
        except Exception as e:
            await self.db.rollback()  # Rollback on error
            raise e  # Reraise the exception for further handling