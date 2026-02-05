import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json
import math

# Nastavení přístupového rozsahu pro Google Sheets API
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Získání informací o službě z tajných dat ve Streamlitu
service_account_info = dict(st.secrets["gcp_service_account"])

# Vytvoření přihlašovacích údajů pomocí Google Credentials z knihovny google-auth
credentials = Credentials.from_service_account_info(service_account_info, scopes=scope)

# Autorizace klienta knihovnou gspread
client = gspread.authorize(credentials)

# Otevření listu podle klíče - VAŠE ID
sheet = client.open_by_key("1mbeCadh9vQd62BKvLWpBYr67BXMa6UMQW5OjGzl_eHE")

# Výběr worksheetu - změňte "Sheet1" na název vašeho listu
worksheet = sheet.worksheet("výsledky")

# Načtení dat
data = worksheet.get_all_records()

# Převod dat do Pandas DataFrame
df = pd.DataFrame(data)
# Načtení dat
data = worksheet.get_all_records()

# Převod dat do Pandas DataFrame
df = pd.DataFrame(data)

# Odstraní první sloupec, pokud vypadá jako index
first_col = df.columns[0]
if first_col == '' or 'Unnamed' in first_col or df[first_col].apply(lambda x: isinstance(x, int)).all():
    df = df.drop(columns=[first_col])



# Čištění a typy dat
df['Datum'] = pd.to_datetime(df['Datum'], errors='coerce')
df['Pořadí'] = pd.to_numeric(df['Pořadí'], errors='coerce')
df['Skóre'] = (
    df['Skóre']
    .astype(str)
    .str.replace(r"[^\d.]", "", regex=True) # Odstraní vše kromě číslic a tečky
    .replace("", None) # Prázdné řetězce nahradí None
    .astype(float)
)


