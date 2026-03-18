"""
Squared Circle: Wrestling RPG – Main Streamlit Application.
v4 – kinematyczny wstęp, park/Kaz/piwnica, system intro_step
"""

import random
import streamlit as st

from game.characters import (
    Powerhouse, HighFlyer, Technician, Wrestler,
    build_npc_roster, npc_choose_move,
)
from game.items import STARTER_ITEMS, CHAMPIONSHIPS
from game.skills import MOVES_CATALOGUE, FINISHER_CATALOGUE
from game.exceptions import (
    InsufficientEnergyError, FinisherNotAvailableError,
    ItemRequirementError,
)
from game.assets import LOGO_CREATOR_B64, LOGO_GAME_B64

# ══════════════════════════════════════════════════════════════════════════════
# LORE & DIALOGI
# ══════════════════════════════════════════════════════════════════════════════

CLASS_COMMENTS = {
    "Powerhouse": "...jak lodówka. Dobra. Siłacze się przydają. Ale bez głowy to tylko mebel.",
    "HighFlyer":  "...ktoś kto zaraz spadnie z dachu. Akrobaci. Zawsze myślą że latanie wystarczy.",
    "Technician": "...ktoś kto za dużo myśli. Technicy. Lubię technicznych. Rzadko głupio giną.",
}

CLASS_ENTER = {
    "Powerhouse": "Wskazuje na ring.<br><b>– Wejdź. Zobaczymy czy ta lodówka umie się ruszać.</b>",
    "HighFlyer":  "Wskazuje na ring.<br><b>– Wejdź. I nie spadnij.</b>",
    "Technician": "Wskazuje na ring.<br><b>– Wejdź. I pokaż mi czy myślenie ci pomaga.</b>",
}

TRENER_QUOTES = [
    "Kaz patrzy jak ćwiczysz. Nic nie mówi. To dobry znak.",
    "– Jeszcze raz – warczy Kaz. – Jakbyś robił to po raz pierwszy.",
    "– Nieźle – mówi Kaz i odchodzi. Pochwała od Kaza to jak Oscar.",
    "Kaz rzuca ci ręcznik. – Woda. Nie zdychaj mi tu.",
    "– Widziałem gorszych – mówi Kaz. – Ale nie wielu.",
    "– Ból to informacja – mówi Kaz. – Słuchaj jej, ale nie słuchaj za długo.",
    "– Nikt nie pamięta drugiego miejsca – warczy Kaz. – Trenuj mocniej.",
    "Kaz poprawia twój uchwyt bez słowa. Potem kiwa głową. To jego wersja komplementu.",
]

NPC_LORE = {
    "Rocky Bułka":       "Kaz: <i>– Rocky. Syn piekarza z Końskich. Silny jak wół, powolny jak wół. Nie daj mu się złapać.</i>",
    "Timmy Flip":        "Kaz: <i>– Timmy. Oglądał za dużo WWE jako dziecko. Myśli że jest Rey Mysterio. Pokaż mu że nie jest.</i>",
    "Grzegorz Dźwignia": "Kaz: <i>– Grzegorz. Były judoka. Uważaj na chwyty – wie co robi. Jedyny tu co myśli.</i>",
    "Bartek Mocarz":     "Kaz: <i>– Bartek jest tu rok. Myśli że już wszystko umie. Takim trzeba pokazać że nie umieją.</i>",
    "Salto Stasiu":      "Kaz: <i>– Stasiu. Dobry chłopak, za bardzo się stara. Przez to robi błędy. Wykorzystaj to.</i>",
    "Adam Dusiciel":     "Bożena szepcze: <i>– Uważaj na Adama. Całkiem miły poza ringiem. W ringu jakby ktoś go przełączał.</i>",
    "Wielki Zbyszek":    "<b>– ZBYSZEK CIĘ ZMIAŻDŻY!</b> – ryczy przez całą szatnię.<br>Bożena: <i>– Nie przejmuj się. Jego mama mówi że w domu jest bardzo spokojny.</i>",
    "Lotny Krzysztof":   "Krzysztof podaje rękę: <i>– Cześć. Przepraszam z góry za to co zrobię. Naprawdę mi przykro.</i><br>Uśmiecha się i odchodzi.",
    "Mistrz Janusz":     "Janusz mówi do nieistniejącego menadżera: <i>– Powiedzcie temu nowemu że Janusz nie rozmawia z nikim poniżej TOP 5.</i><br>Jesteście sami w szatni.",
    "Destruktor Marek":  "Bożena: <i>– Marek jest tu od 3 lat. Bije każdego. Ale płaci składkę punktualnie, więc co zrobisz.</i>",
    "Feniks Radek":      "Radek nie odwraca się: <i>– Słyszałem o tobie. Kaz cię trenował. To znaczy że umiesz walczyć.</i><br><i>– Ale ja też umiem.</i>",
    "Żelazny Piotr":     "<i>– Wiesz co jest różnica między tobą a mną? Ja byłem tu 12 lat temu tam gdzie ty jesteś. Przetrwałem.</i><br><i>– Zobaczymy czy ty też.</i>",
    "Kolos Waldemar":    "Bożena ścisza głos: <i>– Waldemar to były ochroniarz. Nie wiem czy to jest oficjalne zawodnictwo czy coś innego. Powodzenia, skarbie.</i>",
    "Profesor Zygmunt":  "<i>– Interesujący okaz – mówi Zygmunt, notując coś w zeszycie. – Sprawdzimy twoją odporność na ból.</i>",
    "Legenda \u2013 El Aguila": "Bożena wstaje od biurka.<br><i>– To jest El Aguila. Przyjeżdża z Warszawy specjalnie. To... duże. Naprawdę duże.</i>",
}

AFTER_WIN_SCHOOL = {
    1: "Kaz podchodzi. Długa chwila ciszy.<br><i>– Żyjesz. Na dziś wystarczy.</i>",
    3: "<i>– Zaczynasz wyglądać jak zawodnik – mówi Kaz. – Zaczynasz</i> – dodaje szybko.",
    5: (
        "Kaz siada na krawędzi ringu. Pierwszy raz nie stoi.<br>"
        "<i>– Nauczyłem cię wszystkiego co mogę nauczyć w piwnicy.</i><br>"
        "Milczy chwilę.<br>"
        "<i>– Jest w Radomiu federacja. Lokalna, mała. Ale prawdziwa.</i><br>"
        "<i>– Chcesz – mogę zadzwonić do Staszka.</i>"
    ),
}

AFTER_WIN_FED = {
    1: "Bożena klaszcze raz, ceremonialnie. <i>– Witamy w tabeli wyników, skarbie.</i>",
    3: (
        "Bożena wychodzi zza biurka – pierwszy raz odkąd tu jesteś.<br>"
        "<i>– Kaz dzwonił. Pytał jak ci idzie. Powiedziałam że nieźle.</i><br>"
        "<i>– Co odpowiedział? – pytasz.</i><br>"
        "<i>– 'Nieźle to za mało' – mówi z uśmiechem. – Ale on tak zawsze.</i>"
    ),
    7: (
        "W szatni czekasz sam. Wchodzi <b>Destruktor Marek</b>.<br>"
        "<i>– Słyszałem że robisz postępy. Kaz cię trenował. Mnie też. Dawno temu.</i><br>"
        "Wstaje.<br>"
        "<i>– Pokonaj Waldemara. Zasłuż na pas. A potem – przyjedź do Warszawy.</i><br>"
        "Wychodzi zanim zdążysz odpowiedzieć."
    ),
}

