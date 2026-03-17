# 🤼 Wrestling RPG

Projekt semestralny – Programowanie Obiektowe I  
Semestr letni 2025/2026

## Opis projektu

Wrestling RPG to turowa gra fabularna osadzona w świecie wrestlingu, zbudowana z użyciem Streamlit.
Gracz tworzy własnego zawodnika (Powerhouse, HighFlyer lub Technician), wybiera repertuar ruchów,
szkoli się w wrestlingu, zdobywa doświadczenie i pnie się po drabince karier – od szkoły wrestlingu
po lokalną federację.

## Wymagania

- Python 3.10+
- streamlit >= 1.35.0
- pytest >= 7.0.0
- pytest-cov >= 4.0.0 (opcjonalnie)

## Instalacja

```bash
pip install -r requirements.txt
```

## Uruchomienie

### Gra (Streamlit)
```bash
cd wrestling_rpg
streamlit run app.py
```

### Program demonstracyjny (CLI)
```bash
cd wrestling_rpg
python demo.py
```

### Testy jednostkowe
```bash
cd wrestling_rpg
pytest tests/ -v
```

## Struktura projektu

```
wrestling_rpg/
├── game/
│   ├── __init__.py
│   ├── characters.py      # Wrestler (ABC), Powerhouse, HighFlyer, Technician, NPC roster
│   ├── items.py           # Item (ABC), Outfit, Gadget, Protector, Championship
│   ├── skills.py          # Skill (ABC), ActiveSkill, PassiveSkill, katalogi ruchów
│   └── exceptions.py      # Hierarchia własnych wyjątków
├── tests/
│   ├── __init__.py
│   └── test_game.py       # 30+ testów jednostkowych pytest
├── app.py                 # Główna aplikacja Streamlit
├── demo.py                # Program demonstracyjny
├── README.md
├── CHECKLIST.md
├── UZASADNIENIA.md
└── requirements.txt
```

## Klasy gry

| Klasa | Siła | Zręczność | HP | Energia | Pasywna |
|-------|------|-----------|-----|---------|---------|
| Powerhouse | 18 | 6 | 140 | 80 | +15% HP, +5 Siły |
| HighFlyer | 10 | 18 | 100 | 120 | +20% Energii, +5 Zręczności |
| Technician | 13 | 15 | 120 | 100 | +10% HP, +8 Zręczności |

## Zaimplementowane mechaniki OOP

- Klasy abstrakcyjne (ABC): `Wrestler`, `Skill`, `Item`
- Dziedziczenie: 3 klasy postaci, 3 typy przedmiotów, 2 typy umiejętności
- Enkapsulacja: prywatne atrybuty z `@property` i setterami
- Polimorfizm: wspólny interfejs `apply()` dla `ActiveSkill` i `PassiveSkill`
- Kompozycja: `Wrestler` zawiera `StatBonus`, `ActiveSkill`, `PassiveSkill`
- Własne wyjątki: 5 specjalizowanych klas dziedziczących po `WrestlingRPGError`
- Metody specjalne: `__str__`, `__repr__`, `__eq__`, `__lt__`, `__len__`, `__add__`
- Type hints i docstringi dla wszystkich klas i metod publicznych
