"""
Compliance rule abstractions and concrete policy rules.
"""

class BaseRule:
    """
    Abstract Base Class for all compliance evaluation rules.
    """
    pass

class EncryptionRequiredRule(BaseRule):
    pass

class LoggingRequiredRule(BaseRule):
    pass

class PublicExposureForbiddenRule(BaseRule):
    pass
