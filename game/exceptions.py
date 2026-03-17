"""
Custom exception hierarchy for the Wrestling RPG game.

All game-specific exceptions inherit from WrestlingRPGError,
providing a clear error hierarchy for the application.
"""


class WrestlingRPGError(Exception):
    """Base exception for all Wrestling RPG errors.
    
    All custom exceptions in this game inherit from this class,
    allowing callers to catch all game-specific errors with a single handler.
    """
    pass


class InsufficientEnergyError(WrestlingRPGError):
    """Raised when a wrestler tries to use a move without enough energy.
    
    Args:
        required: Energy points required for the move.
        available: Energy points currently available.
    """
    def __init__(self, required: int, available: int) -> None:
        self.required = required
        self.available = available
        super().__init__(
            f"Brak energii! Wymagane: {required}, dostępne: {available}"
        )


class ItemRequirementError(WrestlingRPGError):
    """Raised when a wrestler does not meet item requirements.
    
    Args:
        item_name: Name of the item that cannot be equipped.
        reason: Specific reason why the requirement is not met.
    """
    def __init__(self, item_name: str, reason: str) -> None:
        self.item_name = item_name
        self.reason = reason
        super().__init__(
            f"Nie można założyć '{item_name}': {reason}"
        )


class InvalidStatValueError(WrestlingRPGError):
    """Raised when a stat value would go below zero or above maximum.
    
    Args:
        stat_name: Name of the statistic.
        value: The invalid value that was attempted.
    """
    def __init__(self, stat_name: str, value: int) -> None:
        self.stat_name = stat_name
        self.value = value
        super().__init__(
            f"Nieprawidłowa wartość statystyki '{stat_name}': {value}"
        )


class InvalidMoveError(WrestlingRPGError):
    """Raised when a wrestler tries to use a move they don't own.
    
    Args:
        move_name: Name of the move attempted.
    """
    def __init__(self, move_name: str) -> None:
        self.move_name = move_name
        super().__init__(f"Nieznany ruch: '{move_name}'")


class FinisherNotAvailableError(WrestlingRPGError):
    """Raised when finisher is attempted but opponent is above 35% HP.
    
    Args:
        opponent_hp_pct: Current HP percentage of the opponent.
    """
    def __init__(self, opponent_hp_pct: float) -> None:
        self.opponent_hp_pct = opponent_hp_pct
        super().__init__(
            f"Finisher niedostępny! Rywal ma {opponent_hp_pct:.0f}% HP (wymagane < 35%)"
        )
