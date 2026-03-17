# CHECKLIST – Mechanizmy OOP

## 4.1.1 Podstawy klas
- [X] Klasy i obiekty – `game/characters.py`, `game/items.py`, `game/skills.py`
- [X] Konstruktor `__init__` – wszystkie klasy (Wrestler, Item, Skill, StatBonus)
- [X] Atrybuty instancji – `_name`, `_current_hp`, `_xp` itp. w każdej klasie
- [X] Atrybuty klasy – `Wrestler.total_wrestlers`, `Item.total_items_created`, `Skill.skill_registry`
- [X] Metody instancji – `take_damage()`, `equip()`, `apply()`, `train()`, itd.

## 4.1.2 Enkapsulacja i metody specjalne
- [X] Prywatne atrybuty – `_name`, `_base_strength`, `_current_hp`, `_moves` (konwencja `_protected`)
- [X] `@property` – `name`, `level`, `max_hp`, `effective_strength`, `slot`, `character_class`, itd.
- [X] `@property.setter` – `current_hp`, `current_energy` z clamping validation
- [X] `__str__()` – `Wrestler.__str__`, `Item.__str__`, `Skill.__str__`
- [X] `__repr__()` – `Wrestler.__repr__`, `Item.__repr__`, `Skill.__repr__`
- [X] `__eq__()` – `Wrestler.__eq__`, `Item.__eq__`, `Skill.__eq__`, `StatBonus` (via dataclass)
- [X] Dodatkowa metoda specjalna – `__lt__` (Wrestler, Item, Skill), `__len__` (Wrestler, Item), `__add__` (StatBonus)

## 4.1.3 Dziedziczenie
- [X] Klasa bazowa – `Wrestler` (characters.py), `Item` (items.py), `Skill` (skills.py)
- [X] Klasy pochodne – `Powerhouse`, `HighFlyer`, `Technician`; `Outfit`, `Gadget`, `Protector`, `Championship`; `ActiveSkill`, `PassiveSkill`
- [X] `super()` – wywołania w konstruktorach wszystkich klas pochodnych
- [X] Nadpisywanie metod – `character_class`, `level_up_bonus`, `slot`, `item_type_label`, `apply`, `check_requirements`
- [X] `isinstance()` i `issubclass()` – `characters.py:npc_choose_move`, `demo.py`, `tests/test_game.py`

## 4.1.4 Polimorfizm
- [X] Polimorfizm – `apply()` wywołana na `ActiveSkill` i `PassiveSkill` daje różne efekty
- [X] Duck typing – lista `[ActiveSkill, PassiveSkill]` używa wspólnego interfejsu `apply()` (demo.py:153, test_game.py:TestSpecialMethods::test_polymorphism_apply)

## 4.1.5 Kompozycja i agregacja
- [X] Kompozycja – `Wrestler` tworzy i zarządza `_equipped: dict[slot, Item]` (silne powiązanie)
- [X] Agregacja – `Wrestler` przechowuje referencje do `ActiveSkill` w `_moves` (słabe powiązanie – skille istnieją w katalogach niezależnie)

## 4.1.6 Klasy abstrakcyjne i operatory
- [X] Klasa abstrakcyjna (ABC) – `Wrestler`, `Item`, `Skill` (importują `ABC` z modułu `abc`)
- [X] `@abstractmethod` – `character_class`, `level_up_bonus` (Wrestler); `slot`, `item_type_label`, `check_requirements` (Item); `apply` (Skill)
- [X] Przeciążanie operatorów – `__add__` (StatBonus), `__lt__` (Wrestler, Item, Skill), `__len__` (Wrestler, Item)

## 4.1.7 Wyjątki
- [X] Własny wyjątek bazowy – `WrestlingRPGError(Exception)` – `game/exceptions.py:8`
- [X] Hierarchia wyjątków – `InsufficientEnergyError`, `ItemRequirementError`, `InvalidStatValueError`, `FinisherNotAvailableError`, `InvalidMoveError`
- [X] Zgłaszanie wyjątków – `raise` w `check_requirements`, `spend_energy`, `apply` (skills.py)
- [X] Obsługa wyjątków – `try-except` w `app.py`, `demo.py`, `tests/test_game.py`

## 4.1.8 Testowanie i dokumentacja
- [X] Testy pytest – `tests/test_game.py` – 35+ testów
- [X] Docstringi – dla wszystkich klas i metod publicznych (format Google)
- [X] Type hints – dla wszystkich parametrów i wartości zwracanych metod publicznych
