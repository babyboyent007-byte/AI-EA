from datetime import datetime
import pytz
from ..core import constants

class SessionManager:
    def __init__(self, timezone: str = 'UTC'):
        self.tz = pytz.timezone(timezone)

    def is_market_open(self) -> bool:
        """Basic check for weekend closure."""
        now = datetime.now(self.tz)
        # Friday 22:00 to Sunday 22:00 roughly
        if now.weekday() == 4 and now.hour >= 22:
            return False
        if now.weekday() == 5:
            return False
        if now.weekday() == 6 and now.hour < 22:
            return False
        return True

    def get_current_session(self) -> str:
        """Returns the dominant trading session based on UTC hour."""
        hour = datetime.now(self.tz).hour
        
        if 0 <= hour < 8: return constants.TOKYO
        if 8 <= hour < 13: return constants.LONDON
        if 13 <= hour < 21: return constants.NEWYORK
        return 'TRANSITION'