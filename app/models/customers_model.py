from database import Base
from sqlalchemy import Column, Integer, String, Numeric, func


class Cacus(Base):
    __tablename__ = "cacus"

    zid = Column(Integer, primary_key=True, index=True)
    xcus = Column(String, primary_key=True, index=True)
    xorg = Column(String)
    xadd1 = Column(String)
    xcity = Column(String, index=True)
    xstate = Column(String, index=True)
    xmobile = Column(String, index=True)
    xtaxnum = Column(String, index=True)
    xsp = Column(String, index=True)
    xsp1 = Column(String, index=True)
    xsp2 = Column(String, index=True)
    xsp3 = Column(String, index=True)
    # For Offer Columns
    # Offer Columns
    xtitle = Column(String)  # Customer segment title (e.g., 'Developing-1')
    xfax = Column(String)  # Segmentation score between 0.00 to 1.00
    xcreditr = Column(String)  # Default offer description (e.g., 'Free Tshirt')
    xmonper = Column(Numeric(5, 2))  # Monthly monitoring extra sale % (e.g., 5.00)
    xmondiscper = Column(Numeric(5, 2))  # Monthly discount % (e.g., 2.00)
    xisgotmon = Column(String)  # 'True' or 'False' if customer got monitoring offer
    xisgotdefault = Column(String)  # 'True' or 'False' if customer got default offer