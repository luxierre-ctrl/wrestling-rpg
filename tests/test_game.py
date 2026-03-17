"""
test_game.py – Testy jednostkowe dla Wrestling RPG.

Pokrywa co najmniej 15 testów wszystkich głównych mechanik.
Uruchom: pytest tests/ -v
"""

import pytest
from game.characters import Powerhouse, HighFlyer, Technician, Wrestler, XP_THRESHOLDS
from game.items import (
    Outfit, Gadget, Protector, Championship, StatBonus,
    OUTFITS, GADGETS, PROTECTORS, CHAMPIONSHIPS, STARTER_ITEMS,
)
from game.skills import (
    ActiveSkill, PassiveSkill, MOVES_CATALOGUE, FINISHER_CATALOGUE, PASSIVE_SKILLS,
)
from game.exceptions import (
    WrestlingRPGError, InsufficientEnergyError, ItemRequirementError,
    InvalidStatValueError, FinisherNotAvailableError, InvalidMoveError,
)


# ════════════════════════════════════════════════════════════════════
# Fixtures
# ════════════════════════════════════════════════════════════════════

@pytest.fixture
def powerhouse() -> Powerhouse:
    """Create a fresh Powerhouse wrestler for each test."""
    w = Powerhouse("Test Rocky")
    w.restore_to_full()
    return w


@pytest.fixture
def highflyer() -> HighFlyer:
    """Create a fresh HighFlyer wrestler for each test."""
    w = HighFlyer("Test Luna")
    w.restore_to_full()
    return w


@pytest.fixture
def technician() -> Technician:
    """Create a fresh Technician wrestler for each test."""
    w = Technician("Test Tech")
    w.restore_to_full()
    return w


@pytest.fixture
def basic_move() -> ActiveSkill:
    """Return a cheap, low-damage active skill."""
    return ActiveSkill("Test Slam", energy_cost=10, damage_multiplier=1.0)


@pytest.fixture
def expensive_move() -> ActiveSkill:
    """Return an active skill with very high energy cost."""
    return ActiveSkill("Mega Slam", energy_cost=999, damage_multiplier=2.0)


@pytest.fixture
def finisher_move() -> ActiveSkill:
    """Return a finisher-type active skill."""
    return ActiveSkill("Test Finisher", energy_cost=30, damage_multiplier=2.5, is_finisher=True)


@pytest.fixture
def level1_item() -> Gadget:
    """Return a level-1 equippable gadget."""
    return Gadget("Test Tape", "Test item", required_level=1, bonuses=StatBonus(strength=5))


@pytest.fixture
def high_level_item() -> Outfit:
    """Return an item requiring level 4."""
    return Outfit("Elite Attire", "Fancy", required_level=4, bonuses=StatBonus(hp=30))


# ════════════════════════════════════════════════════════════════════
# 1-3. Tworzenie postaci i statystyki bazowe
# ════════════════════════════════════════════════════════════════════

class TestCharacterCreation:
    """Tests for character class instantiation and base stats."""

    def test_powerhouse_creation(self, powerhouse: Powerhouse) -> None:
        """Powerhouse should have correct base stats."""
        assert powerhouse.name == "Test Rocky"
        assert powerhouse.character_class == "Powerhouse"
        assert powerhouse.level == 1
        assert powerhouse.xp == 0

    def test_highflyer_creation(self, highflyer: HighFlyer) -> None:
        """HighFlyer should have correct base stats."""
        assert highflyer.character_class == "HighFlyer"
        assert highflyer.max_energy > highflyer.max_hp  # More energy than HP

    def test_technician_creation(self, technician: Technician) -> None:
        """Technician should have balanced stats."""
        assert technician.character_class == "Technician"
        assert technician.effective_dexterity > technician.effective_strength

    def test_powerhouse_higher_strength_than_highflyer(
        self, powerhouse: Powerhouse, highflyer: HighFlyer
    ) -> None:
        """Powerhouse should have more strength than HighFlyer."""
        assert powerhouse.effective_strength > highflyer.effective_strength

    def test_highflyer_higher_dexterity_than_powerhouse(
        self, powerhouse: Powerhouse, highflyer: HighFlyer
    ) -> None:
        """HighFlyer should have more dexterity than Powerhouse."""
        assert highflyer.effective_dexterity > powerhouse.effective_dexterity


