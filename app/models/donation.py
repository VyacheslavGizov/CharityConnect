from sqlalchemy import Column, Text, ForeignKey, Integer

from .abstracts import InvestInfoAndDatesAbstractModel


MAX_COMMENT_LEN = 50


class Donation(InvestInfoAndDatesAbstractModel):
    user_id = Column(
        Integer,
        ForeignKey('user.id', name='fk_donation_user_id_user')
    )
    comment = Column(Text)

    def __repr__(self):
        comment = self.comment[:MAX_COMMENT_LEN] if self.comment else None
        return (
            f'{super().__repr__()}, '
            f'{self.user_id=}, '
            f'self.comment={comment}'
        )
