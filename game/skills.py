"""
Skill system for Wrestling RPG.

Contains base Skill class and concrete implementations for
wrestling moves (ActiveSkill) and passive class bonuses (PassiveSkill).
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.characters import Wrestler


class Skill(ABC):
    """Abstract base class for all skills (moves and passives).
    
    Defines the common interface that all skills must implement.
    
    Args:
        name: Display name of the skill.
        description: Human-readable description of what the skill does.
    """

    # Class attribute: all registered skill names for duck typing
    skill_registry: list[str] = []

    def __init__(self, name: str, description: str) -> None:
        self._name = name
        self._description = description
        Skill.skill_registry.append(name)

    @property
    def name(self) -> str:
        """Return skill name."""
        return self._name

    @property
    def description(self) -> str:
        """Return skill description."""
        return self._description

    @abstractmethod
    def apply(self, user: "Wrestler", target: "Wrestler | None" = None) -> str:
        """Apply the skill effect.
        
        Args:
            user: The wrestler using this skill.
            target: Optional target wrestler (for offensive moves).
            
        Returns:
            String describing what happened when the skill was applied.
        """
        pass

    def __str__(self) -> str:
        return f"{self._name}: {self._description}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self._name!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Skill):
            return NotImplemented
        return self._name == other._name

    def __lt__(self, other: "Skill") -> bool:
        """Allow sorting skills by name."""
        return self._name < other._name


class ActiveSkill(Skill):
    """An active wrestling move that costs energy and deals damage.
    
    Args:
        name: Name of the wrestling move.
        energy_cost: Energy points consumed when used.
        damage_multiplier: Multiplier applied to the user's strength for damage.
        is_finisher: Whether this move is a finisher (requires opponent < 35% HP).
    """

    def __init__(
        self,
        name: str,
        energy_cost: int,
        damage_multiplier: float,
        is_finisher: bool = False,
    ) -> None:
        desc = (
            f"Finisher | Koszt: {energy_cost} energii | DMG: {damage_multiplier}x Siła"
            if is_finisher
            else f"Ruch | Koszt: {energy_cost} energii | DMG: {damage_multiplier}x Siła"
        )
        super().__init__(name, desc)
        self._energy_cost = energy_cost
        self._damage_multiplier = damage_multiplier
        self._is_finisher = is_finisher

    @property
    def energy_cost(self) -> int:
        """Energy cost of this move."""
        return self._energy_cost

    @property
    def damage_multiplier(self) -> float:
        """Damage multiplier applied to user's strength."""
        return self._damage_multiplier

    @property
    def is_finisher(self) -> bool:
        """Whether this is a finisher move."""
        return self._is_finisher

    def calculate_damage(self, user_strength: int) -> int:
        """Calculate raw damage dealt by this move.
        
        Args:
            user_strength: Effective strength of the attacking wrestler.
            
        Returns:
            Integer damage value (rounded).
        """
        return int(user_strength * self._damage_multiplier)

    def apply(self, user: "Wrestler", target: "Wrestler | None" = None) -> str:
        """Execute this move: deduct energy from user, deal damage to target.
        
        Args:
            user: Attacking wrestler.
            target: Defending wrestler (required for active moves).
            
        Returns:
            Battle log string describing the result.
        """
        from game.exceptions import InsufficientEnergyError, FinisherNotAvailableError

        if user.current_energy < self._energy_cost:
            raise InsufficientEnergyError(self._energy_cost, user.current_energy)

        if target is None:
            return f"{user.name} wykonuje {self._name} w powietrze..."

        if self._is_finisher:
            hp_pct = (target.current_hp / target.max_hp) * 100
            if hp_pct >= 35:
                raise FinisherNotAvailableError(hp_pct)

        user.spend_energy(self._energy_cost)
        dmg = self.calculate_damage(user.effective_strength)
        target.take_damage(dmg)

        if self._is_finisher:
            return (
                f"💥 FINISHER! {user.name} wykonuje {self._name}! "
                f"Zadano {dmg} obrażeń! {target.name} zostaje zniszczony!"
            )
        return (
            f"🤼 {user.name} używa {self._name}! "
            f"Zadano {dmg} obrażeń. {target.name} ma {target.current_hp}/{target.max_hp} HP."
        )

    def __repr__(self) -> str:
        return (
            f"ActiveSkill(name={self._name!r}, cost={self._energy_cost}, "
            f"mult={self._damage_multiplier}, finisher={self._is_finisher})"
        )


