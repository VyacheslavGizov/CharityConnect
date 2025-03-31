from datetime import datetime

from app.models.abstracts import InvestInfoAndDatesAbstractModel


def donations_distribution(
        target: InvestInfoAndDatesAbstractModel,
        sources: list[InvestInfoAndDatesAbstractModel]
) -> list[InvestInfoAndDatesAbstractModel]:
    changed = []
    for source in sources:
        invested_amount = min(
            target.full_amount - target.invested_amount,
            source.full_amount - source.invested_amount)
        for item in [target, source]:
            item.invested_amount += invested_amount
            if item.invested_amount == item.full_amount:
                item.fully_invested = True
                item.close_date = datetime.now()
        changed.append(source)
        if target.fully_invested:
            break
    return changed
