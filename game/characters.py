"""
Character system for Wrestling RPG.

Hierarchy:
  Wrestler (ABC)  ←  base class with all mechanics
    Powerhouse    ←  high strength/HP, low dexterity
    HighFlyer     ←  high dexterity/energy, lower HP
    Technician    ←  balanced dexterity/HP

NPC roster is also defined here.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
import random

from game.exceptions import (
    InsufficientEnergyError,
    InvalidStatValueError,
    ItemRequirementError,
)
from game.skills import ActiveSkill, PassiveSkill, PASSIVE_SKILLS
from game.items import Item, StatBonus, Championship


# ---------------------------------------------------------------------------
# XP thresholds per level (level 1-10)
# ---------------------------------------------------------------------------
XP_THRESHOLDS: list[int] = [0, 200, 500, 950, 1600, 2500, 3700, 5200, 7000, 9200]


class Wrestler(ABC):
    """Abstract base class for all wrestlers (player and NPC).
    
    Implements all core RPG mechanics: stats, levelling, inventory,
    equipment, and combat interactions.
    
    Args:
        name: Wrestler's display name.
        base_strength: Base strength stat.
        base_dexterity: Base dexterity stat.
        base_hp: Base max HP.
        base_energy: Base max energy.
    """

    # Class attribute – total wrestlers created
    total_wrestlers: int = 0

    def __init__(
        self,
        name: str,
        base_strength: int,
        base_dexterity: int,
        base_hp: int,
        base_energy: int,
    ) -> None:
        Wrestler.total_wrestlers += 1

        self._name: str = name
        self._base_strength: int = base_strength
        self._base_dexterity: int = base_dexterity
        self._base_hp: int = base_hp
        self._base_energy: int = base_energy

        self._level: int = 1
        self._xp: int = 0

        # Equipped items dict: slot -> Item | None
        self._equipped: dict[str, Optional[Item]] = {
            "outfit": None,
            "gadget": None,
            "protector": None,
            "championship": None,
        }

        # Inventory (bag)
        self._inventory: list[Item] = []

        # Selected moves (3 active + 1 finisher)
        self._moves: list[ActiveSkill] = []
        self._finisher: Optional[ActiveSkill] = None

        # Current combat values (start at max)
        self._current_hp: int = self.max_hp
        self._current_energy: int = self.max_energy

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def character_class(self) -> str:
        """Return class name string: 'Powerhouse', 'HighFlyer', 'Technician'."""
        pass

    @abstractmethod
    def level_up_bonus(self) -> StatBonus:
        """Return stat bonuses gained per level-up (class-specific scaling)."""
        pass

    # ------------------------------------------------------------------
    # Properties: identity
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Wrestler name."""
        return self._name

    @property
    def level(self) -> int:
        """Current level."""
        return self._level

    @property
    def xp(self) -> int:
        """Current XP."""
        return self._xp

    @property
    def xp_to_next_level(self) -> int:
        """XP required to reach next level."""
        if self._level >= len(XP_THRESHOLDS):
            return 9999
        return XP_THRESHOLDS[self._level] - self._xp

    # ------------------------------------------------------------------
    # Passive skill
    # ------------------------------------------------------------------

    @property
    def passive_skill(self) -> PassiveSkill:
        """Return passive skill for this class."""
        return PASSIVE_SKILLS[self.character_class]

    # ------------------------------------------------------------------
    # Effective stats (base + items + level bonuses + passive)
    # ------------------------------------------------------------------

    def _item_bonuses(self) -> StatBonus:
        """Sum all bonuses from currently equipped items."""
        total = StatBonus()
        for item in self._equipped.values():
            if item is not None:
                total = total + item.bonuses
        return total

    def _level_bonuses(self) -> StatBonus:
        """Cumulative bonuses from all levels gained (not counting base)."""
        bonus = self.level_up_bonus()
        levels_gained = self._level - 1
        return StatBonus(
            strength=bonus.strength * levels_gained,
            dexterity=bonus.dexterity * levels_gained,
            hp=bonus.hp * levels_gained,
            energy=bonus.energy * levels_gained,
        )

    @property
    def effective_strength(self) -> int:
        """Effective strength = base + item bonuses + level bonuses + passive."""
        passive = self.passive_skill
        ib = self._item_bonuses()
        lb = self._level_bonuses()
        return self._base_strength + ib.strength + lb.strength + passive.strength_bonus

    @property
    def effective_dexterity(self) -> int:
        """Effective dexterity = base + item bonuses + level bonuses + passive."""
        passive = self.passive_skill
        ib = self._item_bonuses()
        lb = self._level_bonuses()
        return self._base_dexterity + ib.dexterity + lb.dexterity + passive.dexterity_bonus

    @property
    def max_hp(self) -> int:
        """Max HP including all bonuses and passive percentage."""
        passive = self.passive_skill
        ib = self._item_bonuses()
        lb = self._level_bonuses()
        base_total = self._base_hp + ib.hp + lb.hp
        return int(base_total * (1 + passive.hp_bonus_pct / 100))

    @property
    def max_energy(self) -> int:
        """Max energy including all bonuses and passive percentage."""
        passive = self.passive_skill
        ib = self._item_bonuses()
        lb = self._level_bonuses()
        base_total = self._base_energy + ib.energy + lb.energy
        return int(base_total * (1 + passive.energy_bonus_pct / 100))

    # ------------------------------------------------------------------
    # Current HP / Energy (combat state)
    # ------------------------------------------------------------------

    @property
    def current_hp(self) -> int:
        """Current HP (combat state)."""
        return self._current_hp

    @current_hp.setter
    def current_hp(self, value: int) -> None:
        """Set current HP with clamping to [0, max_hp]."""
        self._current_hp = max(0, min(value, self.max_hp))

    @property
    def current_energy(self) -> int:
        """Current energy (combat state)."""
        return self._current_energy

    @current_energy.setter
    def current_energy(self, value: int) -> None:
        """Set current energy with clamping to [0, max_energy]."""
        self._current_energy = max(0, min(value, self.max_energy))

    @property
    def is_alive(self) -> bool:
        """True if wrestler has more than 0 HP."""
        return self._current_hp > 0

    @property
    def hp_percentage(self) -> float:
        """Current HP as a percentage of max HP."""
        return (self._current_hp / self.max_hp) * 100 if self.max_hp > 0 else 0.0

    # ------------------------------------------------------------------
    # Combat actions
    # ------------------------------------------------------------------

    def take_damage(self, amount: int) -> None:
        """Receive damage, reducing current HP (floored at 0).
        
        Args:
            amount: Damage to take (negative values clamped to 0).
        """
        amount = max(0, amount)
        self._current_hp = max(0, self._current_hp - amount)

    def spend_energy(self, amount: int) -> None:
        """Spend energy for a move.
        
        Args:
            amount: Energy to spend.
            
        Raises:
            InsufficientEnergyError: If not enough energy available.
        """
        if self._current_energy < amount:
            raise InsufficientEnergyError(amount, self._current_energy)
        self._current_energy -= amount

    def heal(self, amount: int) -> None:
        """Restore HP, capped at max_hp.
        
        Args:
            amount: HP to restore.
        """
        self._current_hp = min(self._current_hp + amount, self.max_hp)

    def restore_energy(self, amount: int) -> None:
        """Restore energy, capped at max_energy.
        
        Args:
            amount: Energy to restore.
        """
        self._current_energy = min(self._current_energy + amount, self.max_energy)

    def restore_to_full(self) -> None:
        """Fully restore HP and energy (used between fights)."""
        self._current_hp = self.max_hp
        self._current_energy = self.max_energy

    # ------------------------------------------------------------------
    # XP and levelling
    # ------------------------------------------------------------------

    def gain_xp(self, amount: int) -> list[str]:
        """Gain experience points; trigger level-ups as needed.
        
        Args:
            amount: XP to gain.
            
        Returns:
            List of log strings (level-up announcements).
        """
        self._xp += amount
        messages: list[str] = [f"🏅 +{amount} XP zdobyte! (łącznie: {self._xp})"]

        while (
            self._level < len(XP_THRESHOLDS)
            and self._xp >= XP_THRESHOLDS[self._level]
        ):
            self._level += 1
            # Restore HP / energy after level-up
            self._current_hp = self.max_hp
            self._current_energy = self.max_energy
            messages.append(
                f"⭐ LEVEL UP! Osiągnąłeś poziom {self._level}! "
                f"HP i energia zostały uzupełnione."
            )
        return messages

    # ------------------------------------------------------------------
    # Move management
    # ------------------------------------------------------------------

    def set_moves(self, moves: list[ActiveSkill], finisher: ActiveSkill) -> None:
        """Assign the wrestler's combat moves.
        
        Args:
            moves: List of exactly 3 regular active moves.
            finisher: The finisher move.
        """
        self._moves = moves
        self._finisher = finisher

    @property
    def moves(self) -> list[ActiveSkill]:
        """Selected regular moves."""
        return self._moves

    @property
    def finisher(self) -> Optional[ActiveSkill]:
        """Selected finisher move."""
        return self._finisher

    @property
    def finisher_available(self) -> bool:
        """True if conditions allow finisher (opponent would need < 35% HP – checked at use)."""
        return self._finisher is not None

    # ------------------------------------------------------------------
    # Equipment
    # ------------------------------------------------------------------

    def equip(self, item: Item) -> str:
        """Equip an item (must be in inventory first).
        
        Args:
            item: Item to equip.
            
        Returns:
            Log message.
            
        Raises:
            ItemRequirementError: If level requirements are not met.
        """
        item.check_requirements(self._level)
        slot = item.slot
        # Un-equip existing item in the slot
        old = self._equipped.get(slot)
        if old is not None:
            self._equipped[slot] = None
        self._equipped[slot] = item
        # Clamp current stats to new max values
        self._current_hp = min(self._current_hp, self.max_hp)
        self._current_energy = min(self._current_energy, self.max_energy)
        return f"✅ Założono: {item.name}"

    def unequip(self, slot: str) -> str:
        """Remove item from equipment slot.
        
        Args:
            slot: Slot name to clear.
            
        Returns:
            Log message.
        """
        item = self._equipped.get(slot)
        if item is None:
            return f"Slot '{slot}' jest pusty."
        self._equipped[slot] = None
        self._current_hp = min(self._current_hp, self.max_hp)
        self._current_energy = min(self._current_energy, self.max_energy)
        return f"🔄 Zdjęto: {item.name}"

    def add_to_inventory(self, item: Item) -> None:
        """Add item to inventory bag.
        
        Args:
            item: Item to add.
        """
        self._inventory.append(item)

    @property
    def inventory(self) -> list[Item]:
        """All items in the inventory bag."""
        return list(self._inventory)

    @property
    def equipped(self) -> dict[str, Optional[Item]]:
        """Currently equipped items by slot."""
        return dict(self._equipped)

    def award_championship(self, champ: Championship) -> str:
        """Award a championship belt to this wrestler.
        
        Args:
            champ: Championship to award.
            
        Returns:
            Announcement string.
        """
        self._equipped["championship"] = champ
        self._current_hp = min(self._current_hp, self.max_hp)
        return f"🏆 {self._name} ZDOBYWA {champ.name.upper()}!"

    # ------------------------------------------------------------------
    # Daily actions
    # ------------------------------------------------------------------

    def train(self) -> list[str]:
        """Perform training session: +40 XP, -25 HP, -10 Energy.
        
        Returns:
            Log messages including possible level-up.
        """
        messages = ["🏋️ Trening rozpoczęty..."]
        self._current_hp = max(0, self._current_hp - 25)
        self._current_energy = max(0, self._current_energy - 10)
        messages.append(f"💪 Trening ukończony! -25 HP, -10 Energii")
        xp_messages = self.gain_xp(40)
        messages.extend(xp_messages)
        return messages

    def walk(self) -> tuple[list[str], Optional[Item]]:
        """Take a walk: random chance to find a loot-able item.
        
        Returns:
            Tuple of (log messages, found_item or None).
        """
        from game.items import ALL_LOOTABLE_ITEMS
        messages = ["🚶 Spacer po okolicach..."]
        found: Optional[Item] = None

        eligible = [i for i in ALL_LOOTABLE_ITEMS if i.required_level <= self._level]
        if eligible and random.random() < 0.45:
            found = random.choice(eligible)
            self._inventory.append(found)
            messages.append(f"🎁 Znaleziono: {found.name}! ({found.item_type_label()})")
        else:
            messages.append("Nic ciekawego się nie wydarzyło podczas spaceru.")
        return messages, found

    def regenerate(self) -> list[str]:
        """Rest and recover: +30 HP, +10 Energy (capped at max).
        
        Returns:
            Log messages.
        """
        hp_before = self._current_hp
        en_before = self._current_energy
        self._current_hp = min(self._current_hp + 30, self.max_hp)
        self._current_energy = min(self._current_energy + 10, self.max_energy)
        hp_gained = self._current_hp - hp_before
        en_gained = self._current_energy - en_before
        return [
            f"😴 Regeneracja... +{hp_gained} HP, +{en_gained} Energii.",
            f"Stan: {self._current_hp}/{self.max_hp} HP | "
            f"{self._current_energy}/{self.max_energy} Energii",
        ]

    # ------------------------------------------------------------------
    # Adrenaline rush (combat only)
    # ------------------------------------------------------------------

    def adrenaline_rush(self) -> str:
        """Use Adrenaline Rush in combat: no damage but +30 HP, +5 Energy.
        
        Returns:
            Log message.
        """
        self.heal(30)
        self.restore_energy(5)
        return (
            f"⚡ ADRENALINA! {self._name} czerpie z rezerw! "
            f"+30 HP, +5 Energii. ({self._current_hp}/{self.max_hp} HP)"
        )

    # ------------------------------------------------------------------
    # Special methods
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return (
            f"{self._name} [{self.character_class}] Lvl {self._level} | "
            f"HP: {self._current_hp}/{self.max_hp} | "
            f"Energia: {self._current_energy}/{self.max_energy} | "
            f"Siła: {self.effective_strength} | Zręczność: {self.effective_dexterity}"
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(name={self._name!r}, level={self._level}, "
            f"xp={self._xp})"
        )

    def __eq__(self, other: object) -> bool:
        """Two wrestlers are equal if they have the same name."""
        if not isinstance(other, Wrestler):
            return NotImplemented
        return self._name == other._name

    def __lt__(self, other: "Wrestler") -> bool:
        """Compare by level, then by total effective stats."""
        if self._level != other._level:
            return self._level < other._level
        return (self.effective_strength + self.effective_dexterity) < (
            other.effective_strength + other.effective_dexterity
        )

    def __len__(self) -> int:
        """Return number of items in inventory."""
        return len(self._inventory)


# ---------------------------------------------------------------------------
# Concrete wrestler classes
# ---------------------------------------------------------------------------

class Powerhouse(Wrestler):
    """Heavy-hitting powerhouse: high Strength & HP, low Dexterity.
    
    Args:
        name: Wrestler name.
    """

    def __init__(self, name: str) -> None:
        super().__init__(
            name=name,
            base_strength=16,
            base_dexterity=6,
            base_hp=135,
            base_energy=80,
        )

    @property
    def character_class(self) -> str:
        return "Powerhouse"

    def level_up_bonus(self) -> StatBonus:
        """Powerhouses gain mostly Strength and HP per level."""
        return StatBonus(strength=3, dexterity=1, hp=12, energy=3)


class HighFlyer(Wrestler):
    """Aerial specialist: high Dexterity & Energy, lower HP.
    
    Args:
        name: Wrestler name.
    """

    def __init__(self, name: str) -> None:
        super().__init__(
            name=name,
            base_strength=10,
            base_dexterity=18,
            base_hp=100,
            base_energy=120,
        )

    @property
    def character_class(self) -> str:
        return "HighFlyer"

    def level_up_bonus(self) -> StatBonus:
        """High Flyers gain mostly Dexterity and Energy per level."""
        return StatBonus(strength=1, dexterity=3, hp=8, energy=6)


class Technician(Wrestler):
    """Technical wrestler: balanced Dexterity/HP, moderate Strength.
    
    Args:
        name: Wrestler name.
    """

    def __init__(self, name: str) -> None:
        super().__init__(
            name=name,
            base_strength=15,
            base_dexterity=15,
            base_hp=125,
            base_energy=100,
        )

    @property
    def character_class(self) -> str:
        return "Technician"

    def level_up_bonus(self) -> StatBonus:
        """Technicians gain balanced stats per level."""
        return StatBonus(strength=2, dexterity=2, hp=10, energy=4)


# ---------------------------------------------------------------------------
# NPC factory
# ---------------------------------------------------------------------------

def _make_npc(cls: type, name: str, level: int, moves_idx: list[int], fin_idx: int) -> Wrestler:
    """Helper: create an NPC of given class, level, and move selection.
    
    Args:
        cls: Wrestler subclass (Powerhouse, HighFlyer, Technician).
        name: NPC name.
        level: Level to set the NPC to.
        moves_idx: Indices of moves to pick from class catalogue.
        fin_idx: Index of finisher to pick.
        
    Returns:
        Fully configured NPC Wrestler.
    """
    from game.skills import MOVES_CATALOGUE, FINISHER_CATALOGUE
    npc = cls(name)
    # Force level without XP tracking
    npc._level = level  # type: ignore[attr-defined]
    # Level-up stat inflation is handled via level_up_bonus()

    class_name = npc.character_class
    available_moves = MOVES_CATALOGUE[class_name]
    available_finishers = FINISHER_CATALOGUE[class_name]

    selected_moves = [available_moves[i] for i in moves_idx if i < len(available_moves)]
    finisher = available_finishers[fin_idx % len(available_finishers)]
    npc.set_moves(selected_moves, finisher)
    npc.restore_to_full()
    return npc


def build_npc_roster() -> list[Wrestler]:
    """Build the full NPC roster used for match-making.
    
    Returns:
        List of NPC wrestlers, from weakest to strongest.
    """
    roster: list[Wrestler] = [
        # Chapter 1 – School (weak trainees)
        _make_npc(Powerhouse, "Rocky Bułka",        level=1, moves_idx=[0,4,7], fin_idx=2),
        _make_npc(HighFlyer,  "Timmy Flip",          level=1, moves_idx=[0,6,3], fin_idx=0),
        _make_npc(Technician, "Grzegorz Dźwignia",   level=1, moves_idx=[0,2,7], fin_idx=0),
        _make_npc(Powerhouse, "Bartek Mocarz",        level=2, moves_idx=[1,3,5], fin_idx=0),
        _make_npc(HighFlyer,  "Salto Stasiu",         level=2, moves_idx=[1,4,8], fin_idx=1),

        # Mid-tier opponents
        _make_npc(Technician, "Adam Dusiciел",        level=3, moves_idx=[1,5,8], fin_idx=1),
        _make_npc(Powerhouse, "Wielki Zbyszek",       level=3, moves_idx=[2,5,9], fin_idx=1),
        _make_npc(HighFlyer,  "Lotny Krzysztof",      level=3, moves_idx=[2,7,9], fin_idx=2),

        # Chapter 2 – Local Federation
        _make_npc(Technician, "Mistrz Janusz",        level=4, moves_idx=[3,6,8], fin_idx=2),
        _make_npc(Powerhouse, "Destruktor Marek",     level=4, moves_idx=[0,2,5], fin_idx=0),
        _make_npc(HighFlyer,  "Feniks Radek",         level=5, moves_idx=[3,7,9], fin_idx=2),
        _make_npc(Technician, "Żelazny Piotr",        level=5, moves_idx=[4,6,9], fin_idx=0),

        # Bosses
        _make_npc(Powerhouse, "Kolos Waldemar",       level=6, moves_idx=[1,2,5], fin_idx=0),
        _make_npc(Technician, "Profesor Zygmunt",     level=6, moves_idx=[2,5,8], fin_idx=2),
        _make_npc(HighFlyer,  "Legenda – El Aguila",  level=7, moves_idx=[1,4,7], fin_idx=1),
    ]
    return roster


# ---------------------------------------------------------------------------
# NPC AI: choose a move
# ---------------------------------------------------------------------------

def npc_choose_move(npc: Wrestler, player: Wrestler) -> ActiveSkill:
    """Simple NPC AI: use finisher if available, otherwise random move.
    
    Args:
        npc: The NPC wrestler.
        player: The player wrestler (used to check finisher eligibility).
        
    Returns:
        The ActiveSkill the NPC will use.
    """
    # Try finisher
    if (
        npc.finisher is not None
        and player.hp_percentage < 35
        and npc.current_energy >= npc.finisher.energy_cost
    ):
        return npc.finisher

    # Pick affordable moves
    affordable = [m for m in npc.moves if npc.current_energy >= m.energy_cost]
    if affordable:
        return random.choice(affordable)

    # No affordable moves → adrenaline (handled externally) or weakest move
    return min(npc.moves, key=lambda m: m.energy_cost)