# Kompletní styl pro Streamlit aplikaci s černým textem
st.markdown("""
<style>
    /* Hlavní aplikace - světle šedé pozadí pro všechny */
    .stApp {
        background-color: #e0e0e0 !important;
        color: black !important;
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* Hlavní obsah */
    .main .block-container {
        background-color: #e0e0e0 !important;
        color: black !important;
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background-color: #d8d8d8 !important;
        color: black !important;
    }
    
    /* Obecné styly pro tělo */
    body {
        background-color: #e0e0e0;
        color: black;
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* VŠECHEN TEXT V APLIKACI - ČERNÝ */
    .stMarkdown, .stText, .stWrite,
    .element-container p, .element-container div,
    .stMarkdown p, .stMarkdown div,
    .stSubheader, h1, h2, h3, h4, h5, h6 {
        color: black !important;
    }
    
    /* Metriky - černý text */
    .metric-container, .metric-container .metric-value,
    .metric-container .metric-label, .metric-container .metric-delta {
        color: black !important;
    }
    
    /* Selectbox label - černý text */
    .stSelectbox label, .stSelectbox > label {
        color: black !important;
    }
    
    /* Styly pro HTML tabulky */
    table {
        background-color: #f8f9fa;
        border-collapse: collapse;
        width: auto;
        max-width: 100%;
        border-radius: 10px;
        overflow-x: auto;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
    
    /* Zakáže zalamování textu ve všech buňkách a hlavičkách */
    td, th {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        vertical-align: middle;
    }
    
    /* Styly pro buňky */
    td {
        padding: 10px;
        color: #000000;
        text-align: center;
        font-size: 0.95em;
    }
    
    /* Styly pro hlavičky */
    th {
        background-color: #e9ecef;
        color: #007bff;
        padding: 10px;
        text-align: center;
        font-size: 1em;
    }
    
    /* Speciální styly pro konkrétní sloupce */
    .dataframe th:nth-child(9),
    .dataframe th:nth-child(10),
    .dataframe th:nth-child(11) {
        background-color: #dee2e6 !important;
    }
    
    /* Streamlit dataframe styly */
    .stDataFrame {
        background-color: #f8f9fa;
    }
    
    /* Input fieldy */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #ffffff;
        color: black;
        border-color: #ced4da;
    }
    
    /* Selectboxy - kompletní přepsání */
    .stSelectbox > div > div > select {
        background-color: #ffffff !important;
        color: black !important;
        border-color: #ced4da !important;
    }
    
    /* Selectbox dropdown options */
    .stSelectbox option {
        background-color: #ffffff !important;
        color: black !important;
    }
    
    /* Selectbox při hover */
    .stSelectbox > div > div > select:hover {
        background-color: #f8f9fa !important;
        border-color: #adb5bd !important;
    }
    
    /* Selectbox při focus */
    .stSelectbox > div > div > select:focus {
        background-color: #ffffff !important;
        color: black !important;
        border-color: #007bff !important;
        box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25) !important;
    }
    
    /* Tlačítka */
    .stButton > button {
        background-color: #ffffff;
        color: black;
        border-color: #ced4da;
    }
    
    .stButton > button:hover {
        background-color: #f8f9fa;
        border-color: #adb5bd;
    }

    
    /* Info boxy */
    .stInfo {
        color: black !important;
    }
    
    /* Divs s inline styly */
    div[style*="font-size: 1.1rem"] {
        color: black !important;
    }
    
    /* AGRESIVNÍ přepsání selectbox stylů */
    div[data-testid="stSelectbox"] > div > div > select,
    div[data-testid="stSelectbox"] select,
    .stSelectbox select,
    select {
        background-color: white !important;
        color: black !important;
        border: 1px solid #ced4da !important;
        -webkit-appearance: none !important;
        -moz-appearance: none !important;
        appearance: none !important;
    }
    
    /* Dropdown options */
    div[data-testid="stSelectbox"] option,
    .stSelectbox option,
    select option {
        background-color: white !important;
        color: black !important;
    }
    
    /* Řádky tabulky s černým textem */
    tr {
        color: black !important;
    }
    
    tr:hover {
        background-color: #e9ecef !important;
    }
    
    /* NAVIGAČNÍ LIŠTA (TABS) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        background-color: #f8f9fa;
        border-radius: 10px 10px 0 0;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #ffffff;
        border-radius: 5px 5px 0 0;
        color: black;
        font-size: 16px;
        font-weight: 500;
        padding: 10px 24px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #007bff !important;
        color: white !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e9ecef;
    }
    
    .stTabs [aria-selected="true"]:hover {
        background-color: #0056b3 !important;
    }
</style>
""", unsafe_allow_html=True)

