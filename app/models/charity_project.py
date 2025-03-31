from sqlalchemy import Column, String, Text

from .abstracts import InvestInfoAndDatesAbstractModel
from app.core.config import MAX_NAME_LENGTH


MAX_DESCRIPTION_LEN = 50


class CharityProject(InvestInfoAndDatesAbstractModel):
    name = Column(String(MAX_NAME_LENGTH), unique=True, nullable=False)
    description = Column(Text, nullable=False)

    def __repr__(self):
        return (
            f'{super().__repr__()}, '
            f'{self.name=}, '
            f'{self.description[:MAX_DESCRIPTION_LEN]=}'
        )
