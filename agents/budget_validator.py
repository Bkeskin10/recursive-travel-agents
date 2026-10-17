
from decimal import Decimal, InvalidOperation


def validate_budget(budget_limit, expenses=None, stated_total=None):
    """
    Validate a structured budget.

    expenses example:
        {
            "food": 100,
            "transport": 35,
            "activities": 20
        }

    Returns PASS, FAIL, or NOT_CHECKED.
    """

    if expenses is None:
        return {
            "status": "NOT_CHECKED",
            "message": "No structured expenses were supplied.",
            "total": None,
            "remaining": None,
        }

    try:
        limit = Decimal(str(budget_limit))

        if limit < 0:
            raise ValueError("Budget cannot be negative")

        if not isinstance(expenses, dict) or not expenses:
            raise ValueError("Expenses must be a nonempty dictionary")

        amounts = {}

        for category, value in expenses.items():
            amount = Decimal(str(value))

            if not amount.is_finite() or amount < 0:
                raise ValueError(
                    f"Invalid expense for {category}"
                )

            amounts[category] = amount

        total = sum(amounts.values(), Decimal("0"))
        remaining = limit - total

        issues = []

        if total > limit:
            issues.append(
                f"Budget exceeded by ${-remaining:.2f}"
            )

        if stated_total is not None:
            reported = Decimal(str(stated_total))

            if not reported.is_finite():
                raise ValueError("Invalid stated total")

            if abs(reported - total) > Decimal("0.01"):
                issues.append(
                    f"Reported total ${reported:.2f} "
                    f"does not match calculated total ${total:.2f}"
                )

        status = "FAIL" if issues else "PASS"

        return {
            "status": status,
            "message": "; ".join(issues) if issues
                       else "Budget arithmetic validated.",
            "total": float(total),
            "remaining": float(remaining),
            "breakdown": {
                key: float(value)
                for key, value in amounts.items()
            },
        }

    except (InvalidOperation, ValueError, TypeError) as exc:
        return {
            "status": "FAIL",
            "message": f"Invalid budget data: {exc}",
            "total": None,
            "remaining": None,
        }