# Inicializace slovníku pro mapování jmen hráčů na obrázky
player_images = {
    "pstross": "https://cdn.royaleapi.com/static/img/ui/ic_crown.png",
    "jirigulas": "https://cdn.royaleapi.com/static/img/ui/ic_trophy.png",
    "fanda": "https://cdn.royaleapi.com/static/img/ui/ic_clan_badge.png",
    "jakubdanecek": "https://cdn.royaleapi.com/static/img/ui/ic_gold_rush.png",
    "dawe": "https://cdn.royaleapi.com/static/img/ui/ic_star_level.png",
    "maty": "https://cdn.royaleapi.com/static/img/ui/ic_cards_locked.png",
    "mates": "https://cdn.royaleapi.com/static/img/ui/ic_chest_legendary.png",
    "kuliskm": "https://cdn.royaleapi.com/static/img/ui/ic_experience.png",
    "davidos": "https://cdn.royaleapi.com/static/img/ui/ic_chest_epic.png",
    "t0ny": "https://cdn.royaleapi.com/static/img/ui/ic_chest_rare.png",
    "czechman": "https://cdn.royaleapi.com/static/img/ui/ic_chest_silver.png",
    "krizsi": "https://cdn.royaleapi.com/static/img/ui/ic_chest_golden.png",
    "ondra_k14": "https://cdn.royaleapi.com/static/img/ui/ic_chest_giant.png",
    "martinh03": "https://cdn.royaleapi.com/static/img/ui/ic_chest_magical.png",
    "adele": "https://cdn.royaleapi.com/static/img/ui/ic_chest_super_magical.png",
    "martinhorvath": "https://cdn.royaleapi.com/static/img/ui/ic_chest_mega_lightning.png",
    "darrien": "https://cdn.royaleapi.com/static/img/ui/ic_chest_legendary_kings.png",
    "pajaman": "https://cdn.royaleapi.com/static/img/ui/ic_chest_wood.png",
    "haris": "https://cdn.royaleapi.com/static/img/ui/ic_lightning_strike.png",
    "daniel": "https://cdn.royaleapi.com/static/img/ui/ic_fireball.png",
    "tadik": "https://cdn.royaleapi.com/static/img/ui/ic_freeze.png",
    "marecek": "https://cdn.royaleapi.com/static/img/ui/ic_rage.png",
    "filip": "https://cdn.royaleapi.com/static/img/ui/ic_mirror.png",
    "nikolas87": "https://cdn.royaleapi.com/static/img/ui/ic_clone.png",
    "barborka": "https://cdn.royaleapi.com/static/img/ui/ic_heal_spirit.png",
    "petr": "https://cdn.royaleapi.com/static/img/ui/ic_elixir.png",
    "rene": "https://cdn.royaleapi.com/static/img/ui/ic_gold.png",
    "denis": "https://cdn.royaleapi.com/static/img/ui/ic_gem.png",
    "dominik": "https://cdn.royaleapi.com/static/img/ui/ic_ticket.png",
    "ales": "https://cdn.royaleapi.com/static/img/ui/ic_tournament.png",
    "honza": "https://cdn.royaleapi.com/static/img/ui/ic_challenge.png",
    "martin": "https://cdn.royaleapi.com/static/img/ui/ic_chest_crown.png",
    "patrik": "https://cdn.royaleapi.com/static/img/ui/ic_chest_fortune.png",
    "tomas": "https://cdn.royaleapi.com/static/img/ui/ic_chest_plentiful.png",
    "venca": "https://cdn.royaleapi.com/static/img/ui/ic_chest_bounty.png",
    "zdenka": "https://cdn.royaleapi.com/static/img/ui/ic_chest_royal_wild.png",
    "zuzana": "https://cdn.royaleapi.com/static/img/ui/ic_chest_season.png",
    "adam": "https://cdn.royaleapi.com/static/img/ui/ic_chest_overflow.png",
    "lukas": "https://cdn.royaleapi.com/static/img/ui/ic_cards_new.png",
    "kaja": "https://cdn.royaleapi.com/static/img/ui/ic_cards_coming.png",
    "pepa": "https://cdn.royaleapi.com/static/img/ui/ic_shop.png",
    "jirka": "https://cdn.royaleapi.com/static/img/ui/ic_battle.png",
    "ivan": "https://cdn.royaleapi.com/static/img/ui/ic_cards_found.png",
    "michal": "https://cdn.royaleapi.com/static/img/ui/ic_clan_war.png",
    "jakub": "https://cdn.royaleapi.com/static/img/ui/ic_clan_games.png",
    "ondra": "https://cdn.royaleapi.com/static/img/ui/ic_friendly_battle.png",
    "david": "https://cdn.royaleapi.com/static/img/ui/ic_2v2.png",
    "marek": "https://cdn.royaleapi.com/static/img/ui/ic_1v1.png",
    "roman": "https://cdn.royaleapi.com/static/img/ui/ic_draft.png",
    "stanislav": "https://cdn.royaleapi.com/static/img/ui/ic_triple_elixir.png",
    "vojta": "https://cdn.royaleapi.com/static/img/ui/ic_sudden_death.png"
}

