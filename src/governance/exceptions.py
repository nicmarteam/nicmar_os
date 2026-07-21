class GovernanceException(Exception):
    """Excepție de bază pentru erorile de guvernanță AI."""
    pass

class PolicyViolationError(GovernanceException):
    """Aruncată atunci când o cerere încalcă o politică de securitate sau rol."""
    pass

class BudgetExceededError(GovernanceException):
    """Aruncată atunci când s-a depășit bugetul alocat (cost, tool-uri, pași)."""
    pass
