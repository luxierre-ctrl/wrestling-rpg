# UZASADNIENIA PROJEKTOWE

## 1. Wybór klasy abstrakcyjnej

**Które klasy są ABC i dlaczego?**  
Trzy klasy zostały zdefiniowane jako abstrakcyjne: `Wrestler`, `Item` oraz `Skill`.

- `Wrestler` – istnieje wyłącznie po to, by być rozszerzonym. Bezpośrednia instancja `Wrestler("Jan")` nie miałaby zdefiniowanego `character_class` ani `level_up_bonus`, co uczyniłoby ją niepoprawną w logice gry.  
- `Item` – podobnie, „item bez kategorii" nie ma sensu: nie wiadomo do jakiego slotu go przypisać. Klasy pochodne (`Outfit`, `Gadget`, `Protector`, `Championship`) definiują te szczegóły.  
- `Skill` – metoda `apply()` musi być zaimplementowana inaczej w `ActiveSkill` (zadaje obrażenia, kosztuje energię) i `PassiveSkill` (zwraca info, bo efekt liczy się inaczej).

**Metody abstrakcyjne:**  
- `Wrestler.character_class` i `level_up_bonus` – muszą być znane w każdej klasie, bo wpływają na obliczenia statystyk.  
- `Item.slot` i `item_type_label` – potrzebne do systemu ekwipunku (grupowanie slotów).  
- `Skill.apply()` – kluczowy polimorficzny punkt systemu walki.

**Metody konkretne w ABC:**  
`Wrestler` zawiera dużą ilość konkretnych metod (`take_damage`, `gain_xp`, `train`), bo logika jest wspólna dla wszystkich klas postaci i nie ma powodu jej powielać.

---

## 2. Wybór relacji między obiektami

**Kompozycja:**  
`Wrestler` zawiera słownik `_equipped: dict[str, Optional[Item]]`. Choć items mogą istnieć niezależnie (są też w inventory), equip-slot jest integralną częścią wrestlera – gdyby wrestlera usunąć, slot znika razem z nim. To silne powiązanie (kompozycja).

Drugi przykład: `StatBonus` jest tworzony i zarządzany wewnątrz `Item`. Bez `Item` `StatBonus` tego konkretnego przedmiotu traci kontekst.

**Agregacja:**  
`Wrestler._moves: list[ActiveSkill]` – skille istnieją w globalnych katalogach (`MOVES_CATALOGUE`) niezależnie od postaci. Postać jedynie trzyma referencje. To agregacja.

---

## 3. Implementacja umiejętności pasywnych

Pasywne umiejętności są obiektami klasy `PassiveSkill` przechowywanymi w globalnym słowniku `PASSIVE_SKILLS` (skills.py). Każda klasa postaci pobiera swój pasywny przez `wrestler.passive_skill`.

Efekt pasywny **nie jest aplikowany przez metodę `apply()`** (ta tylko zwraca tekst informacyjny), lecz jest **wbudowany w obliczenia efektywnych statystyk**: `max_hp` i `max_energy` stosują mnożnik procentowy, a `effective_strength` i `effective_dexterity` dodają flat bonus z `passive_skill.strength_bonus` / `dexterity_bonus`.

Dzięki temu efekt pasywny jest zawsze aktualny i nie wymaga ręcznego aplikowania ani cofania.

---

## 4. System przedmiotów

**Reprezentacja konkretnych przedmiotów:**  
Konkretne przedmioty są instancjami klas (`Outfit`, `Gadget`, itd.), nie osobnymi klasami. Tworzenie osobnej klasy dla np. `BasicKneePads` byłoby nadmiernym podziałem (over-engineering). Katalogi (np. `PROTECTORS`) trzymają gotowe instancje.

**Modyfikacja statystyk:**  
Przedmioty modyfikują statystyki przez `StatBonus`. Metody `effective_strength`, `max_hp` itd. sumują `_item_bonuses()` ze wszystkich slotów. Nie ma potrzeby cache'owania – obliczenia są lekkie.

**Sprawdzanie wymagań:**  
Metoda `Item.check_requirements(wrestler_level)` jest wywoływana przez `Wrestler.equip()`. Rzuca `ItemRequirementError` jeśli warunek nie jest spełniony. `Championship.check_requirements` jest nadpisana jako no-op (pasy nie mają wymagań poziomowych – są nagrodą fabularną).

---

## 5. Przeciążone operatory

| Operator | Klasa | Uzasadnienie |
|---|---|---|
| `__add__` | `StatBonus` | Naturalna semantyka: suma bonusów z kilku źródeł (item + level + passive). Pozwala na `total = bonus1 + bonus2`. |
| `__lt__` | `Wrestler` | Sortowanie zawodników po sile (po poziomie, potem po statystykach) – przydatne przy doborze rywali. |
| `__lt__` | `Item` | Sortowanie przedmiotów po wymaganym poziomie – przydatne przy wyświetlaniu listy przedmiotów. |
| `__lt__` | `Skill` | Sortowanie alfabetyczne umiejętności. |
| `__len__` | `Wrestler` | Liczba przedmiotów w inventory – intuicyjne `len(wrestler)`. |
| `__len__` | `Item` | Suma wartości bonusów – szybkie porównanie „siły" przedmiotu. |

---

## 6. Hierarchia wyjątków

```
WrestlingRPGError (bazowy)
├── InsufficientEnergyError  – brak energii na ruch
├── ItemRequirementError     – za niski poziom do założenia przedmiotu
├── InvalidStatValueError    – próba ustawienia statystyki poza zakresem
├── FinisherNotAvailableError – finisher gdy rywal ma ≥ 35% HP
└── InvalidMoveError         – użycie ruchu spoza zestawu postaci
```

Wspólny bazowy `WrestlingRPGError` pozwala na globalny catch (`except WrestlingRPGError`) tam gdzie nie zależy nam na rodzaju błędu. Specjalizowane wyjątki dają precyzyjną obsługę (np. Streamlit pokazuje inny komunikat dla braku energii vs. wymagań przedmiotu).

---

## 7. Dodatkowe decyzje

**Dwa rozdziały fabularne:**  
System `chapter` + `school_wins` w session_state Streamlit pozwala na prostą progresję fabularną bez potrzeby osobnego silnika narracji.

**NPC Roster:**  
15 NPC-ów o różnych poziomach zapewnia skalującą trudność. Funkcja `npc_choose_move()` implementuje prostą AI: priorytet finishera, potem losowy affordowalny ruch, awaryjne użycie adrenaliny.

**Streamlit session_state jako model stanu gry:**  
Zamiast bazy danych, cały stan gry (postać, dzień, dziennik) jest trzymany w `st.session_state`. To wystarczy dla projektu tej skali i eliminuje potrzebę persistence layer.