# Funkce pro získání barvy pozadí podle pořadí (ponecháno pro zpětnou kompatibilitu)
def get_color_by_rank(rank, force_text_color=None):
    try:
        rank = int(rank)
        bg_color = ''
        text_color = 'black'
        if 1 <= rank <= 10:
            bg_color = '#00cc00'
            text_color = 'white'
        elif 11 <= rank <= 30:
            bg_color = '#c6efce'
            text_color = 'black'
        elif 31 <= rank <= 40:
            bg_color = '#ffeb9c'
            text_color = 'black'
        elif 41 <= rank <= 47:
            bg_color = '#f4cccc'
            text_color = 'black'
        elif 48 <= rank <= 50:
            bg_color = '#ff0000'
            text_color = 'white'
        else:
            return ''
        if force_text_color:
            text_color = force_text_color
        return f'background-color: {bg_color}; color: {text_color};'
    except (ValueError, TypeError):
        return ''

# Funkce pro zvýraznění Top 3
def highlight_top3(row):
    celk_posledni = row.get('Celk. pořadí - Posledních 5', None)
    styles = [''] * len(row)
    try:
        rank = int(celk_posledni)
        if rank == 1:
            for i in range(len(row)):
                styles[i] = 'background-color: #FFD700; color: black; font-weight: bold;'
        elif rank == 2:
            for i in range(len(row)):
                styles[i] = 'background-color: #C0C0C0; color: black; font-weight: bold;'
        elif rank == 3:
            for i in range(len(row)):
                styles[i] = 'background-color: #CD7F32; color: black; font-weight: bold;'
    except (ValueError, TypeError):
        pass
    return styles

# Funkce pro barvení buněk podle hodnot
def color_cells(val, column_name):
    if pd.isna(val) or val == '':
        return ''
    if 'pořadí' in column_name.lower() and 'posledních' not in column_name.lower():
        return get_color_by_rank(val)
    return ''

# Funkce pro formátování čísla s mezerami jako oddělovači tisíců
def format_number(val):
    if pd.isna(val):
        return '-'
    return "{:,.0f}".format(val).replace(',', ' ')

# Příprava DataFrame podle specifikace
df_sorted = df.sort_values(by='Datum', ascending=False).reset_index(drop=True)
summary_data = []

for player_name in df['Hráč'].unique():
    player_df = df_sorted[df_sorted['Hráč'] == player_name].copy()
    truhly_data = player_df[player_df['Event'].str.lower() == 'truhla']
    hrady_data = player_df[player_df['Event'].str.lower() == 'hrady/bomby']
    truhly_last5 = truhly_data.head(5)
    hrady_last5 = hrady_data.head(5)
    count_truhly = len(truhly_last5)
    count_hrady = len(hrady_last5)
    is_novacek = count_truhly < 5 or count_hrady < 5
    avg_rank_truhly = truhly_last5['Pořadí'].mean() if count_truhly > 0 else None
    avg_rank_hrady = hrady_last5['Pořadí'].mean() if count_hrady > 0 else None
    avg_score_truhly = truhly_last5['Skóre'].mean() if count_truhly > 0 else None
    avg_score_hrady = hrady_last5['Skóre'].mean() if count_hrady > 0 else None
    if avg_rank_truhly is not None and avg_rank_hrady is not None:
        celk_posledni = (avg_rank_truhly + avg_rank_hrady) / 2
    else:
        celk_posledni = None
    avg_rank_truhly_all = truhly_data['Pořadí'].mean() if len(truhly_data) > 0 else None
    avg_rank_hrady_all = hrady_data['Pořadí'].mean() if len(hrady_data) > 0 else None
    avg_score_truhly_all = truhly_data['Skóre'].mean() if len(truhly_data) > 0 else None
    avg_score_hrady_all = hrady_data['Skóre'].mean() if len(hrady_data) > 0 else None
    if avg_rank_truhly_all is not None and avg_rank_hrady_all is not None:
        celk_all = (avg_rank_truhly_all + avg_rank_hrady_all) / 2
    else:
        celk_all = None
    summary_data.append({
        'Hráč': player_name,
        'Je nováček': is_novacek,
        'Celk. pořadí - Posledních 5': celk_posledni,
        '📦 Truhly - pořadí (posledních 5)': avg_rank_truhly,
        '📦 Truhly - skóre (posledních 5)': avg_score_truhly,
        '🏰 Hrady/Bomby - pořadí (posledních 5)': avg_rank_hrady,
        '🏰 Hrady/Bomby - skóre (posledních 5)': avg_score_hrady,
        'Celk. pořadí (všechny hry)': celk_all,
        '📦 Truhly - pořadí (všechny hry)': avg_rank_truhly_all,
        '📦 Truhly - skóre (všechny hry)': avg_score_truhly_all,
        '🏰 Hrady/Bomby - pořadí (všechny hry)': avg_rank_hrady_all,
        '🏰 Hrady/Bomby - skóre (všechny hry)': avg_score_hrady_all
    })