class PassiveSkill(Skill):
    """A passive skill that permanently modifies wrestler statistics.
    
    Passive skills are applied once when the wrestler is created
    and contribute to effective stat calculations.
    
    Args:
        name: Name of the passive bonus.
        description: What the passive does.
        strength_bonus: Flat bonus to strength.
        dexterity_bonus: Flat bonus to dexterity.
        hp_bonus_pct: Percentage bonus to max HP (e.g. 10 = +10%).
        energy_bonus_pct: Percentage bonus to max energy.
    """

    def __init__(
        self,
        name: str,
        description: str,
        strength_bonus: int = 0,
        dexterity_bonus: int = 0,
        hp_bonus_pct: float = 0.0,
        energy_bonus_pct: float = 0.0,
    ) -> None:
        super().__init__(name, description)
        self.strength_bonus = strength_bonus
        self.dexterity_bonus = dexterity_bonus
        self.hp_bonus_pct = hp_bonus_pct
        self.energy_bonus_pct = energy_bonus_pct

    def apply(self, user: "Wrestler", target: "Wrestler | None" = None) -> str:
        """Passive skills do not have active application – stats computed separately.
        
        Returns:
            Info string about the passive skill.
        """
        return f"[Pasywna] {self._name}: {self._description}"

    def __repr__(self) -> str:
        return (
            f"PassiveSkill(name={self._name!r}, str={self.strength_bonus}, "
            f"dex={self.dexterity_bonus}, hp_pct={self.hp_bonus_pct})"
        )


# ---------------------------------------------------------------------------
# Move catalogues (used by characters.py)
# ---------------------------------------------------------------------------

MOVES_CATALOGUE: dict[str, list[ActiveSkill]] = {
    "Powerhouse": [
        ActiveSkill("Vertical Suplex", 15, 1.2),
        ActiveSkill("Spinebuster", 18, 1.4),
        ActiveSkill("Military Press", 20, 1.5),
        ActiveSkill("Powerslam", 15, 1.3),
        ActiveSkill("Big Boot", 10, 1.1),
        ActiveSkill("Clothesline from Hell", 22, 1.6),
        ActiveSkill("Backbreaker", 17, 1.4),
        ActiveSkill("Bearhug", 12, 1.0),
        ActiveSkill("Fallaway Slam", 16, 1.3),
        ActiveSkill("Shoulder Tackle", 10, 1.1),
    ],
    "HighFlyer": [
        ActiveSkill("Dropkick", 12, 1.1),
        ActiveSkill("Hurricanrana", 15, 1.3),
        ActiveSkill("Moonsault", 22, 1.6),
        ActiveSkill("Enzuigiri", 18, 1.4),
        ActiveSkill("Springboard Forearm", 20, 1.5),
        ActiveSkill("Tornado DDT", 17, 1.4),
        ActiveSkill("Crossbody", 14, 1.2),
        ActiveSkill("Standing Shooting Star", 25, 1.7),
        ActiveSkill("Handspring Elbow", 15, 1.3),
        ActiveSkill("619 Kick", 20, 1.5),
    ],
    "Technician": [
        ActiveSkill("Arm Bar", 10, 1.0),
        ActiveSkill("German Suplex", 18, 1.5),
        ActiveSkill("Dragon Screw", 12, 1.2),
        ActiveSkill("Cobra Twist", 15, 1.3),
        ActiveSkill("Northern Lights Suplex", 17, 1.4),
        ActiveSkill("Crossface", 20, 1.6),
        ActiveSkill("Ankle Lock", 18, 1.4),
        ActiveSkill("Exploder Suplex", 16, 1.3),
        ActiveSkill("Sharpshooter", 22, 1.7),
        ActiveSkill("Fujiwara Armbar", 15, 1.3),
    ],
}

FINISHER_CATALOGUE: dict[str, list[ActiveSkill]] = {
    "Powerhouse": [
        ActiveSkill("Powerbomb", 45, 2.5, is_finisher=True),
        ActiveSkill("Chokeslam", 40, 2.3, is_finisher=True),
        ActiveSkill("Spear", 35, 2.1, is_finisher=True),
    ],
    "HighFlyer": [
        ActiveSkill("450 Splash", 35, 2.4, is_finisher=True),
        ActiveSkill("Red Arrow", 40, 2.6, is_finisher=True),
        ActiveSkill("Phoenix Splash", 45, 2.7, is_finisher=True),
    ],
    "Technician": [
        ActiveSkill("LeBell Lock", 30, 2.2, is_finisher=True),
        ActiveSkill("Cattle Mutilation", 35, 2.4, is_finisher=True),
        ActiveSkill("Hell's Gate", 40, 2.5, is_finisher=True),
    ],
}

PASSIVE_SKILLS: dict[str, PassiveSkill] = {
    "Powerhouse": PassiveSkill(
        "Iron Body",
        "+15% max HP, +5 Siły dzięki masie mięśniowej",
        strength_bonus=5,
        hp_bonus_pct=15.0,
    ),
    "HighFlyer": PassiveSkill(
        "Aerial Mastery",
        "+20% max Energii, +5 Zręczności dzięki treningom akrobatycznym",
        dexterity_bonus=5,
        energy_bonus_pct=20.0,
    ),
    "Technician": PassiveSkill(
        "Technical Precision",
        "+10% max HP, +8 Zręczności dzięki technicznym umiejętnościom",
        dexterity_bonus=8,
        hp_bonus_pct=10.0,
    ),
}
