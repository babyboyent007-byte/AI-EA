class AI_EA_Error(Exception): pass
class MT5ConnectionError(AI_EA_Error): pass
class DataValidationError(AI_EA_Error): pass
class ModelNotFoundError(AI_EA_Error): pass
class RiskViolationError(AI_EA_Error): pass