summary_df = pd.DataFrame(summary_data)
summary_df = summary_df.sort_values(by='Celk. pořadí - Posledních 5', ascending=True, na_position='last').reset_index(drop=True)

# Přidání sloupce "Postavení"
summary_df.insert(0, 'Postavení', range(1, len(summary_df) + 1))

# Úprava sloupce Hráč s obrázkem a nálepkou "NOVÁČEK"
def format_player_column(row):
    player_name = row['Hráč']
    is_novacek = row['Je nováček']
    player_lower = player_name.lower()
    if player_lower in player_images:
        avatar_url = player_images[player_lower]
    else:
        import unicodedata
        normalized = (
            unicodedata.normalize('NFKD', player_name)
            .encode('ascii', 'ignore')
            .decode('utf-8')
            .strip()
            .lower()
        )
        avatar_url = player_images.get(normalized, None)
    if avatar_url:
        img_html = f'<img src="{avatar_url}" width="24" height="24" style="vertical-align: middle; margin-right: 8px;">'
    else:
        img_html = ''
    if is_novacek:
        novacek_badge = '<span style="background-color: #ffc107; color: black; padding: 2px 6px; border-radius: 4px; font-size: 0.75em; margin-left: 8px; font-weight: bold;">NOVÁČEK</span>'
    else:
        novacek_badge = ''
    return f'{img_html}{player_name}{novacek_badge}'

summary_df['Hráč'] = summary_df.apply(format_player_column, axis=1)
summary_df = summary_df.drop(columns=['Je nováček'])

styled_df = summary_df.style.apply(highlight_top3, axis=1).applymap(
    lambda val: color_cells(val, 'pořadí'),
    subset=['📦 Truhly - pořadí (posledních 5)', '🏰 Hrady/Bomby - pořadí (posledních 5)',
            '📦 Truhly - pořadí (všechny hry)', '🏰 Hrady/Bomby - pořadí (všechny hry)']
).format({
    'Celk. pořadí - Posledních 5': lambda x: f"{x:.2f}" if pd.notna(x) else '-',
    '📦 Truhly - pořadí (posledních 5)': lambda x: f"{x:.2f}" if pd.notna(x) else '-',
    '📦 Truhly - skóre (posledních 5)': format_number,
    '🏰 Hrady/Bomby - pořadí (posledních 5)': lambda x: f"{x:.2f}" if pd.notna(x) else '-',
    '🏰 Hrady/Bomby - skóre (posledních 5)': format_number,
    'Celk. pořadí (všechny hry)': lambda x: f"{x:.2f}" if pd.notna(x) else '-',
    '📦 Truhly - pořadí (všechny hry)': lambda x: f"{x:.2f}" if pd.notna(x) else '-',
    '📦 Truhly - skóre (všechny hry)': format_number,
    '🏰 Hrady/Bomby - pořadí (všechny hry)': lambda x: f"{x:.2f}" if pd.notna(x) else '-',
    '🏰 Hrady/Bomby - skóre (všechny hry)': format_number
}, na_rep='-').set_table_styles([
    {'selector': 'thead th', 'props': [('text-align', 'center')]},
    {'selector': 'tbody td', 'props': [('text-align', 'center')]}
])