CHAMPIONSHIP_STORY = {
    "Local Championship": (
        "🎺 <b>NOWY MISTRZ LOKALNEJ FEDERACJI!</b><br><br>"
        "Ring. Kilkaset osób krzyczy. Sędzia unosi twoją rękę.<br>"
        "W pierwszym rzędzie siedzą Bożena i... Kaz.<br>"
        "Kaz nie klaszcze. Ale kiwa głową.<br>"
        "<i>To wystarczy.</i>"
    ),
    "National Championship": (
        "🏆 <b>MISTRZ KRAJOWY!</b><br><br>"
        "Światła. Hałas. Pas ląduje na twoich ramionach.<br>"
        "Gdzieś w tłumie Kaz stoi z założonymi rękami.<br>"
        "<i>– Wiedziałem – mówi cicho, do siebie.</i><br><br>"
        "<i>Droga na szczyt właśnie się zaczęła.</i>"
    ),
}

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG & CSS
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Squared Circle",
    page_icon="🤼",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Wymuś ciemny motyw – nadpisz jasne kolory Streamlita
st.markdown("""
<style>
/* Wymuś ciemne tło nawet gdy Streamlit Cloud ładuje jasny motyw */
html, body, [data-testid="stAppViewContainer"], 
[data-testid="stMain"], .main, 
[data-testid="stHeader"] {
    background-color: #0f0f1a !important;
    color: #eeeeee !important;
}
[data-testid="stSidebar"] { background-color: #1a1a2e !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif;
    font-size: 15px;
}

h1 { font-family: 'Bebas Neue', sans-serif; letter-spacing: 2px; font-size: 2.2rem !important; margin-bottom: 0.4rem !important; }
h2 { font-family: 'Bebas Neue', sans-serif; font-size: 1.5rem !important; margin-bottom: 0.3rem !important; }
h3 { font-family: 'Bebas Neue', sans-serif; font-size: 1.2rem !important; margin-bottom: 0.25rem !important; }

.main .block-container {
    max-width: 860px;
    padding-top: 0.6rem;
    padding-bottom: 1rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

/* Zawsze wąski jak telefon – na każdym urządzeniu */
.main .block-container {
    max-width: 480px !important;
    margin: 0 auto !important;
}

/* ── MOBILE COMPACT ── */
@media (max-width: 768px) {
    .main .block-container {
        padding-left: 0.4rem !important;
        padding-right: 0.4rem !important;
        padding-top: 0.3rem !important;
    }
    /* Metryki w 2 kolumnach na telefonie */
    div[data-testid="metric-container"] {
        padding: 3px 4px !important;
    }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 1rem !important;
    }
    /* Mniejsze przyciski na tel */
    div[data-testid="stButton"] > button {
        font-size: 0.75rem !important;
        padding: 0.2rem 0.4rem !important;
    }
    /* Mniejsze bary */
    .bar-bg { height: 7px !important; margin: 1px 0 4px 0 !important; }
    .hp-bar, .en-bar, .npc-bar, .npc-en-bar { height: 7px !important; }
    /* Kompaktowe stat-boxy */
    .stat-box { padding: 4px 8px !important; font-size: 0.78rem !important; margin: 2px 0 !important; }
    /* Dziennik mniejszy na tel */
    .journal-box { height: 220px !important; font-size: 0.76rem !important; }
    /* Lore box */
    .lore-box { padding: 7px 10px !important; font-size: 0.8rem !important; }
}

.stMarkdown p { font-size: 0.9rem; margin-bottom: 0.25rem; }
.stCaption, [data-testid="stCaptionContainer"] p { font-size: 0.82rem !important; }

button[data-baseweb="tab"] {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1rem !important;
    letter-spacing: 1px;
    padding: 6px 18px !important;
}

/* ── INTRO STYLES ── */
.intro-screen {
    max-width: 680px;
    margin: 0 auto;
    padding: 2rem 0 1rem 0;
}

.intro-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3.5rem;
    color: #e94560;
    letter-spacing: 4px;
    text-align: center;
    margin-bottom: 0.2rem;
}

.intro-subtitle {
    text-align: center;
    color: #666;
    font-size: 0.8rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 2rem;
}

.scene-box {
    background: #0a0a14;
    border: 1px solid #1e1e2e;
    border-radius: 8px;
    padding: 2rem 2.5rem;
    margin: 1rem 0;
    color: #ccc;
    font-size: 0.95rem;
    line-height: 1.9;
}

.scene-time {
    color: #e94560;
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1rem;
    letter-spacing: 3px;
    margin-bottom: 1.2rem;
    display: block;
}

.scene-pause {
    display: block;
    height: 0.8rem;
}

.dialogue {
    color: #fff;
    font-weight: 600;
    font-size: 1rem;
}

.choice-info {
    color: #888;
    font-size: 0.78rem;
    text-align: center;
    margin-top: 0.5rem;
    font-style: italic;
}

/* ── GAME STYLES ── */
.stat-box {
    background: #1a1a2e;
    border: 1px solid #e94560;
    border-radius: 6px;
    padding: 6px 11px;
    margin: 3px 0;
    color: #eee;
    font-size: 0.84rem;
    line-height: 1.5;
}

.stat-label {
    color: #e94560;
    font-weight: 700;
    font-size: 0.73rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.lore-box {
    background: #0e0e1c;
    border-left: 3px solid #e94560;
    border-radius: 0 6px 6px 0;
    padding: 10px 16px;
    margin: 8px 0;
    color: #ccc;
    font-size: 0.88rem;
    line-height: 1.7;
}

.journal-box {
    background: #0f0f1a;
    border: 1px solid #2a2a3e;
    border-radius: 6px;
    padding: 10px 14px;
    height: 180px;
    overflow-y: auto;
    color: #bbb;
    font-size: 0.84rem;
    line-height: 1.6;
}

.chapter-badge {
    background: #e94560;
    color: white;
    padding: 2px 10px;
    border-radius: 10px;
    font-size: 0.73rem;
    font-weight: 700;
    letter-spacing: 0.5px;
}

.bar-bg {
    background: #2a2a3a;
    border-radius: 3px;
    height: 10px;
    margin: 2px 0 7px 0;
}
.hp-bar     { background: #e94560; border-radius: 3px; height: 10px; }
.en-bar     { background: #4ecdc4; border-radius: 3px; height: 10px; }
.npc-bar    { background: #f39c12; border-radius: 3px; height: 10px; }
.npc-en-bar { background: #9b59b6; border-radius: 3px; height: 10px; }

div[data-testid="stButton"] > button {
    border-radius: 5px;
    font-weight: 600;
    font-size: 0.84rem;
    padding: 0.28rem 0.7rem;
}

div[data-testid="metric-container"] { padding: 5px 7px !important; }
div[data-testid="metric-container"] label { font-size: 0.76rem !important; }
div[data-testid="metric-container"] [data-testid="stMetricValue"] { font-size: 1.2rem !important; }

details summary { font-size: 0.84rem !important; }
hr { margin: 0.5rem 0 !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════

def _init_state() -> None:
    defaults = {
        "phase": "splash",
        "splash_step": 0,
        "intro_step": 0,
        "intro_fear_choice": None,
        "player": None,
        "player_name_input": "",
        "selected_class": "Powerhouse",
        "day": 1,
        "chapter": 1,
        "school_wins": 0,
        "federation_wins": 0,
        "journal": [],
        "npc_roster": build_npc_roster(),
        "current_npc": None,
        "battle_log": [],
        "battle_over": False,
        "battle_won": None,
        "offered_chapter2": False,
        "train_count": 0,
        "chapter2_declined_day": -99,
        "fight_day_npc": None,
        "fight_day_npc_day": -1,
        "npc_adrenaline_streak": 0,
        "last_event": "",
        "show_equip": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

def log(msg: str) -> None:
    st.session_state.journal.insert(0, msg)
    # Ważne wydarzenia trafiają też do paska
    if any(x in msg for x in ["🏆", "⭐", "💥", "🎁", "🥊", "💀", "📖", "🏅"]):
        import re
        clean = re.sub(r"<[^>]+>", "", msg).strip()
        st.session_state.last_event = clean

def blog(msg: str) -> None:
    st.session_state.battle_log.append(msg)

def next_intro() -> None:
    st.session_state.intro_step += 1
    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def pick_npc_for_fight() -> Wrestler:
    player: Wrestler = st.session_state.player
    roster: list[Wrestler] = st.session_state.npc_roster
    school_wins = st.session_state.school_wins

    if st.session_state.chapter == 1:
        # Pierwsze 2 wygrane – TYLKO Lvl 1 rywale
        # Potem – do Lvl player+1 (stopniowe trudniejsze)
        if school_wins < 2:
            pool = [n for n in roster if n.level == 1]
        elif school_wins < 4:
            pool = [n for n in roster if n.level <= 2]
        else:
            pool = [n for n in roster if n.level <= max(2, player.level)]
    else:
        fed_wins = st.session_state.federation_wins
        if fed_wins < 2:
            pool = [n for n in roster if n.level == 3]
        elif fed_wins < 5:
            pool = [n for n in roster if 3 <= n.level <= 4]
        else:
            pool = [n for n in roster if n.level >= 4]

    pool = pool or roster
    npc = random.choice(pool)
    npc.restore_to_full()
    return npc

def _bar(current: int, maximum: int, css_class: str, label: str) -> str:
    pct = int((current / maximum) * 100) if maximum > 0 else 0
    return (
        f'<div class="stat-label">{label}: {current}/{maximum}</div>'
        f'<div class="bar-bg"><div class="{css_class}" style="width:{pct}%"></div></div>'
    )

def _lore(text: str) -> None:
    st.markdown(f'<div class="lore-box">{text}</div>', unsafe_allow_html=True)

def _scene(content: str) -> None:
    st.markdown(f'<div class="scene-box">{content}</div>', unsafe_allow_html=True)

def _centered_btn(label: str, key: str, primary: bool = True) -> bool:
    col1, col2, col3 = st.columns([2, 3, 2])
    with col2:
        return st.button(label, key=key,
                         type="primary" if primary else "secondary",
                         use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PHASE: SPLASH SCREEN
# ══════════════════════════════════════════════════════════════════════════════

def phase_splash() -> None:
    """Animowany splash screen: logo twórcy → logo gry → przycisk Graj."""
    step = st.session_state.splash_step

    st.markdown("""
    <style>
    @keyframes fadeIn {
        from { opacity: 0; transform: scale(0.94); }
        to   { opacity: 1; transform: scale(1); }
    }
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(24px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .splash-creator {
        text-align: center;
        width: 100%;
    }
    .splash-creator img {
        max-width: 460px;
        width: 75vw;
        display: inline-block;
        animation: fadeIn 1.2s ease forwards;
    }
    .splash-presents {
        color: #555;
        font-family: 'Bebas Neue', sans-serif;
        letter-spacing: 6px;
        font-size: 1rem;
        margin-top: 1rem;
        animation: fadeIn 1.5s ease 0.8s both;
        text-transform: uppercase;
        text-align: center;
    }
    .splash-game {
        text-align: center;
        width: 100%;
    }
    .splash-game img {
        max-width: 800px;
        width: 88vw;
        display: inline-block;
        animation: fadeIn 1.4s ease forwards;
        border-radius: 10px;
    }
    .splash-btn-wrap {
        margin-top: 2rem;
        animation: slideUp 0.8s ease 0.5s both;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── KROK 0: Logo twórcy ───────────────────────────────────────────────────
    if step == 0:
        st.markdown(
            f'''<div class="splash-creator">
                <img src="data:image/png;base64,{LOGO_CREATOR_B64}" alt="Don Kiepa Games"/>
                <div class="splash-presents">prezentuje</div>
            </div>''',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3, 2, 3])
        with col2:
            if st.button("Dalej →", key="splash_next", type="primary", use_container_width=True):
                st.session_state.splash_step = 1
                st.rerun()

    # ── KROK 1: Logo gry + przycisk Graj ─────────────────────────────────────
    elif step == 1:
        st.markdown(
            f'''<div class="splash-game">
                <img src="data:image/png;base64,{LOGO_GAME_B64}" alt="Squared Circle Wrestling RPG"/>
            </div>''',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="splash-btn-wrap">',
            unsafe_allow_html=True,
        )
        col1, col2, col3 = st.columns([3, 2, 3])
        with col2:
            if st.button("🤼  GRAJ!", key="splash_play", type="primary", use_container_width=True):
                st.session_state.phase = "intro"
                st.rerun()
    

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PHASE: INTRO – kinematyczny wstęp
# ══════════════════════════════════════════════════════════════════════════════

def phase_intro() -> None:
    step = st.session_state.intro_step

    st.markdown('<div class="intro-screen">', unsafe_allow_html=True)

    # ── KROK 0: Tytuł i początek ─────────────────────────────────────────────
    if step == 0:
        st.markdown('<div class="intro-title">SQUARED CIRCLE</div>', unsafe_allow_html=True)
        st.markdown('<div class="intro-subtitle">Wrestling RPG &nbsp;&middot;&nbsp; Droga na szczyt</div>', unsafe_allow_html=True)

        _scene(
            '<span class="scene-time">RADOM. WTOREK. 23:14.</span>'
            'Wracasz do domu przez park przy Żeromskiego.<br>'
            'Słuchawki w uszach. Muzyka za głośna żeby słyszeć cokolwiek.<br>'
            'Normalny wieczór.<br>'
            '<span class="scene-pause"></span>'
            'Potem słyszysz.<br>'
            '<span class="scene-pause"></span>'
            'Nie muzykę – muzyka dalej gra.<br>'
            'Coś innego. Coś <i>przez</i> muzykę.<br>'
            '<span class="scene-pause"></span>'
            'Wyciągasz słuchawki.'
        )
        if _centered_btn("Dalej →", "intro_0"):
            next_intro()

    # ── KROK 1: Scena w parku ─────────────────────────────────────────────────
    elif step == 1:
        _scene(
            'Za rogiem.<br>'
            'Trzech mężczyzn. Jeden leży.<br>'
            'Kopią go bez słowa. Bez emocji. <i>Jak pracę.</i><br>'
            '<span class="scene-pause"></span>'
            'Stoisz.<br>'
            'Trzy sekundy. Może pięć.<br>'
            '<span class="scene-pause"></span>'
            'Potem coś w tobie podejmuje decyzję zanim ty zdążysz.'
        )
        if _centered_btn("– Hej!", "intro_1"):
            next_intro()
        st.markdown('<div class="choice-info">[ jedyna opcja ]</div>', unsafe_allow_html=True)

    # ── KROK 2: Ucieczka, Kaz wstaje ─────────────────────────────────────────
    elif step == 2:
        _scene(
            'Krzyczysz.<br>'
            'Trzej mężczyźni zatrzymują się.<br>'
            'Patrzą na ciebie.<br>'
            'Ty patrzysz na nich.<br>'
            '<span class="scene-pause"></span>'
            'Nikt się nie rusza przez chwilę która trwa za długo.<br>'
            '<span class="scene-pause"></span>'
            'Potem – uciekają.<br>'
            'Bez słowa. Bez pośpiechu. Jakby po prostu skończyli robotę.<br>'
            '<span class="scene-pause"></span>'
            'Leżący człowiek nie prosi o pomoc.<br>'
            'Nie krzyczy.<br>'
            'Po prostu – powoli – siada.<br>'
            '<span class="scene-pause"></span>'
            'Starszy. Siwy. Twarz jak wykuta z kamienia.<br>'
            'Rozcięta brew. Krew na dresie.<br>'
            'Patrzy przed siebie przez chwilę.<br>'
            '<span class="scene-pause"></span>'
            '<span class="dialogue">– Trzech na jednego. Mogło być gorzej.</span>'
        )
        if _centered_btn("Pomóż mu wstać →", "intro_2"):
            next_intro()

    # ── KROK 3: Pytanie o strach ──────────────────────────────────────────────
    elif step == 3:
        _scene(
            'Wyciągasz rękę.<br>'
            'Bierze ją bez słowa. Wstaje.<br>'
            'Jest cięższy niż myślałeś.<br>'
            '<span class="scene-pause"></span>'
            'Mężczyzna patrzy na ciebie.<br>'
            'Długo. Uważnie.<br>'
            'Jak ktoś kto całe życie uczył się oceniać ludzi w kilka sekund.<br>'
            '<span class="scene-pause"></span>'
            '<span class="dialogue">– Bałeś się?</span>'
        )

        st.markdown("**Twoja odpowiedź:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Tak. Ale i tak\nkrzyknąłem.", key="fear_a", use_container_width=True, type="primary"):
                st.session_state.intro_fear_choice = "A"
                next_intro()
        with col2:
            if st.button("Nie miałem\nczasu się bać.", key="fear_b", use_container_width=True, type="primary"):
                st.session_state.intro_fear_choice = "B"
                next_intro()
        with col3:
            if st.button("Szczerze?\nTrochę.", key="fear_c", use_container_width=True, type="primary"):
                st.session_state.intro_fear_choice = "C"
                next_intro()

    # ── KROK 4: Kaz się przedstawia ──────────────────────────────────────────
    elif step == 4:
        fear = st.session_state.intro_fear_choice
        reactions = {
            "A": "Kaz kiwa głową powoli.<br><i>– Tak jest lepiej niż się nie bać. Kto się nie boi – głupi albo martwy.</i><br><span class='scene-pause'></span>",
            "B": "Kaz patrzy na ciebie przez chwilę.<br><i>– Instynkt. To się przydaje. Myślenie można nauczyć. Instynktu – nie.</i><br><span class='scene-pause'></span>",
            "C": "Kącik ust Kaza unosi się minimalnie. Prawie uśmiech.<br><i>– Szczerość. Rzadka rzecz.</i><br><span class='scene-pause'></span>",
        }
        reaction = reactions.get(fear or "B", "")

        _scene(
            reaction +
            '<span class="dialogue">– Kaz – mówi. – Kazimierz Wróbel.</span><br>'
            'Podaje rękę. Uścisk jak imadło.<br>'
            '<span class="scene-pause"></span>'
            '<span class="dialogue">– Żeromskiego 14. Piwnica. Jutro. Siódma rano.</span><br>'
            '<span class="scene-pause"></span>'
            'Odwraca się i odchodzi.<br>'
            'Bez dziękuję.<br>'
            'Bez wyjaśnienia.<br>'
            'Bez obejrzenia się.<br>'
            '<span class="scene-pause"></span>'
            'Stoisz sam w parku.<br>'
            'Słuchawki w ręku.<br>'
            'Muzyka dalej gra – do nikogo.<br>'
            '<span class="scene-pause"></span>'
            'Idziesz do domu.<br>'
            'Przez całą noc nie wiesz czy pójdziesz.<br>'
            '<i>Nad ranem wiesz.</i>'
        )
        if _centered_btn("Następnego dnia... →", "intro_4"):
            next_intro()

    # ── KROK 5: Drzwi do piwnicy ─────────────────────────────────────────────
    elif step == 5:
        st.markdown(
            '<div style="text-align:center;color:#555;font-size:0.8rem;'
            'letter-spacing:3px;text-transform:uppercase;padding:1rem 0 0.5rem 0;">'
            'Następnego dnia. 6:58.</div>',
            unsafe_allow_html=True
        )
        _scene(
            'Żeromskiego 14.<br>'
            'Zardzewiałe drzwi w suterenie.<br>'
            'Odrapany napis na ścianie: <b>ZELAZNA PIWNICA – Szkola Wrestlingu</b><br>'
            '<i>(literę Ł ktoś domalował markerem, krzywo)</i><br>'
            '<span class="scene-pause"></span>'
            'Przez drzwi słychać odgłosy upadków.<br>'
            'I sapanie.<br>'
            'I coś co brzmi jak ciało uderzające o matę.<br>'
            '<span class="scene-pause"></span>'
            'Bierzesz głęboki oddech.'
        )
        if _centered_btn("Wejdź", "intro_5"):
            next_intro()

    # ── KROK 6: Środek piwnicy + tworzenie postaci ────────────────────────────
    elif step == 6:
        _scene(
            'Środek jest większy niż myślałeś.<br>'
            'Ring po środku. Stary, z poplamionym płótnem.<br>'
            'Worki treningowe pod ścianą. Ciężary. Lusterko.<br>'
            'Na ścianie zdjęcia – zawodnicy, walki, areny.<br>'
            'Na jednym zdjęciu – <i>młody mężczyzna z pasem mistrzowskim.</i><br>'
            'Twarz znajoma. Młodsza. Ale te same oczy.<br>'
            '<span class="scene-pause"></span>'
            '<span class="dialogue">– Myślałem że nie przyjdziesz.</span><br>'
            '<span class="scene-pause"></span>'
            'Kaz stoi przy ringu. Plaster na brwi. Jakby nic.<br>'
            '<span class="scene-pause"></span>'
            '<span class="dialogue">– Większość nie przychodzi.</span><br>'
            '<span class="scene-pause"></span>'
            '<span class="dialogue">– Jak masz na imię. I jak chcesz żeby cię zwali na ringu.</span>'
        )

        name = st.text_input(
            "Twoje imię na ringu:",
            max_chars=24,
            placeholder="np. El Diablo",
            key="name_input_field"
        )

        if st.button("Dalej →", key="intro_6", type="primary",
                     disabled=not name.strip()):
            st.session_state.player_name_input = name.strip()
            next_intro()

    # ── KROK 7: Wybór klasy ───────────────────────────────────────────────────
    elif step == 7:
        name = st.session_state.player_name_input
        _scene(
            f'Kaz zapisuje w notesie. Nie patrzy na ciebie.<br>'
            f'<span class="scene-pause"></span>'
            f'<span class="dialogue">– I co ty właściwie umiesz?</span><br>'
            f'<span class="dialogue">– Bo wyglądasz jak...</span>'
        )

        cls_info = {
            "Powerhouse": {"icon": "🏋️", "stats": "Siła 18 · Zr 6 · HP 140 · En 80",   "desc": "Siłacz. Wysoka Siła i HP, niska Zręczność."},
            "HighFlyer":  {"icon": "🦅", "stats": "Siła 10 · Zr 18 · HP 100 · En 120", "desc": "Akrobata. Wysoka Zręczność i Energia, niskie HP."},
            "Technician": {"icon": "🎓", "stats": "Siła 13 · Zr 15 · HP 120 · En 100", "desc": "Technik. Zbalansowany, wysoka Zręczność i HP."},
        }

        selected = st.radio(
            "Kim jesteś?",
            options=list(cls_info.keys()),
            format_func=lambda c: f"{cls_info[c]['icon']} {c}",
            horizontal=True,
            label_visibility="collapsed",
            key="class_radio"
        )

        if selected:
            info = cls_info[selected]
            comment = CLASS_COMMENTS[selected]
            enter = CLASS_ENTER[selected]
            _scene(
                f'<span class="dialogue">– ...{comment}</span><br>'
                f'<span class="scene-pause"></span>'
                f'{enter}<br>'
                f'<span class="scene-pause"></span>'
                f'<span style="color:#888;font-size:0.8rem">{info["stats"]}</span>'
            )

        if st.button("Wejdź na ring →", key="intro_7", type="primary"):
            cls_map = {"Powerhouse": Powerhouse, "HighFlyer": HighFlyer, "Technician": Technician}
            player = cls_map[selected](name)
            # Bonus startowy za wybór odpowiedzi o strachu
            fear = st.session_state.intro_fear_choice
            # (reputacja – można tu dodać w przyszłości)
            st.session_state.player = player
            st.session_state.selected_class = selected
            next_intro()

    # ── KROK 8: Wybór ruchów ──────────────────────────────────────────────────
    elif step == 8:
        player: Wrestler = st.session_state.player
        _scene(
            'Kaz prowadzi cię na matę i pokazuje podstawowe ruchy.<br>'
            '<span class="scene-pause"></span>'
            '<span class="dialogue">– Każdy zawodnik ma swój styl.</span><br>'
            '<span class="dialogue">– Trzy ruchy które robi lepiej niż cokolwiek innego.</span><br>'
            '<span class="dialogue">– I jeden koronny – którego rywal się boi.</span><br>'
            '<span class="scene-pause"></span>'
            '<span class="dialogue">– Zły zawodnik ma dziesięć i nie umie żadnego.</span>'
        )

        moves = MOVES_CATALOGUE[player.character_class]
        finishers = FINISHER_CATALOGUE[player.character_class]

        move_options = {
            f"{m.name}  ({m.energy_cost}⚡ · ×{m.damage_multiplier})": m
            for m in moves
        }
        selected_labels = st.multiselect(
            "Wybierz 3 ruchy:",
            options=list(move_options.keys()),
            max_selections=3,
            key="move_multiselect"
        )

        st.markdown("**Koronny cios (finisher):**")
        fin_options = {
            f"{f.name}  ({f.energy_cost}⚡ · ×{f.damage_multiplier})": f
            for f in finishers
        }
        selected_fin = st.radio(
            "Finisher",
            options=list(fin_options.keys()),
            label_visibility="collapsed",
            key="fin_radio"
        )

        if st.button("Zaczynam trening! →", key="intro_8", type="primary",
                     disabled=len(selected_labels) != 3):
            player.set_moves(
                [move_options[l] for l in selected_labels],
                fin_options[selected_fin]
            )
            log(f"💪 Ruchy: {', '.join(m.name for m in player.moves)}")
            log(f"💥 Koronny cios: {player.finisher.name}")
            next_intro()

    # ── KROK 9: Prezent od Kaza ───────────────────────────────────────────────
    elif step == 9:
        player: Wrestler = st.session_state.player
        _scene(
            'Po treningu.<br>'
            'Siedzisz na podłodze przy ringu. Oddychasz ciężko.<br>'
            'Kaz podchodzi. Rzuca przed tobą starą torbę.<br>'
            '<span class="scene-pause"></span>'
            '<span class="dialogue">– Masz.</span><br>'
            '<span class="scene-pause"></span>'
            'Patrzysz na niego.<br>'
            '<span class="scene-pause"></span>'
            '<span class="dialogue">– Nie pytaj skąd. Poprzedni właściciel już tego nie potrzebuje.</span><br>'
            '<span class="dialogue">– Wybierz jedno. Reszta nie dla ciebie.</span><br>'
            '<span class="scene-pause"></span>'
            'Prawie odchodzi. Zatrzymuje się.<br>'
            '<span class="scene-pause"></span>'
            '<span class="dialogue">– I... dziękuję. Za wczoraj.</span><br>'
            '<span class="scene-pause"></span>'
            '<i>Odchodzi zanim zdążysz odpowiedzieć.<br>'
            'Pierwszy i ostatni raz słyszysz to słowo od Kaza.</i>'
        )

        st.markdown("**Wybierz przedmiot startowy:**")
        cols = st.columns(3)
        for i, item in enumerate(STARTER_ITEMS):
            with cols[i]:
                st.markdown(
                    f'<div class="stat-box"><b>{item.name}</b><br>'
                    f'<span style="color:#aaa;font-size:0.8rem">{item.description}</span><br>'
                    f'<span class="stat-label">{repr(item.bonuses)}</span></div>',
                    unsafe_allow_html=True
                )
                if st.button("Weź to", key=f"starter_{i}", type="primary",
                             use_container_width=True):
                    player.add_to_inventory(item)
                    player.equip(item)
                    player.restore_to_full()
                    log(f"🎁 Kaz wręczył: {item.name}")
                    next_intro()

    # ── KROK 10: Finale intro ─────────────────────────────────────────────────
    elif step == 10:
        player: Wrestler = st.session_state.player
        _scene(
            'Wkładasz przedmiot do torby.<br>'
            'Patrzysz na ring.<br>'
            'Na stare zdjęcie na ścianie.<br>'
            'Na młodego Kaza z pasem.<br>'
            '<span class="scene-pause"></span>'
            'Gdzieś w środku coś klika.<br>'
            '<span class="scene-pause"></span>'
            '<b>Chcesz tam być.</b><br>'
            '<b>Na tym zdjęciu.</b><br>'
            '<b>Z tym pasem.</b><br>'
            '<span class="scene-pause"></span>'
            '<i>Nie wiesz jeszcze ile cię to będzie kosztować.</i>'
        )

        st.markdown(
            '<div style="text-align:center;margin:1.5rem 0;">'
            '<span style="font-family:Bebas Neue,sans-serif;font-size:1.8rem;'
            'color:#e94560;letter-spacing:4px;">ROZDZIAŁ I</span><br>'
            '<span style="color:#666;font-size:0.8rem;letter-spacing:3px;'
            'text-transform:uppercase;">Żelazna Piwnica</span>'
            '</div>',
            unsafe_allow_html=True
        )

        if _centered_btn("Zaczynam! →", "intro_10"):
            log(f"📍 Radom. Żelazna Piwnica. Dzień pierwszy.")
            log(f"🎉 {player.name} [{player.character_class}] wchodzi do gry!")
            st.session_state.phase = "game"
            st.rerun()

    else:
        # Failsafe
        st.session_state.phase = "game"
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# LEFT PANEL
# ══════════════════════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════════════════════
# MOBILE-FIRST LAYOUT HELPERS
# ══════════════════════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════════════════
# UI HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _full_bar(current: int, maximum: int, color: str, label: str) -> str:
    """Pasek statystyki: etykieta | pasek | liczby."""
    pct = int((current / maximum) * 100) if maximum > 0 else 0
    return (
        f'<div style="display:flex;align-items:center;gap:6px;margin:3px 0;">'
        f'<span style="color:#888;font-size:0.72rem;width:24px;flex-shrink:0;">{label}</span>'
        f'<div style="flex:1;background:#2a2a3a;border-radius:4px;height:10px;">'
        f'<div style="width:{pct}%;background:{color};border-radius:4px;height:10px;"></div>'
        f'</div>'
        f'<span style="color:#aaa;font-size:0.72rem;min-width:58px;text-align:right;">'
        f'{current} / {maximum}</span>'
        f'</div>'
    )

def _mini_bar(current: int, maximum: int, color: str, label: str) -> str:
    """Mini pasek do ekranu walki."""
    pct = int((current / maximum) * 100) if maximum > 0 else 0
    return (
        f'<div style="display:flex;align-items:center;gap:4px;margin:2px 0;">'
        f'<span style="color:#888;font-size:0.65rem;width:22px;flex-shrink:0;">{label}</span>'
        f'<div style="flex:1;background:#2a2a3a;border-radius:3px;height:8px;">'
        f'<div style="width:{pct}%;background:{color};border-radius:3px;height:8px;"></div>'
        f'</div>'
        f'<span style="color:#aaa;font-size:0.65rem;min-width:55px;text-align:right;">'
        f'{current}/{maximum}</span>'
        f'</div>'
    )

def _last_event_bar() -> None:
    """Pasek ostatniego ważnego wydarzenia."""
    ev = st.session_state.get("last_event", "")
    if ev:
        st.markdown(
            f'<div style="background:#1a1200;border:1px solid #f39c12;border-radius:8px;'
            f'padding:7px 12px;margin:5px 0;display:flex;align-items:center;gap:8px;">'
            f'<span style="font-size:1rem;">📢</span>'
            f'<span style="color:#f39c12;font-size:0.8rem;font-weight:600;">{ev}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

def _section_label(text: str) -> None:
    st.markdown(
        f'<div style="color:#888;font-size:0.65rem;font-weight:700;letter-spacing:1.5px;'
        f'text-transform:uppercase;margin:8px 0 4px 0;">{text}</div>',
        unsafe_allow_html=True,
    )

# ══════════════════════════════════════════════════════════════════════════════
# GŁÓWNY HUD – wg mockupu
# ══════════════════════════════════════════════════════════════════════════════

def render_hud(player: "Wrestler", day: int = 0, show_equip_btn: bool = True) -> None:
    """HUD wg mockupu: nagłówek, karta postaci, ruchy."""
    from game.characters import XP_THRESHOLDS
    from game.assets import LOGO_CREATOR_B64

    chapter = st.session_state.chapter
    chapter_label = "Rozdział I" if chapter == 1 else "Rozdział II"
    location = "Żelazna Piwnica" if chapter == 1 else "Radom Wrestling League"
    federation = "Żelazna Piwnica – Szkoła Wrestlingu" if chapter == 1 else "Radom Wrestling League"
    wins = st.session_state.school_wins if chapter == 1 else st.session_state.federation_wins
    wins_max = "/5" if chapter == 1 else ""

    xp_needed = XP_THRESHOLDS[player.level] if player.level < len(XP_THRESHOLDS) else player.xp or 1

    champ = player.equipped.get("championship")
    champ_name = champ.name if champ else "Brak"
    champ_color = "#f39c12" if champ else "#555"

    passive = player.passive_skill

    # ── NAGŁÓWEK: Rozdział | Lokacja ─────────────────────────────────────────
    st.markdown(
        f'''<div style="display:flex;align-items:center;justify-content:space-between;
                       padding:8px 0 8px 0;border-bottom:1px solid #2a2a3e;margin-bottom:8px;">
            <div style="display:flex;align-items:baseline;gap:10px;">
                <span style="color:#e94560;font-size:0.68rem;font-weight:700;
                             letter-spacing:1px;text-transform:uppercase;">{chapter_label}</span>
                <span style="font-family:Bebas Neue,sans-serif;font-size:1.7rem;
                             color:#fff;letter-spacing:2px;">{location.upper()}</span>
            </div>
            <img src="data:image/png;base64,{LOGO_CREATOR_B64}"
                 style="height:40px;width:auto;opacity:0.85;" alt="DKG"/>
        </div>''',
        unsafe_allow_html=True,
    )

    # ── KARTA POSTACI ─────────────────────────────────────────────────────────
    _section_label("Karta postaci")

    # Wiersz 1: Imię + LVL badge + DZIEŃ X
    day_html = (
        f'<span style="font-family:Bebas Neue,sans-serif;font-size:1.5rem;'
        f'color:#fff;letter-spacing:1px;">DZIEŃ {day}</span>'
    ) if day > 0 else ""

    st.markdown(
        f'<div style="background:#12121f;border:1px solid #2a2a3e;border-radius:10px;'
        f'padding:12px 14px;margin-bottom:6px;">'

        # Wiersz 1: Imię + LVL + Dzień
        f'<div style="display:flex;align-items:center;justify-content:space-between;'
        f'margin-bottom:6px;">'
        f'<div style="display:flex;align-items:center;gap:8px;">'
        f'<span style="font-family:Bebas Neue,sans-serif;font-size:1.2rem;color:#fff;">'
        f'{player.name.upper()} [{player.character_class}]</span>'
        f'<span style="background:#2a2a3e;border:1px solid #e94560;border-radius:6px;'
        f'padding:1px 8px;font-size:0.72rem;color:#e94560;font-weight:700;">'
        f'LVL {player.level}</span>'
        f'</div>'
        f'{day_html}'
        f'</div>'

        # Wiersz 2: Federacja + Pas
        f'<div style="font-size:0.7rem;color:#666;margin-bottom:8px;">'
        f'Federacja: <span style="color:#888;">{federation}</span>'
        f' · Pas: <span style="color:{champ_color};">{champ_name}</span>'
        f'</div>'

        # Paski + statystyki obok
        f'<div style="display:flex;gap:10px;align-items:flex-start;">'

        # Lewa: paski XP/HP/En
        f'<div style="flex:1;min-width:0;">'
        + _full_bar(player.xp, xp_needed, "#9b59b6", "XP")
        + _full_bar(player.current_hp, player.max_hp, "#e94560", "HP")
        + _full_bar(player.current_energy, player.max_energy, "#4ecdc4", "En")
        + f'</div>'

        # Prawa: Wygrane + Siła + Zręczność
        f'<div style="flex-shrink:0;text-align:right;font-size:0.75rem;line-height:1.8;">'
        f'<div style="color:#f39c12;">🏆 Wygrane: {wins}{wins_max}</div>'
        f'<div style="color:#ddd;">💪 Siła: <b>{player.effective_strength}</b></div>'
        f'<div style="color:#ddd;">🏃 Zręczność: <b>{player.effective_dexterity}</b></div>'
        f'</div>'
        f'</div>'  # koniec flex pasków
        f'</div>',  # koniec karty
        unsafe_allow_html=True,
    )

    # ── RUCHY I UMIEJĘTNOŚCI ──────────────────────────────────────────────────
    _section_label("Ruchy i Umiejętności")

    fin = player.finisher
    moves = player.moves

    # 3 ruchy w górnym rzędzie – bez ikon, tylko tekst
    move_cells = ""
    for m in moves[:3]:
        move_cells += (
            f'<div style="background:#1a1a2e;border:1px solid #2a2a3e;border-radius:8px;'
            f'padding:8px 6px;text-align:center;">'
            f'<div style="font-size:0.8rem;color:#ddd;font-weight:600;">{m.name}</div>'
            f'<div style="font-size:0.67rem;color:#888;margin-top:2px;">'
            f'{m.energy_cost}⚡ ×{m.damage_multiplier}</div>'
            f'</div>'
        )

    # Finisher + Pasywna w dolnym rzędzie
    fin_cell = ""
    if fin:
        fin_cell = (
            f'<div style="background:#1a0e00;border:1px solid #f39c12;border-radius:8px;'
            f'padding:8px 12px;">'
            f'<div style="font-size:0.85rem;color:#f39c12;font-weight:700;">{fin.name}</div>'
            f'<div style="font-size:0.67rem;color:#888;margin-top:2px;">'
            f'{fin.energy_cost} 💥×{fin.damage_multiplier} '
            f'<span style="background:#2a1800;color:#f39c12;padding:1px 5px;'
            f'border-radius:4px;font-size:0.6rem;font-weight:700;">Koronny</span>'
            f'</div>'
            f'</div>'
        )

    passive_cell = (
        f'<div style="background:#001a18;border:1px solid #4ecdc4;border-radius:8px;'
        f'padding:8px 12px;">'
        f'<div style="font-size:0.85rem;color:#4ecdc4;font-weight:700;">{passive.name}</div>'
        f'<div style="font-size:0.67rem;color:#888;margin-top:2px;">'
        f'Pasywna · {passive.description[:35]}{"…" if len(passive.description)>35 else ""}'
        f'</div>'
        f'</div>'
    )

    st.markdown(
        f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:5px;margin-bottom:5px;">'
        f'{move_cells}</div>'
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:5px;margin-bottom:8px;">'
        f'{fin_cell}{passive_cell}</div>',
        unsafe_allow_html=True,
    )

    # ── EKWIPUNEK (jeden szeroki przycisk) ────────────────────────────────────
    if show_equip_btn:
        if st.button("🎽  Ekwipunek", key="open_equip", use_container_width=True):
            st.session_state.show_equip = not st.session_state.get("show_equip", False)
            st.rerun()

        if st.session_state.get("show_equip", False):
            _render_equip_panel(player)

    # ── OSTATNIE WYDARZENIE ───────────────────────────────────────────────────
    _last_event_bar()


def _render_equip_panel(player: "Wrestler") -> None:
    """Rozwijany panel ekwipunku."""
    slots = {
        "outfit":       ("👕", "Strój"),
        "gadget":       ("🧤", "Gadżet"),
        "protector":    ("🦺", "Ochraniacz"),
        "championship": ("🏆", "Pas Mistrzowski"),
    }
    rows = ""
    for slot, (icon, label) in slots.items():
        item = player.equipped.get(slot)
        name = item.name if item else "— brak —"
        bonus = f"  {repr(item.bonuses)}" if item else ""
        color = "#ddd" if item else "#444"
        rows += (
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'padding:5px 0;border-bottom:1px solid #1a1a2e;">'
            f'<span style="font-size:0.75rem;color:#888;">{icon} {label}</span>'
            f'<span style="font-size:0.75rem;color:{color};">{name}{bonus}</span>'
            f'</div>'
        )
    st.markdown(
        f'<div style="background:#0f0f1a;border:1px solid #2a2a3e;border-radius:8px;'
        f'padding:10px 12px;margin:4px 0;">{rows}</div>',
        unsafe_allow_html=True,
    )
    inv = player.inventory
    if inv:
        with st.expander(f"🎒 Torba ({len(inv)} przedmiotów)"):
            for idx, item in enumerate(inv):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.caption(f"**{item.name}** · {repr(item.bonuses)} · Lvl {item.required_level}+")
                with c2:
                    if st.button("Załóż", key=f"equip_{idx}_{item.name}"):
                        try:
                            log(player.equip(item))
                            st.rerun()
                        except ItemRequirementError as e:
                            st.error(str(e))
    else:
        st.caption("Torba pusta – idź na spacer!")


def render_journal() -> None:
    """Log wydarzeń – scrollowalny."""
    _section_label("Log Wydarzeń")
    entries = st.session_state.journal[:60]
    html = "<br>".join(f"<span>{e}</span>" for e in entries)
    st.markdown(
        f'<div style="background:#0a0a14;border:1px solid #1a1a2e;border-radius:8px;'
        f'padding:10px 14px;height:200px;overflow-y:auto;'
        f'font-size:0.8rem;color:#bbb;line-height:1.8;">{html}</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# PHASE: GAME
# ══════════════════════════════════════════════════════════════════════════════

def phase_game() -> None:
    player: Wrestler = st.session_state.player
    day = st.session_state.day

    render_hud(player, day=day)

    # Chapter transition
    declined_day = st.session_state.get("chapter2_declined_day", -99)
    recently_declined = (st.session_state.day - declined_day) < 7
    if (
        not st.session_state.offered_chapter2
        and st.session_state.chapter == 1
        and st.session_state.school_wins >= 5
        and player.level >= 3
        and not recently_declined
    ):
        _lore(
            "Kaz siada na krawędzi ringu. Pierwszy raz nie stoi.<br>"
            "<b>– Nauczyłem cię wszystkiego co mogę. Jest federacja w Radomiu. Chcesz?</b>"
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Dołącz do RWL!", type="primary", use_container_width=True):
                st.session_state.chapter = 2
                st.session_state.offered_chapter2 = True
                log("🏟️ Rozdział II – Radom Wrestling League!")
                st.rerun()
        with c2:
            if st.button("❌ Zostań w szkole", use_container_width=True):
                st.session_state.chapter2_declined_day = st.session_state.day
                st.rerun()
        render_journal()
        return

    # Dzień walki
    if day % 7 == 0:
        if st.session_state.get("fight_day_npc_day") != day:
            npc_preview = pick_npc_for_fight()
            st.session_state.fight_day_npc = npc_preview
            st.session_state.fight_day_npc_day = day
        else:
            npc_preview = st.session_state.fight_day_npc

        st.markdown(
            f'<div style="background:#1a0808;border:1px solid #e94560;border-radius:10px;'
            f'padding:12px 14px;margin:8px 0;text-align:center;">'
            f'<div style="font-family:Bebas Neue,sans-serif;font-size:1.3rem;color:#e94560;">'
            f'🥊 DZIEŃ WALKI</div>'
            f'<div style="font-size:0.8rem;color:#aaa;margin-top:4px;">'
            f'Rywal: <b style="color:#fff;">{npc_preview.name}</b>'
            f' · Lvl {npc_preview.level}'
            f' · HP {npc_preview.max_hp}'
            f' · Siła {npc_preview.effective_strength}'
            f'</div></div>',
            unsafe_allow_html=True,
        )
        lore_text = NPC_LORE.get(npc_preview.name)
        if lore_text:
            _lore(lore_text)
        if st.button("🥊  WEJDŹ NA RING!", type="primary", use_container_width=True):
            st.session_state.current_npc = npc_preview
            st.session_state.battle_log = [
                f"🎺 {player.name} vs {npc_preview.name} [Lvl {npc_preview.level}]",
                f"Rywal: HP {npc_preview.current_hp} | Siła {npc_preview.effective_strength} | En {npc_preview.current_energy}",
            ]
            st.session_state.battle_over = False
            st.session_state.battle_won = None
            st.session_state.npc_adrenaline_streak = 0
            npc_preview.restore_to_full()
            st.session_state.phase = "battle"
            st.rerun()
    else:
        # Akcje dnia
        st.markdown(
            f'<div style="font-size:0.85rem;color:#aaa;margin:6px 0 4px 0;">'
            f'Co robisz dzisiaj?</div>',
            unsafe_allow_html=True,
        )
        btn_train = st.button(
            "🏋️  Trening (+40XP -25HP)",
            key="btn_train", use_container_width=True, type="primary"
        )
        btn_walk = st.button(
            "🚶  Spacer – Szukanie przedmiotów  -5 En",
            key="btn_walk", use_container_width=True
        )
        btn_regen = st.button(
            "😴  Odpoczynek (+30HP +10En)",
            key="btn_regen", use_container_width=True
        )

        if btn_train:
            for m in player.train(): log(m)
            st.session_state.train_count += 1
            if st.session_state.train_count % 2 == 0:
                log(f"💬 {random.choice(TRENER_QUOTES)}")
            st.session_state.day += 1
            st.rerun()
        elif btn_walk:
            msgs, _ = player.walk()
            for m in msgs: log(m)
            player.spend_energy(min(5, player.current_energy))
            log("🚶 Spacer: −5 Energii")
            st.session_state.day += 1
            st.rerun()
        elif btn_regen:
            for m in player.regenerate(): log(m)
            st.session_state.day += 1
            st.rerun()

    render_journal()


# ══════════════════════════════════════════════════════════════════════════════
# PHASE: BATTLE
# ══════════════════════════════════════════════════════════════════════════════

def phase_battle() -> None:
    player: Wrestler = st.session_state.player
    npc: Wrestler = st.session_state.current_npc

    # HUD gracza (bez dnia i bez ekwipunku)
    render_hud(player, day=0, show_equip_btn=False)

    # Status walki
    _section_label("Status walki")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f'<div style="background:#12121f;border:1px solid #e94560;border-radius:8px;'
            f'padding:8px 10px;">'
            f'<div style="font-size:0.75rem;font-weight:700;color:#fff;margin-bottom:4px;">'
            f'🤼 {player.name}</div>'
            + _mini_bar(player.current_hp, player.max_hp, "#e94560", "HP")
            + _mini_bar(player.current_energy, player.max_energy, "#4ecdc4", "En")
            + '</div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<div style="background:#12121f;border:1px solid #f39c12;border-radius:8px;'
            f'padding:8px 10px;">'
            f'<div style="font-size:0.75rem;font-weight:700;color:#f39c12;margin-bottom:4px;">'
            f'⚔️ {npc.name} Lvl{npc.level}</div>'
            + _mini_bar(npc.current_hp, npc.max_hp, "#f39c12", "HP")
            + _mini_bar(npc.current_energy, npc.max_energy, "#9b59b6", "En")
            + '</div>',
            unsafe_allow_html=True,
        )

    _last_event_bar()

    # Log walki
    if st.session_state.battle_log:
        battle_html = "<br>".join(st.session_state.battle_log[-12:])
        st.markdown(
            f'<div style="background:#0a0a14;border:1px solid #1a1a2e;border-radius:8px;'
            f'padding:8px 12px;height:110px;overflow-y:auto;'
            f'font-size:0.78rem;color:#bbb;line-height:1.6;margin:6px 0;">'
            f'{battle_html}</div>',
            unsafe_allow_html=True,
        )

    # Koniec walki
    if st.session_state.battle_over:
        if st.session_state.battle_won:
            st.success("🏆 Wygrałeś!")
        else:
            st.error("💀 Przegrałeś...")
        if st.button("Kontynuuj →", type="primary", use_container_width=True):
            st.session_state.day += 1
            st.session_state.phase = "game"
            st.session_state.show_equip = False
            st.rerun()
        render_journal()
        return

    # Akcje walki
    _section_label("Twoja akcja")
    move_cols = st.columns(len(player.moves))
    for i, move in enumerate(player.moves):
        with move_cols[i]:
            disabled = player.current_energy < move.energy_cost
            if st.button(
                f"{move.name}\n{move.energy_cost}⚡",
                key=f"move_{i}",
                disabled=disabled,
                use_container_width=True,
            ):
                _execute_player_turn(move, player, npc)
                st.rerun()

    fin = player.finisher
    col_fin, col_adr = st.columns(2)
    with col_fin:
        if fin:
            fin_ok = npc.hp_percentage < 35 and player.current_energy >= fin.energy_cost
            if st.button(
                f"💥 {fin.name}\n{fin.energy_cost}⚡  {'✅' if fin_ok else '🔒<35%HP'}",
                disabled=not fin_ok,
                type="primary" if fin_ok else "secondary",
                use_container_width=True,
                key="btn_fin",
            ):
                _execute_player_turn(fin, player, npc)
                st.rerun()
    with col_adr:
        if st.button(
            "⚡ ADRENALINA\n+30HP +25En",
            key="adrenaline",
            use_container_width=True,
        ):
            blog(player.adrenaline_rush())
            _npc_turn(npc, player)
            st.rerun()

    render_journal()


def _execute_player_turn(move, player: Wrestler, npc: Wrestler) -> None:
    try:
        blog(move.apply(player, npc))
    except InsufficientEnergyError as e:
        blog(f"❌ {e}"); return
    except FinisherNotAvailableError as e:
        blog(f"❌ {e}"); return
    if not npc.is_alive:
        _resolve_battle(won=True, player=player, npc=npc)
        return
    _npc_turn(npc, player)


def _npc_turn(npc: Wrestler, player: Wrestler) -> None:
    affordable = [m for m in npc.moves if npc.current_energy >= m.energy_cost]

    # Adrenalina TYLKO gdy: brak ruchów na stanie LUB bardzo mało HP i energii
    # Ale NIE częściej niż co 2 tury – żeby nie zapętlić się w adrenalinie
    npc_adrenaline_count = st.session_state.get("npc_adrenaline_streak", 0)

    should_adrenaline = (
        not affordable
        or (npc.hp_percentage < 20 and npc.current_energy < 15)
    )
    # Jeśli użył adrenaliny 2 razy z rzędu – wymuś atak nawet najtańszym ruchem
    if npc_adrenaline_count >= 2:
        should_adrenaline = False

    if should_adrenaline:
        npc.heal(30)
        npc.restore_energy(20)  # więcej energii żeby mógł zaatakować w następnej turze
        st.session_state.npc_adrenaline_streak = npc_adrenaline_count + 1
        blog(f"[{npc.name}] ⚡ Adrenalina! +30 HP, +20 En ({npc.current_hp}/{npc.max_hp} HP)")
        return

    # Reset streak gdy atakuje
    st.session_state.npc_adrenaline_streak = 0

    # Jeśli nadal nie ma affordowalnych po resecie – użyj najtańszego ruchu za darmo (panic move)
    if not affordable:
        cheapest = min(npc.moves, key=lambda m: m.energy_cost)
        npc._current_energy = cheapest.energy_cost  # daj dokładnie tyle energii
        affordable = [cheapest]

    try:
        blog(f"[{npc.name}] {npc_choose_move(npc, player).apply(npc, player)}")
    except (InsufficientEnergyError, FinisherNotAvailableError):
        # Ostatnia deska – słaby cios
        cheapest = min(npc.moves, key=lambda m: m.energy_cost)
        npc._current_energy = cheapest.energy_cost
        try:
            blog(f"[{npc.name}] {cheapest.apply(npc, player)}")
        except Exception:
            blog(f"[{npc.name}] walczy z ostatnich sił...")

    if not player.is_alive:
        _resolve_battle(won=False, player=player, npc=npc)


def _resolve_battle(won: bool, player: Wrestler, npc: Wrestler) -> None:
    st.session_state.battle_over = True
    st.session_state.battle_won = won

    if won:
        xp_reward = 70 + npc.level * 15
        for m in player.gain_xp(xp_reward):
            blog(m); log(m)

        if st.session_state.chapter == 1:
            st.session_state.school_wins += 1
            wins = st.session_state.school_wins
            log(f"🏫 Wygrane w szkole: {wins}/5")
            story = AFTER_WIN_SCHOOL.get(wins)
            if story:
                _story_log(story)
        else:
            st.session_state.federation_wins += 1
            wins = st.session_state.federation_wins
            log(f"🏟️ Wygrane w federacji: {wins}")
            story = AFTER_WIN_FED.get(wins)
            if story:
                _story_log(story)

        champ_eq = player.equipped.get("championship")
        if st.session_state.chapter == 2:
            if champ_eq is None and st.session_state.federation_wins >= 3:
                champ = CHAMPIONSHIPS[0]
                player.award_championship(champ)
                _story_log(CHAMPIONSHIP_STORY.get(champ.name, f"Zdobyłeś {champ.name}!"))
                blog(f"🏆 {player.name} zdobywa {champ.name}!")
            elif (
                champ_eq and champ_eq.name == CHAMPIONSHIPS[0].name
                and st.session_state.federation_wins >= 7
            ):
                champ = CHAMPIONSHIPS[1]
                player.award_championship(champ)
                _story_log(CHAMPIONSHIP_STORY.get(champ.name, f"Zdobyłeś {champ.name}!"))
                blog(f"🏆 {player.name} zdobywa {champ.name}!")

        blog(f"✅ +{xp_reward} XP")
        log(f"🥊 Wygrałeś z {npc.name}! (+{xp_reward} XP)")
    else:
        log(f"💀 Przegrałeś z {npc.name}...")
        log("💬 Kaz: <i>– Bolało? Dobrze. Zapamiętasz.</i>")
        player.restore_to_full()


def _story_log(text: str) -> None:
    """Add story text to journal (stripped of HTML for readability)."""
    import re
    clean = re.sub(r'<[^>]+>', '', text).strip()
    log(f"📖 {clean}")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN ROUTER
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    phase = st.session_state.phase
    if   phase == "splash":  phase_splash()
    elif phase == "intro":   phase_intro()
    elif phase == "game":    phase_game()
    elif phase == "battle":  phase_battle()
    else:
        st.session_state.phase = "splash"
        st.rerun()

if __name__ == "__main__":
    main()