# ════════════════════════════════════════════════════════════════════
# 4-6. Przedmioty – zakładanie, zdejmowanie, wymagania
# ════════════════════════════════════════════════════════════════════

class TestItems:
    """Tests for the item system."""

    def test_equip_item_increases_stats(
        self, powerhouse: Powerhouse, level1_item: Gadget
    ) -> None:
        """Equipping an item should increase the relevant stat."""
        before = powerhouse.effective_strength
        powerhouse.add_to_inventory(level1_item)
        powerhouse.equip(level1_item)
        assert powerhouse.effective_strength == before + 5

    def test_unequip_item_decreases_stats(
        self, powerhouse: Powerhouse, level1_item: Gadget
    ) -> None:
        """Unequipping an item should restore stat to original value."""
        before = powerhouse.effective_strength
        powerhouse.add_to_inventory(level1_item)
        powerhouse.equip(level1_item)
        powerhouse.unequip("gadget")
        assert powerhouse.effective_strength == before

    def test_equip_high_level_item_raises(
        self, powerhouse: Powerhouse, high_level_item: Outfit
    ) -> None:
        """Equipping item above wrestler level should raise ItemRequirementError."""
        powerhouse.add_to_inventory(high_level_item)
        with pytest.raises(ItemRequirementError):
            powerhouse.equip(high_level_item)

    def test_item_requirement_error_is_wrestling_error(self) -> None:
        """ItemRequirementError should inherit from WrestlingRPGError."""
        assert issubclass(ItemRequirementError, WrestlingRPGError)

    def test_stat_bonus_addition(self) -> None:
        """StatBonus __add__ should correctly sum bonuses."""
        b1 = StatBonus(strength=5, dexterity=3)
        b2 = StatBonus(strength=2, hp=10)
        combined = b1 + b2
        assert combined.strength == 7
        assert combined.dexterity == 3
        assert combined.hp == 10

    def test_championship_has_no_level_requirement(self) -> None:
        """Championships should be equippable at any level."""
        champ = CHAMPIONSHIPS[0]
        assert champ.required_level == 1

    def test_item_slot_property(self) -> None:
        """Each item category should return the correct slot string."""
        assert OUTFITS[0].slot == "outfit"
        assert GADGETS[0].slot == "gadget"
        assert PROTECTORS[0].slot == "protector"
        assert CHAMPIONSHIPS[0].slot == "championship"


# ════════════════════════════════════════════════════════════════════
# 7-9. Umiejętności aktywne i energia
# ════════════════════════════════════════════════════════════════════

class TestSkills:
    """Tests for active skill usage and energy management."""

    def test_active_skill_deals_damage(
        self, powerhouse: Powerhouse, highflyer: HighFlyer, basic_move: ActiveSkill
    ) -> None:
        """Using an active skill should reduce opponent's HP."""
        powerhouse.set_moves([basic_move, basic_move, basic_move], FINISHER_CATALOGUE["Powerhouse"][0])
        before_hp = highflyer.current_hp
        basic_move.apply(powerhouse, highflyer)
        assert highflyer.current_hp < before_hp

    def test_active_skill_costs_energy(
        self, powerhouse: Powerhouse, highflyer: HighFlyer, basic_move: ActiveSkill
    ) -> None:
        """Using a skill should deduct energy from the user."""
        before_energy = powerhouse.current_energy
        basic_move.apply(powerhouse, highflyer)
        assert powerhouse.current_energy == before_energy - basic_move.energy_cost

    def test_insufficient_energy_raises(
        self, powerhouse: Powerhouse, highflyer: HighFlyer, expensive_move: ActiveSkill
    ) -> None:
        """Using a skill without enough energy should raise InsufficientEnergyError."""
        powerhouse.current_energy = 5  # Can't afford 999
        with pytest.raises(InsufficientEnergyError):
            expensive_move.apply(powerhouse, highflyer)

    def test_finisher_blocked_above_35pct(
        self, powerhouse: Powerhouse, highflyer: HighFlyer, finisher_move: ActiveSkill
    ) -> None:
        """Finisher should be blocked when opponent has >= 35% HP."""
        highflyer.restore_to_full()  # 100% HP
        with pytest.raises(FinisherNotAvailableError):
            finisher_move.apply(powerhouse, highflyer)

    def test_finisher_works_below_35pct(
        self, powerhouse: Powerhouse, highflyer: HighFlyer, finisher_move: ActiveSkill
    ) -> None:
        """Finisher should succeed when opponent has < 35% HP."""
        powerhouse.set_moves(
            [MOVES_CATALOGUE["Powerhouse"][0]] * 3, finisher_move
        )
        highflyer._current_hp = int(highflyer.max_hp * 0.20)  # 20%
        result = finisher_move.apply(powerhouse, highflyer)
        assert "FINISHER" in result

    def test_passive_skill_applied_to_stats(self, powerhouse: Powerhouse) -> None:
        """Powerhouse passive should increase max HP by 15%."""
        base_hp = powerhouse._base_hp
        expected = int(base_hp * 1.15)
        assert powerhouse.max_hp == expected  # No items or level bonuses


