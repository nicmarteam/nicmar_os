class AgentError(Exception):
    """Eroare de bază pentru subsistemul de agenți."""
    pass

class AgentMaxStepsExceededError(AgentError):
    """Aruncată când agentul depășește numărul maxim de pași permisi."""
    pass

class AgentPolicyViolationError(AgentError):
    """Aruncată când se încalcă o politică de siguranță a agentului."""
    pass

class AgentExecutionError(AgentError):
    """Aruncată când apare o eroare în timpul execuției unui pas."""
    pass
