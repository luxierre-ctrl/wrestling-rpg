"""
demo.py – Program demonstracyjny Wrestling RPG.

Shows:
1. Creating 3 characters of different classes
2. Initial stats display
3. Equipping items and stat changes
4. Attempting item with wrong requirements (exception)
5. Using active skills
6. Gaining XP and levelling up
7. Passive skills in action
"""

from game.characters import Powerhouse, HighFlyer, Technician, Wrestler
from game.items import OUTFITS, GADGETS, PROTECTORS, CHAMPIONSHIPS, StatBonus
from game.skills import MOVES_CATALOGUE, FINISHER_CATALOGUE, PASSIVE_SKILLS
from game.exceptions import (
    WrestlingRPGError, InsufficientEnergyError,
    ItemRequirementError, FinisherNotAvailableError,
)


def separator(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ── 1. Create 3 characters ─────────────────────────────────────────────────
separator("1. Tworzenie postaci")

rocky = Powerhouse("Rocky Miazga")
luna = HighFlyer("Luna Relámpago")
grzegorz = Technician("Grzegorz Technikus")

for w in [rocky, luna, grzegorz]:
    print(w)

# ── 2. Initial stats display ───────────────────────────────────────────────
separator("2. Statystyki początkowe")

for w in [rocky, luna, grzegorz]:
    print(f"\n{w.name} [{w.character_class}]")
    print(f"  Siła:       {w.effective_strength}")
    print(f"  Zręczność:  {w.effective_dexterity}")
    print(f"  Max HP:     {w.max_hp}")
    print(f"  Max Energia:{w.max_energy}")
    print(f"  Pasywna:    {w.passive_skill.name} – {w.passive_skill.description}")

# ── 3. Equip items and show stat changes ──────────────────────────────────
separator("3. Zakładanie przedmiotów i zmiana statystyk")

sword_item = GADGETS[0]  # Sports Tape – level 1
armor_item = PROTECTORS[0]  # Basic Knee Pads – level 1

print(f"\nPrzed założeniem przedmiotu – Rocky Siła: {rocky.effective_strength}")
rocky.add_to_inventory(sword_item)
rocky.equip(sword_item)
print(f"Po założeniu '{sword_item.name}' – Rocky Siła: {rocky.effective_strength}")
print(f"Bonus przedmiotu: {sword_item.bonuses!r}")

# ── 4. Attempt item with wrong requirements ─────────────────────────────────
separator("4. Próba założenia przedmiotu z niewłaściwymi wymaganiami")

high_level_item = OUTFITS[4]  # Championship Attire – level 4
print(f"Próba założenia '{high_level_item.name}' (wymaga Lvl {high_level_item.required_level}) przez Rocky (Lvl {rocky.level})")
try:
    rocky.equip(high_level_item)
except ItemRequirementError as e:
    print(f"✓ ItemRequirementError złapany: {e}")

# ── 5. Active skills ───────────────────────────────────────────────────────
separator("5. Używanie aktywnych umiejętności")

rocky_moves = MOVES_CATALOGUE["Powerhouse"]
chosen_move = rocky_moves[0]  # Vertical Suplex
rocky.set_moves([rocky_moves[0], rocky_moves[1], rocky_moves[2]], FINISHER_CATALOGUE["Powerhouse"][0])

luna.set_moves([MOVES_CATALOGUE["HighFlyer"][0], MOVES_CATALOGUE["HighFlyer"][1], MOVES_CATALOGUE["HighFlyer"][2]],
               FINISHER_CATALOGUE["HighFlyer"][0])
luna.restore_to_full()
rocky.restore_to_full()

print(f"\nRocky używa {chosen_move.name} na Lunę:")
result = chosen_move.apply(rocky, luna)
print(f"  → {result}")

# Try finisher when opponent has > 35% HP
print(f"\nPróba Finishera gdy rywal ma {luna.hp_percentage:.0f}% HP:")
try:
    rocky.finisher.apply(rocky, luna)
except FinisherNotAvailableError as e:
    print(f"✓ FinisherNotAvailableError złapany: {e}")

# ── 6. XP and level up ────────────────────────────────────────────────────
separator("6. Zdobywanie doświadczenia i awans")

print(f"\nGrzegorz przed: Lvl {grzegorz.level}, XP: {grzegorz.xp}, Max HP: {grzegorz.max_hp}")
msgs = grzegorz.gain_xp(450)
for m in msgs:
    print(f"  {m}")
print(f"Grzegorz po: Lvl {grzegorz.level}, XP: {grzegorz.xp}, Max HP: {grzegorz.max_hp}")

# ── 7. Passive skills ──────────────────────────────────────────────────────
separator("7. Umiejętności pasywne")

print("\nUmiejętności pasywne każdej klasy:")
for cls_name, passive in PASSIVE_SKILLS.items():
    print(f"  {cls_name}: {passive.name}")
    print(f"    → {passive.description}")

print(f"\nRocky (Powerhouse) – bonus HP%: +{rocky.passive_skill.hp_bonus_pct}%")
print(f"Rocky Max HP bez pasywnej: {rocky._base_hp + rocky._item_bonuses().hp}")
print(f"Rocky Max HP z pasywną:   {rocky.max_hp}")

print(f"\nLuna (HighFlyer) – bonus Energii%: +{luna.passive_skill.energy_bonus_pct}%")
print(f"Luna Max Energia bez pasywnej: {luna._base_energy}")
print(f"Luna Max Energia z pasywną:   {luna.max_energy}")

# ── 8. Special methods demo ────────────────────────────────────────────────
separator("8. Metody specjalne")

print(f"\nstr(rocky) → {rocky}")
print(f"repr(rocky) → {repr(rocky)}")
print(f"rocky == rocky: {rocky == rocky}")
print(f"rocky == luna: {rocky == luna}")
print(f"rocky < luna (poziom/statystyki): {rocky < luna}")
print(f"len(rocky.inventory) items: {len(rocky)}")

# StatBonus addition operator
b1 = StatBonus(strength=5, hp=10)
b2 = StatBonus(strength=3, dexterity=4)
b3 = b1 + b2
print(f"\nStatBonus dodawanie: {b1!r} + {b2!r} = {b3!r}")

# ── 9. isinstance / issubclass ─────────────────────────────────────────────
separator("9. isinstance / issubclass")

wrestlers = [rocky, luna, grzegorz]
for w in wrestlers:
    print(f"  isinstance({w.name}, Wrestler): {isinstance(w, Wrestler)}")
print(f"\nissubclass(Powerhouse, Wrestler): {issubclass(Powerhouse, Wrestler)}")
print(f"issubclass(HighFlyer, Powerhouse): {issubclass(HighFlyer, Powerhouse)}")

# ── 10. Duck typing – polymorphism ─────────────────────────────────────────
separator("10. Polimorfizm i duck typing")

from game.skills import ActiveSkill, PassiveSkill

skill_list = [
    MOVES_CATALOGUE["Powerhouse"][0],
    PASSIVE_SKILLS["HighFlyer"],
    MOVES_CATALOGUE["Technician"][0],
]

print("\nWszystkie umiejętności implementują metodę apply() (duck typing):")
for skill in skill_list:
    print(f"  {skill.__class__.__name__}: {skill.name} → {skill.apply(rocky)[:60]}")

separator("Demo zakończone pomyślnie! ✓")