# ════════════════════════════════════════════════════════════════════
# 10-12. System poziomów i XP
# ════════════════════════════════════════════════════════════════════

class TestLevelling:
    """Tests for XP gain and level-up system."""

    def test_gain_xp_increases_xp(self, technician: Technician) -> None:
        """Gaining XP should increase the wrestler's xp attribute."""
        technician.gain_xp(50)
        assert technician.xp == 50

    def test_level_up_occurs(self, technician: Technician) -> None:
        """Gaining enough XP should trigger a level-up."""
        assert technician.level == 1
        technician.gain_xp(XP_THRESHOLDS[1])  # Exactly what's needed for level 2
        assert technician.level == 2

    def test_level_up_increases_max_hp(self, technician: Technician) -> None:
        """Levelling up should increase max HP."""
        before = technician.max_hp
        technician.gain_xp(XP_THRESHOLDS[1])
        assert technician.max_hp > before

    def test_level_up_restores_to_full(self, technician: Technician) -> None:
        """Level-up should fully restore HP and energy."""
        technician._current_hp = 10
        technician.gain_xp(XP_THRESHOLDS[1])
        assert technician.current_hp == technician.max_hp


# ════════════════════════════════════════════════════════════════════
# 13-15. Metody specjalne, polimorfizm, dziedziczenie
# ════════════════════════════════════════════════════════════════════

class TestSpecialMethods:
    """Tests for __str__, __repr__, __eq__, polymorphism, inheritance."""

    def test_str_representation(self, powerhouse: Powerhouse) -> None:
        """__str__ should contain class name and basic stats."""
        s = str(powerhouse)
        assert "Powerhouse" in s
        assert powerhouse.name in s

    def test_repr_representation(self, powerhouse: Powerhouse) -> None:
        """__repr__ should contain class and key attributes."""
        r = repr(powerhouse)
        assert "Powerhouse" in r
        assert "level" in r

    def test_equality_same_name(self, powerhouse: Powerhouse) -> None:
        """Two wrestlers with the same name should be equal."""
        other = Powerhouse("Test Rocky")
        assert powerhouse == other

    def test_equality_different_name(
        self, powerhouse: Powerhouse, highflyer: HighFlyer
    ) -> None:
        """Wrestlers with different names should not be equal."""
        assert powerhouse != highflyer

    def test_isinstance_checks(
        self, powerhouse: Powerhouse, highflyer: HighFlyer, technician: Technician
    ) -> None:
        """All concrete classes should be instances of Wrestler."""
        for w in [powerhouse, highflyer, technician]:
            assert isinstance(w, Wrestler)

    def test_issubclass_checks(self) -> None:
        """Concrete classes should be subclasses of Wrestler."""
        assert issubclass(Powerhouse, Wrestler)
        assert issubclass(HighFlyer, Wrestler)
        assert issubclass(Technician, Wrestler)
        assert not issubclass(Powerhouse, HighFlyer)

    def test_polymorphism_apply(self, powerhouse: Powerhouse) -> None:
        """Skills of different types should all support apply() (duck typing)."""
        skills = [
            MOVES_CATALOGUE["Powerhouse"][0],
            PASSIVE_SKILLS["Powerhouse"],
        ]
        for skill in skills:
            result = skill.apply(powerhouse)
            assert isinstance(result, str)

    def test_skill_equality(self) -> None:
        """Two skills with the same name should be equal."""
        s1 = ActiveSkill("Slam", 10, 1.2)
        s2 = ActiveSkill("Slam", 20, 1.5)
        assert s1 == s2

    def test_item_equality(self) -> None:
        """Items with same name are equal regardless of stats."""
        item1 = Gadget("Tape", "desc", 1, StatBonus(strength=3))
        item2 = Gadget("Tape", "desc", 2, StatBonus(strength=5))
        assert item1 == item2

    def test_item_len(self, level1_item: Gadget) -> None:
        """__len__ on Item should return total bonus value."""
        assert len(level1_item) == 5  # strength=5

    def test_wrestler_len(self, powerhouse: Powerhouse, level1_item: Gadget) -> None:
        """__len__ on Wrestler should return inventory count."""
        assert len(powerhouse) == 0
        powerhouse.add_to_inventory(level1_item)
        assert len(powerhouse) == 1


