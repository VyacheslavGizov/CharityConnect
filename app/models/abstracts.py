from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Integer

from app.core.db import Base


class InvestInfoAndDatesAbstractModel(Base):
    __abstract__ = True

    full_amount = Column(Integer, default=0)
    invested_amount = Column(Integer, default=0)
    fully_invested = Column(Boolean, default=False)
    create_date = Column(DateTime, default=datetime.now)
    close_date = Column(DateTime)

    __table_args__ = (
        CheckConstraint('full_amount > 0', name='positive full_amount'),
        CheckConstraint(
            '0 <= invested_amount <= full_amount',
            name='invested_amount gte 0 and lte full_amount'),
    )

    def __repr__(self):
        return (
            f'{type(self).__name__}: '
            f'{self.id=}, '
            f'{self.full_amount=}, '
            f'{self.invested_amount=}, '
            f'{self.fully_invested=}, '
            f'{self.create_date=}, '
            f'{self.close_date=}'
        )
