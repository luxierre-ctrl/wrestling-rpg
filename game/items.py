"""
Item system for Wrestling RPG.

Implements the full item hierarchy:
- Item (ABC)
  - Outfit (ring attire / strój)
  - Gadget (gadzety)
  - Protector (ochraniacze)
  - Championship (pasy mistrzowskie – unique, not equippable by purchase)
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class StatBonus:
    """Flat stat bonuses provided by an item.
    
    Attributes:
        strength: Bonus to Strength.
        dexterity: Bonus to Dexterity.
        hp: Bonus to max HP.
        energy: Bonus to max Energy.
    """
    strength: int = 0
    dexterity: int = 0
    hp: int = 0
    energy: int = 0

    def __add__(self, other: "StatBonus") -> "StatBonus":
        """Combine two StatBonus objects."""
        return StatBonus(
            strength=self.strength + other.strength,
            dexterity=self.dexterity + other.dexterity,
            hp=self.hp + other.hp,
            energy=self.energy + other.energy,
        )

    def __repr__(self) -> str:
        parts = []
        if self.strength:
            parts.append(f"+{self.strength} Siły")
        if self.dexterity:
            parts.append(f"+{self.dexterity} Zręczności")
        if self.hp:
            parts.append(f"+{self.hp} HP")
        if self.energy:
            parts.append(f"+{self.energy} Energii")
        return ", ".join(parts) if parts else "brak bonusów"


class Item(ABC):
    """Abstract base class for all items in the game.
    
    Every item has a name, description, level requirement,
    stat bonuses, and a slot it occupies.
    
    Args:
        name: Display name of the item.
        description: Flavour text / short description.
        required_level: Minimum wrestler level to equip this item.
        bonuses: StatBonus object with the item's stat modifications.
    """

    # Class attribute – tracks total items created (demonstrates class attr)
    total_items_created: int = 0

    def __init__(
        self,
        name: str,
        description: str,
        required_level: int,
        bonuses: StatBonus,
    ) -> None:
        Item.total_items_created += 1
        self._name = name
        self._description = description
        self._required_level = required_level
        self._bonuses = bonuses

    @property
    def name(self) -> str:
        """Item name."""
        return self._name

    @property
    def description(self) -> str:
        """Item description."""
        return self._description

    @property
    def required_level(self) -> int:
        """Minimum level required to equip this item."""
        return self._required_level

    @property
    def bonuses(self) -> StatBonus:
        """Stat bonuses provided by this item."""
        return self._bonuses

    @property
    @abstractmethod
    def slot(self) -> str:
        """Equipment slot this item occupies (e.g. 'outfit', 'gadget')."""
        pass

    @abstractmethod
    def item_type_label(self) -> str:
        """Human-readable category label for UI display."""
        pass

    def check_requirements(self, wrestler_level: int) -> None:
        """Validate that the wrestler meets this item's requirements.
        
        Args:
            wrestler_level: Current level of the wrestler.
            
        Raises:
            ItemRequirementError: If level requirement is not met.
        """
        from game.exceptions import ItemRequirementError
        if wrestler_level < self._required_level:
            raise ItemRequirementError(
                self._name,
                f"wymagany poziom {self._required_level} (posiadasz {wrestler_level})"
            )

    def __str__(self) -> str:
        return (
            f"[{self.item_type_label()}] {self._name} "
            f"(Lvl {self._required_level}+) | {self._bonuses!r}"
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(name={self._name!r}, "
            f"level={self._required_level}, bonuses={self._bonuses!r})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Item):
            return NotImplemented
        return self._name == other._name

    def __lt__(self, other: "Item") -> bool:
        """Sort items by required level, then name."""
        if self._required_level != other._required_level:
            return self._required_level < other._required_level
        return self._name < other._name

    def __len__(self) -> int:
        """Return combined total bonus value (for comparison/ranking)."""
        b = self._bonuses
        return b.strength + b.dexterity + b.hp + b.energy


# ---------------------------------------------------------------------------
# Concrete item categories
# ---------------------------------------------------------------------------

class Outfit(Item):
    """Ring attire / strój – affects overall stats based on style.
    
    Args:
        name: Outfit name.
        description: Style description.
        required_level: Min level to equip.
        bonuses: Stat bonuses.
    """

    def __init__(
        self,
        name: str,
        description: str,
        required_level: int,
        bonuses: StatBonus,
    ) -> None:
        super().__init__(name, description, required_level, bonuses)

    @property
    def slot(self) -> str:
        return "outfit"

    def item_type_label(self) -> str:
        return "Strój"


class Gadget(Item):
    """In-ring gadget / gadzet – wristbands, accessories, etc.
    
    Args:
        name: Gadget name.
        description: What it does.
        required_level: Min level to equip.
        bonuses: Stat bonuses.
    """

    def __init__(
        self,
        name: str,
        description: str,
        required_level: int,
        bonuses: StatBonus,
    ) -> None:
        super().__init__(name, description, required_level, bonuses)

    @property
    def slot(self) -> str:
        return "gadget"

    def item_type_label(self) -> str:
        return "Gadżet"


class Protector(Item):
    """Protective gear / ochraniacze – knee pads, elbow pads, etc.
    
    Args:
        name: Protector name.
        description: What it protects.
        required_level: Min level to equip.
        bonuses: Stat bonuses.
    """

    def __init__(
        self,
        name: str,
        description: str,
        required_level: int,
        bonuses: StatBonus,
    ) -> None:
        super().__init__(name, description, required_level, bonuses)

    @property
    def slot(self) -> str:
        return "protector"

    def item_type_label(self) -> str:
        return "Ochraniacz"


class Championship(Item):
    """A championship belt – prestigious item awarded for winning titles.
    
    Championships cannot be purchased or found – only won.
    They provide significant stat bonuses as a prestige bonus.
    
    Args:
        name: Championship name.
        description: Prestige description.
        bonuses: Stat bonuses granted by holding the title.
    """

    def __init__(self, name: str, description: str, bonuses: StatBonus) -> None:
        # Championships have no level requirement (awarded by storyline)
        super().__init__(name, description, required_level=1, bonuses=bonuses)

    @property
    def slot(self) -> str:
        return "championship"

    def item_type_label(self) -> str:
        return "🏆 Pas Mistrzowski"

    def check_requirements(self, wrestler_level: int) -> None:
        """Championships have no standard requirements."""
        pass


# ---------------------------------------------------------------------------
# Item catalogue
# ---------------------------------------------------------------------------

# Outfits (stroje) – 5 items, first 2 require level 1
OUTFITS: list[Outfit] = [
    Outfit(
        "Rookie Trunks",
        "Podstawowe spodenki wrestlera – proste, ale dobre na start.",
        required_level=1,
        bonuses=StatBonus(strength=2, dexterity=2),
    ),
    Outfit(
        "Beginner's Singlet",
        "Klasyczny strój zapaśniczy dla debiutantów.",
        required_level=1,
        bonuses=StatBonus(hp=10, energy=5),
    ),
    Outfit(
        "Power Suit",
        "Obcisły strój podkreślający mięśnie – dodaje pewności siebie.",
        required_level=2,
        bonuses=StatBonus(strength=6, hp=15),
    ),
    Outfit(
        "Aerial Tights",
        "Lekki, aerodynamiczny strój dla akrobatów.",
        required_level=3,
        bonuses=StatBonus(dexterity=8, energy=10),
    ),
    Outfit(
        "Championship Attire",
        "Lśniący strój godny mistrza – z obszyciem i złotymi detalami.",
        required_level=4,
        bonuses=StatBonus(strength=5, dexterity=5, hp=20, energy=10),
    ),
]

# Gadgets (gadzety) – 5 items
GADGETS: list[Gadget] = [
    Gadget(
        "Sports Tape",
        "Taśma sportowa na nadgarstki – podstawowe wsparcie.",
        required_level=1,
        bonuses=StatBonus(strength=3),
    ),
    Gadget(
        "Sweatband",
        "Opaska na głowę – utrzymuje skupienie w walce.",
        required_level=1,
        bonuses=StatBonus(dexterity=3),
    ),
    Gadget(
        "Power Gloves",
        "Rękawice treningowe wzmacniające chwyt.",
        required_level=2,
        bonuses=StatBonus(strength=7, dexterity=2),
    ),
    Gadget(
        "Energy Drink Flask",
        "Kolba z napojem energetycznym – uzupełnia zapas energii.",
        required_level=2,
        bonuses=StatBonus(energy=15),
    ),
    Gadget(
        "Champion's Wristbands",
        "Złote opaski mistrza – symbol prestiżu i siły.",
        required_level=4,
        bonuses=StatBonus(strength=8, dexterity=6, energy=10),
    ),
]

# Protectors (ochraniacze) – 5 items
PROTECTORS: list[Protector] = [
    Protector(
        "Basic Knee Pads",
        "Standardowe ochraniacze na kolana – ochrona przed upadkami.",
        required_level=1,
        bonuses=StatBonus(hp=15),
    ),
    Protector(
        "Elbow Pads",
        "Ochraniacze na łokcie – idealne do łokciowych ciosów.",
        required_level=1,
        bonuses=StatBonus(hp=10, dexterity=2),
    ),
    Protector(
        "Pro Knee Guards",
        "Profesjonalne ochraniacze na kolana z wyściółką.",
        required_level=2,
        bonuses=StatBonus(hp=25, dexterity=3),
    ),
    Protector(
        "Steel-Reinforced Boots",
        "Buty z wzmocnionym czubkiem – bezpieczeństwo i moc w kopnięciach.",
        required_level=3,
        bonuses=StatBonus(strength=5, hp=20),
    ),
    Protector(
        "Full Body Wrap",
        "Profesjonalne owiązania całego ciała – maksymalna ochrona.",
        required_level=4,
        bonuses=StatBonus(hp=40, dexterity=4),
    ),
]

# Championship belts
CHAMPIONSHIPS: list[Championship] = [
    Championship(
        "Local Championship",
        "Pas Lokalnej Federacji – pierwszy krok ku sławie.",
        bonuses=StatBonus(strength=5, dexterity=5, hp=20, energy=10),
    ),
    Championship(
        "National Championship",
        "Pas Federacji Krajowej – symbol najlepszego zawodnika w kraju.",
        bonuses=StatBonus(strength=10, dexterity=10, hp=40, energy=20),
    ),
]

# Starter items given by trainer
STARTER_ITEMS: list[Item] = [
    Gadget(
        "Trainer's Gloves",
        "Rękawice od trenera – solidny bonus do siły.",
        required_level=1,
        bonuses=StatBonus(strength=5),
    ),
    Protector(
        "Trainer's Knee Pads",
        "Ochraniacze od trenera – zwiększają zręczność.",
        required_level=1,
        bonuses=StatBonus(dexterity=5),
    ),
    Outfit(
        "Trainer's Singlet",
        "Strój od trenera – dodatkowe punkty życia.",
        required_level=1,
        bonuses=StatBonus(hp=20),
    ),
]

# All loot-able items (excluding championships and starters)
ALL_LOOTABLE_ITEMS: list[Item] = OUTFITS + GADGETS + PROTECTORS