# ════════════════════════════════════════════════════════════════════
# Additional combat and daily action tests
# ════════════════════════════════════════════════════════════════════

class TestCombatAndDaily:
    """Tests for combat mechanics and daily activities."""

    def test_take_damage_reduces_hp(self, powerhouse: Powerhouse) -> None:
        """take_damage() should reduce current HP."""
        before = powerhouse.current_hp
        powerhouse.take_damage(20)
        assert powerhouse.current_hp == before - 20

    def test_hp_cannot_go_below_zero(self, powerhouse: Powerhouse) -> None:
        """HP should floor at 0 even with massive damage."""
        powerhouse.take_damage(9999)
        assert powerhouse.current_hp == 0

    def test_heal_restores_hp(self, powerhouse: Powerhouse) -> None:
        """heal() should restore HP up to max."""
        powerhouse.take_damage(50)
        powerhouse.heal(30)
        assert powerhouse.current_hp <= powerhouse.max_hp

    def test_regeneration_increases_hp_and_energy(self, powerhouse: Powerhouse) -> None:
        """regenerate() should restore HP and energy."""
        powerhouse.take_damage(50)
        powerhouse.spend_energy(20)
        hp_before = powerhouse.current_hp
        en_before = powerhouse.current_energy
        powerhouse.regenerate()
        assert powerhouse.current_hp >= hp_before
        assert powerhouse.current_energy >= en_before

    def test_training_gives_xp(self, powerhouse: Powerhouse) -> None:
        """train() should award exactly 40 XP."""
        before_xp = powerhouse.xp
        powerhouse.train()
        assert powerhouse.xp == before_xp + 40

    def test_training_reduces_hp_and_energy(self, powerhouse: Powerhouse) -> None:
        """train() should cost HP and energy."""
        hp_before = powerhouse.current_hp
        en_before = powerhouse.current_energy
        powerhouse.train()
        assert powerhouse.current_hp < hp_before
        assert powerhouse.current_energy < en_before

    def test_adrenaline_rush_restores(self, powerhouse: Powerhouse) -> None:
        """adrenaline_rush() should restore HP and energy."""
        powerhouse.take_damage(50)
        powerhouse.spend_energy(20)
        hp_before = powerhouse.current_hp
        powerhouse.adrenaline_rush()
        assert powerhouse.current_hp > hp_before

    def test_exception_hierarchy(self) -> None:
        """All custom exceptions should derive from WrestlingRPGError."""
        for exc_cls in [
            InsufficientEnergyError,
            ItemRequirementError,
            FinisherNotAvailableError,
            InvalidMoveError,
            InvalidStatValueError,
        ]:
            assert issubclass(exc_cls, WrestlingRPGError)