styled_df = styled_df.hide(axis='index')

# ============================================
# NAVIGAČNÍ LIŠTA SE TŘEMI ZÁLOŽKAMI
# ============================================

tab1, tab2, tab3 = st.tabs(["📊 Tabulka pořadí", "🏆 Rekordy", "📚 Návody"])

# ============================================
# ZÁLOŽKA 1: TABULKA POŘADÍ
# ============================================
with tab1:
    st.title("🎮 Clash Royale - Clan War")
    
    st.markdown('<div style="background-color: #ffffff; padding: 20px; border-radius: 10px; margin-bottom: 20px;">', unsafe_allow_html=True)
    st.markdown("""
**Vítej ve své Clan War aplikaci!**

Zde najdeš:
- 🏅 **Aktuální pořadí** - na základě posledních 5 her
- 📈 **Kompletní statistiky** - všechny odehrané hry
- 📦 **Truhly** a 🏰 **Hrady/Bomby** - rozdělené statistiky

**Jak se počítá pořadí?**

Celkové pořadí vychází z průměrného umístění v Truhlách a Hradech/Bombách (z posledních 5 her každého typu).

🥇 **1. místo** = Zlatá medaile  
🥈 **2. místo** = Stříbrná medaile  
🥉 **3. místo** = Bronzová medaile

Pokud jsi u nás nový a nemáš ještě odehraných alespoň 5 her v Truhle a 5 her v Hradech/Bombách, bereme na tebe speciální ohledy a za tvým jménem, bude po tuto dobu napsáno "NOVÁČEK".

Přechod do nového klanu může být náročný, takže Ti chceme dát dostatek času na aklimatizaci a přizpůsobení se :)
""")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Výstup hlavní tabulky
    st.markdown(
        styled_df.to_html(escape=False, index=False),
        unsafe_allow_html=True
    )

    st.markdown("---")

    # Výběr hráče pro detail
    plain_player_names = df['Hráč'].unique().tolist()
    plain_player_names.sort()

    selected_player = st.selectbox(
        "Vyber hráče pro zobrazení detailů:",
        options=[''] + plain_player_names,
        index=0
    )

    # Detail hráče
    import unicodedata

    def normalize_name(name):
        return (
            unicodedata.normalize('NFKD', name)
            .encode('ascii', 'ignore')
            .decode('utf-8')
            .strip()
            .lower()
        )

    def display_event_section(title_icon, event_name, event_df):
        st.subheader(f"{title_icon} {event_name}")
        if not event_df.empty:
            st.markdown(f"**Všechny zaznamenané hry ({event_name}):**")
            df_display = event_df[['Datum', 'Event', 'Pořadí', 'Skóre']].copy()
            df_display = df_display.sort_values(by='Datum', ascending=False)
            df_display['Datum'] = pd.to_datetime(df_display['Datum'], errors='coerce')
            df_display['Datum'] = df_display['Datum'].dt.strftime('%d.%m.%Y')
            df_display['Pořadí'] = df_display['Pořadí'].astype('Int64')
            
            def color_rank_cell(val):
                return get_color_by_rank(val)
            styled_df_display = df_display.style \
                .applymap(color_rank_cell, subset=['Pořadí']) \
                .format({
                    'Skóre': lambda x: "{:,.0f}".format(x).replace(',', ' ') if pd.notna(x) else '-',
                    'Pořadí': lambda x: str(int(x)) if pd.notna(x) else '-'
                }, na_rep='-') \
                .set_table_styles([
                    {'selector': 'thead th', 'props': [('text-align', 'center')]},
                    {'selector': 'tbody td', 'props': [('text-align', 'center')]}
                ])
            styled_df_display = styled_df_display.hide(axis='index')
            st.markdown(styled_df_display.to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.info(f"Žádná data pro {event_name}.")

    if selected_player:
        st.markdown("---")
        avatar_url = None
        player_name_lower = selected_player.lower()
        if player_name_lower in player_images:
            avatar_url = player_images[player_name_lower]
        else:
            normalized_name_for_lookup = normalize_name(selected_player)
            if normalized_name_for_lookup in player_images:
                avatar_url = player_images[normalized_name_for_lookup]
        if avatar_url:
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <img src="{avatar_url}" width="48" height="48" style="border-radius: 50%; object-fit: cover;">
                    <h2 style="margin: 0;">Detail pro hráče: {selected_player}</h2>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.header(f"Detail pro hráče: {selected_player}")
        st.markdown("---")
        player_data = df[df['Hráč'] == selected_player].copy()
        if not player_data.empty:
            player_data['Datum'] = pd.to_datetime(player_data['Datum'], errors='coerce')
            player_data['Pořadí_inv'] = 51 - player_data['Pořadí']
            truhly_data = player_data[player_data['Event'].str.lower() == 'truhla'].copy()
            hrady_data = player_data[player_data['Event'].str.lower() == 'hrady/bomby'].copy()
            st.subheader("⭐ Souhrnné statistiky (za všechny hry)")
            col_truhly_1, col_truhly_2, col_truhly_3, col_truhly_4 = st.columns(4)
            with col_truhly_1:
                st.metric(
                    label="📦 Truhly - Průměrné pořadí",
                    value=f"{truhly_data['Pořadí'].mean():.2f}" if not truhly_data.empty and not math.isnan(truhly_data['Pořadí'].mean()) else "-",
                    delta_color="off"
                )
            with col_truhly_2:
                st.metric(
                    label="📦 Truhly - Průměrné skóre",
                    value=(
                        f"{int(truhly_data['Skóre'].mean()):_}".replace('_', ' ')
                        if not truhly_data.empty and pd.notna(truhly_data['Skóre'].mean())
                        else "-"
                    ),
                    delta_color="off"
                )
            with col_truhly_3:
                st.metric(
                    label="📦 Truhly - Osobní rekord",
                    value=(
                        f"{int(truhly_data['Skóre'].max()):_}".replace('_', ' ')
                        if not truhly_data.empty and pd.notna(truhly_data['Skóre'].max())
                        else "-"
                    ),
                    delta_color="off"
                )
            with col_truhly_4:
                st.metric(
                    label="📦 Truhly - Odehráno her",
                    value=len(truhly_data)
                )
            st.markdown("---")
            col_hrady_1, col_hrady_2, col_hrady_3, col_hrady_4 = st.columns(4)
            with col_hrady_1:
                st.metric(
                    label="🏰 Hrady/Bomby - Průměrné pořadí",
                    value=f"{hrady_data['Pořadí'].mean():.2f}" if not hrady_data.empty and not math.isnan(hrady_data['Pořadí'].mean()) else "-",
                    delta_color="off"
                )
            with col_hrady_2:
                st.metric(
                    label="🏰 Hrady/Bomby - Průměrné skóre",
                    value=(
                        f"{int(hrady_data['Skóre'].mean()):_}".replace('_', ' ')
                        if not hrady_data.empty and pd.notna(hrady_data['Skóre'].mean())
                        else "-"
                    ),
                    delta_color="off"
                )
            with col_hrady_3:
                st.metric(
                    label="🏰 Hrady/Bomby - Osobní rekord",
                    value=(
                        f"{int(hrady_data['Skóre'].max()):_}".replace('_', ' ')
                        if not hrady_data.empty and pd.notna(hrady_data['Skóre'].max())
                        else "-"
                    ),
                    delta_color="off"
                )
            with col_hrady_4:
                st.metric(
                    label="🏰 Hrady/Bomby - Odehráno her",
                    value=len(hrady_data)
                )
            st.markdown("---")
            display_event_section("📦", "Truhly", truhly_data)
            st.markdown("---")
            display_event_section("🏰", "Hrady / Bomby", hrady_data)
        else:
            st.info("Pro tohoto hráče nejsou k dispozici žádná detailní data v surovém zdroji.")

# ============================================
# ZÁLOŽKA 2: REKORDY
# ============================================
with tab2:
    st.title("🏆 Top 50 rekordů - Truhly")
    
    st.markdown('<div style="background-color: #ffffff; padding: 20px; border-radius: 10px; margin-bottom: 20px;">', unsafe_allow_html=True)
    st.markdown("""
**Nejlepších 50 individuálních výsledků z eventu Truhla**

Tady najdeš ty nejlepší výkony našich hráčů! 💪
""")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Vyfiltruj pouze Truhly a seřaď podle skóre
    truhly_df = df[df['Event'].str.lower() == 'truhla'].copy()
    truhly_df = truhly_df.sort_values(by='Skóre', ascending=False).head(50).reset_index(drop=True)
    
    # Přidej pořadí
    truhly_df.insert(0, 'Pořadí rekordu', range(1, len(truhly_df) + 1))
    
    # Vyber relevantní sloupce
    records_df = truhly_df[['Pořadí rekordu', 'Hráč', 'Datum', 'Skóre', 'Pořadí']].copy()
    records_df['Datum'] = pd.to_datetime(records_df['Datum'], errors='coerce')
    records_df['Datum'] = records_df['Datum'].dt.strftime('%d.%m.%Y')
    
    # Aplikuj barvení na pořadí v eventu
    def color_rank_cell_records(val):
        return get_color_by_rank(val)
    
    # Zvýrazni top 3 rekordy
    def highlight_top3_records(row):
        rank = row['Pořadí rekordu']
        styles = [''] * len(row)
        if rank == 1:
            for i in range(len(row)):
                styles[i] = 'background-color: #FFD700; color: black; font-weight: bold;'
        elif rank == 2:
            for i in range(len(row)):
                styles[i] = 'background-color: #C0C0C0; color: black; font-weight: bold;'
        elif rank == 3:
            for i in range(len(row)):
                styles[i] = 'background-color: #CD7F32; color: black; font-weight: bold;'
        return styles
    
    styled_records = records_df.style.apply(highlight_top3_records, axis=1).applymap(
        color_rank_cell_records,
        subset=['Pořadí']
    ).format({
        'Skóre': lambda x: "{:,.0f}".format(x).replace(',', ' ') if pd.notna(x) else '-',
        'Pořadí': lambda x: str(int(x)) if pd.notna(x) else '-'
    }, na_rep='-').set_table_styles([
        {'selector': 'thead th', 'props': [('text-align', 'center')]},
        {'selector': 'tbody td', 'props': [('text-align', 'center')]}
    ])
    
    styled_records = styled_records.hide(axis='index')
    
    st.markdown(
        styled_records.to_html(escape=False, index=False),
        unsafe_allow_html=True
    )

# ============================================
# ZÁLOŽKA 3: NÁVODY
# ============================================
with tab3:
    st.title("📚 Návody a tipy")
    
    st.markdown('<div style="background-color: #ffffff; padding: 20px; border-radius: 10px; margin-bottom: 20px;">', unsafe_allow_html=True)
    st.markdown("""
**Tipy a triky pro lepší výsledky v Clan War**

Tato sekce bude brzy doplněna o užitečné návody! 🚀

Zatím si můžeš prohlédnout své statistiky v ostatních záložkách.
""")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.info("💡 Návody budou přidány později. Sleduj tuto sekci!")
