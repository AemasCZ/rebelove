import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json
import math
import unicodedata

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

# Výběr worksheetu
worksheet = sheet.worksheet("výsledky")

# Načtení dat
data = worksheet.get_all_records()
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
    .str.replace(r"[^\d.]", "", regex=True)
    .replace("", None)
    .astype(float)
)

# Kompletní styl pro Streamlit aplikaci
st.markdown("""
<style>
    .stApp {
        background-color: #e0e0e0 !important;
        color: black !important;
        font-family: 'Segoe UI', sans-serif;
    }
    
    .main .block-container {
        background-color: #e0e0e0 !important;
        color: black !important;
    }
    
    .sidebar .sidebar-content {
        background-color: #d8d8d8 !important;
        color: black !important;
    }
    
    body {
        background-color: #e0e0e0;
        color: black;
        font-family: 'Segoe UI', sans-serif;
    }
    
    .stMarkdown, .stText, .stWrite,
    .element-container p, .element-container div,
    .stMarkdown p, .stMarkdown div,
    .stSubheader, h1, h2, h3, h4, h5, h6 {
        color: black !important;
    }
    
    .metric-container, .metric-container .metric-value,
    .metric-container .metric-label, .metric-container .metric-delta {
        color: black !important;
    }
    
    .stSelectbox label, .stSelectbox > label {
        color: black !important;
    }
    
    table {
        background-color: #f8f9fa;
        border-collapse: collapse;
        width: auto;
        max-width: 100%;
        border-radius: 10px;
        overflow-x: auto;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
    
    td, th {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        vertical-align: middle;
    }
    
    td {
        padding: 10px;
        color: #000000;
        text-align: center;
        font-size: 0.95em;
    }
    
    th {
        background-color: #e9ecef;
        color: #007bff;
        padding: 10px;
        text-align: center;
        font-size: 1em;
    }
    
    .dataframe th:nth-child(9),
    .dataframe th:nth-child(10),
    .dataframe th:nth-child(11) {
        background-color: #dee2e6 !important;
    }
    
    .stDataFrame {
        background-color: #f8f9fa;
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #ffffff;
        color: black;
        border-color: #ced4da;
    }
    
    .stSelectbox > div > div > select {
        background-color: #ffffff !important;
        color: black !important;
        border-color: #ced4da !important;
    }
    
    .stSelectbox option {
        background-color: #ffffff !important;
        color: black !important;
    }
    
    .stSelectbox > div > div > select:hover {
        background-color: #f8f9fa !important;
        border-color: #adb5bd !important;
    }
    
    .stSelectbox > div > div > select:focus {
        background-color: #ffffff !important;
        color: black !important;
        border-color: #007bff !important;
        box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25) !important;
    }
    
    .stButton > button {
        background-color: #ffffff;
        color: black;
        border-color: #ced4da;
    }
    
    .stButton > button:hover {
        background-color: #f8f9fa;
        border-color: #adb5bd;
    }
    
    .stInfo {
        color: black !important;
    }
    
    div[style*="font-size: 1.1rem"] {
        color: black !important;
    }
    
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
    
    div[data-testid="stSelectbox"] option,
    .stSelectbox option,
    select option {
        background-color: white !important;
        color: black !important;
    }
    
    tr {
        color: black !important;
    }
    
    tr:hover {
        background-color: #e9ecef !important;
    }
    
    .st-emotion-cache-*, 
    [class*="st-emotion-cache"] {
        background-color: white !important;
        color: black !important;
    }
    
    *[role="listbox"], *[role="option"] {
        background-color: white !important;
        color: black !important;
    }

    div[data-testid="stExpander"] > details {
        margin: 0 !important;
        padding: 0 !important;
    }
    div[data-testid="stExpander"] > details > summary {
        background-color: #2e8b57 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 8px 14px !important;
        font-weight: 700 !important;
        margin: 0 !important;
    }
    div[data-testid="stExpander"] > details > summary svg {
        color: white !important;
    }
    .expander-wrap {
        margin: 0 !important;
        padding: 0 !important;
    }
    .expander-wrap div[data-testid="stExpander"] {
        margin: 0 !important;
    }
    .expander-wrap + .expander-wrap {
        margin-top: 2px !important;
    }
    div[data-testid="stExpander"] {
        margin: 0 !important;
    }
    div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stExpander"]) {
        margin-bottom: 2px !important;
    }
    div[data-testid="stVerticalBlock"] {
        gap: 2px !important;
    }
    .danger-expander div[data-testid="stExpander"] > details > summary {
        background-color: #e00000 !important;
        color: white !important;
    }
    .danger-expander div[data-testid="stExpander"] > details > summary svg {
        color: white !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #d8d8d8;
        color: black;
        font-size: 18px;
        font-weight: 600;
        border-radius: 8px 8px 0 0;
        padding: 10px 30px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #e0e0e0 !important;
        color: black !important;
        border-bottom: 3px solid #ffcc00;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #c0c0c0;
    }

</style>
""", unsafe_allow_html=True)

# Definováni obrázků pro hráče
player_images = {
    'niki': "https://i.imgur.com/dQiv8NF.png",
    'janulik': "https://i.imgur.com/x2gGMZK.jpeg",
    'λουση': "https://i.imgur.com/q490sNO.jpeg",
    'michal.': "https://i.imgur.com/3u7rLQN.jpeg",
    'jiří': "https://i.imgur.com/MXkcviA.png",
    'anežka': "https://i.imgur.com/zgqqufy.png",
    'péťa': "https://i.imgur.com/MEFEJ7N.png",
    'pája': "https://i.imgur.com/Wzwaq6d.png",
    'adéla': "https://i.imgur.com/BRc0l9N.png",
    'alexandr': "https://i.imgur.com/LLXk5zW.png",
    'bobeš cumel': "https://i.imgur.com/qjHHaw2.png",
    'daniel': "https://i.imgur.com/ntvS6G8.jpeg",
    'denisa': "https://i.imgur.com/DLRP9PV.jpeg",
    'diana': "https://i.imgur.com/BlntGcy.png",
    'dominik': "https://i.imgur.com/EVaC6Y0.jpeg",
    'gabriela': "https://i.imgur.com/g5jPZaj.png",
    'honza': "https://i.imgur.com/xdriwVZ.jpeg",
    'jan': "https://i.imgur.com/6mTqmid.jpeg",
    'jiri': "https://i.imgur.com/zndiuOz.png",
    'jirka': "https://i.imgur.com/KHjm3OJ.jpeg",
    'karel': "https://i.imgur.com/kV9e3Mb.jpeg",
    'сергій': "https://i.imgur.com/gGiPfpm.png",
    'laduš': "https://i.imgur.com/PZsLWNJ.jpeg",
    'lukáš.': "https://i.imgur.com/ZseSV5j.jpeg",
    'lukáš': "https://i.imgur.com/gzNwY8F.png",
    'marek': "https://i.imgur.com/ZUvfonE.jpeg",
    'martin.': "https://i.imgur.com/PtuCqFE.png",
    'martin': "https://i.imgur.com/06wuyGd.png",
    'michal': "https://i.imgur.com/UodOidD.png",
    'patrick': "https://i.imgur.com/IdS7DJ2.png",
    'petr': "https://i.imgur.com/LJwjqW3.png",
    'petr.': "https://i.imgur.com/26XtOmP.jpeg",
    'erik': "https://i.imgur.com/cLJaT88.png",
    'radek': "https://i.imgur.com/QCWxEBh.png",
    'renáta': "https://i.imgur.com/stD6IGc.png",
    'rysnerova': "https://i.imgur.com/UNL0TLd.png",
    'stanislav': "https://i.imgur.com/JQ7Aver.png",
    'terez': "https://i.imgur.com/54Slb4J.png",
    'veronika': "https://i.imgur.com/4J9AKEO.png",
    'zuzanka': "https://i.imgur.com/8dnuwQM.png",
    'pavla': "https://i.imgur.com/VC72RkP.png",
    'міша': "https://i.imgur.com/QpbAMvx.jpeg",
    'míša': "https://i.imgur.com/t5C6b8E.jpeg",
    'olina': "https://i.imgur.com/tJRo609.jpeg",
    'žanet': "https://i.imgur.com/AwJm34d.jpeg",
    'lenka': "https://i.imgur.com/DXeR3UY.jpeg",
    'jakub': "https://i.imgur.com/KZF9Xjt.jpeg",
    'paťas': "https://i.imgur.com/0e6W2zA.jpeg",
    'natálie': "https://i.imgur.com/jzMKkFL.jpeg",
    'josefa': "https://i.imgur.com/pnDRT7J.png",
    'michaela': "https://i.imgur.com/7DouLnz.png",
    'veronika.': "https://i.imgur.com/KyP4jGx.png",
    'radek.': "https://i.imgur.com/s4a0gSi.png",
    'jana': "https://i.imgur.com/rtdvkwe.png",
    'michal...': "https://i.imgur.com/gI2ALyH.png",
    'michal..': "https://i.imgur.com/CN4h978.png",
    'vlastimil': "https://i.imgur.com/hOVPeqZ.jpeg",
    'filip': "https://i.imgur.com/bXWhcxe.png",
    'petra': "https://i.imgur.com/0hwa1c9.jpeg",
}

def latest_game_is_record(event_df, max_score):
    if event_df.empty or pd.isna(max_score):
        return False
    latest_entry = event_df.sort_values(by='Datum', ascending=False).head(1)
    if latest_entry.empty:
        return False
    latest_score = latest_entry['Skóre'].iloc[0]
    if pd.isna(latest_score):
        return False
    return math.isclose(float(latest_score), float(max_score), rel_tol=1e-9)

# Výpočet dat pro tabulku
hraci = df['Hráč'].unique()
vystup = []

for hrac in hraci:
    d = df[df['Hráč'] == hrac]
    truhly = d[d['Event'].str.lower() == 'truhla'].sort_values(by='Datum', ascending=False).head(10)
    hrady = d[d['Event'].str.lower() == 'hrady/bomby'].sort_values(by='Datum', ascending=False).head(10)

    if truhly.empty and hrady.empty:
        continue

    p_truhla = truhly['Pořadí'].mean()
    s_truhla = truhly['Skóre'].mean()
    
    truhly_vsechny = d[d['Event'].str.lower() == 'truhla']
    max_truhla = truhly_vsechny['Skóre'].max()
    truhla_new_record = latest_game_is_record(truhly_vsechny, max_truhla)

    p_hrady = hrady['Pořadí'].mean()
    s_hrady = hrady['Skóre'].mean()
    
    hrady_vsechny = d[d['Event'].str.lower() == 'hrady/bomby']
    max_hrady = hrady_vsechny['Skóre'].max()
    hrady_new_record = latest_game_is_record(hrady_vsechny, max_hrady)

    vazeny = float('nan')
    if not math.isnan(s_truhla) or not math.isnan(s_hrady):
        truhla_part = s_truhla if not math.isnan(s_truhla) else 0
        hrady_part = s_hrady if not math.isnan(s_hrady) else 0
        vazeny = (truhla_part * 1) + (hrady_part * 0.33)

    hrac_lower = hrac.lower()
    record_categories = []
    if truhla_new_record:
        record_categories.append('Truhla')
    if hrady_new_record:
        record_categories.append('Hrady/Bomby')
    record_badge_html = ''
    if record_categories:
        badge_context = ' & '.join(record_categories)
        record_badge_html = (
            f'<span style="color: #ffffff; background-color: #c70000; padding: 2px 10px; '
            f'border-radius: 999px; font-size: 0.72rem; font-weight: 700; white-space: nowrap; '
            f'align-self: flex-start;">NEW RECORD ({badge_context})</span>'
        )

    novice_badge_html = ''
    if len(truhly) < 5 or len(hrady) < 5:
        novice_badge_html = (
            f'<span style="display: inline-flex; flex-direction: column; margin-left: 4px; '
            f'font-size: 0.72rem; font-weight: 700; color: #ff7a00; line-height: 1.15; '
            f'white-space: nowrap;">'
            f'NOV\u00c1\u010cEK<span style="font-weight: 600; font-size: 0.65rem; color: #ff7a00; '
            f'white-space: nowrap;">(Nem\u00e1 odehr\u00e1no 10 her)</span></span>'
        )

    if hrac_lower in player_images:
        image_url = player_images[hrac_lower]
        jmeno = (
            f'<div style="display: flex; align-items: center; gap: 10px; min-width: 306px; flex-wrap: nowrap;">'
            f'<img src="{image_url}" width="60" style="border-radius:50%; object-fit: cover;">'
            f'<div style="display: flex; flex-direction: column; gap: 4px;">'
            f'  <div style="display: inline-flex; align-items: center; gap: 6px; white-space: nowrap;">'
            f'    <span style="font-size: 1.2rem; font-weight: bold;">{hrac}</span>'
            f'    {novice_badge_html}'
            f'  </div>'
            f'  {record_badge_html}'
            f'</div>'
            f'</div>'
        )
    else:
        jmeno = (
            f'<div style="display: flex; align-items: center; gap: 10px; flex-wrap: nowrap; min-width: 306px;">'
            f'<div style="display: flex; flex-direction: column; gap: 4px;">'
            f'  <div style="display: inline-flex; align-items: center; gap: 6px; white-space: nowrap;">'
            f'    <span style="font-size: 1.2rem; font-weight: bold;">{hrac}</span>'
            f'    {novice_badge_html}'
            f'  </div>'
            f'  {record_badge_html}'
            f'</div>'
            f'</div>'
        )

    def format_score_value(val):
        return f"{int(val):_}".replace('_', ' ') if pd.notna(val) else '-'

    truhla_record_display = format_score_value(max_truhla)
    if truhla_new_record and truhla_record_display != '-':
        truhla_record_display = (
            f'{truhla_record_display}<br>'
            f'<span style="color: #c70000; font-size: 0.72rem; font-weight: 700; '
            f'white-space: nowrap;">NEW RECORD</span>'
        )

    hrady_record_display = format_score_value(max_hrady)
    if hrady_new_record and hrady_record_display != '-':
        hrady_record_display = (
            f'{hrady_record_display}<br>'
            f'<span style="color: #c70000; font-size: 0.72rem; font-weight: 700; '
            f'white-space: nowrap;">NEW RECORD</span>'
        )

    vystup.append({
    '👤 Hráč': jmeno,
    '⭐ Vážený průměr': round(vazeny) if not math.isnan(vazeny) else None,
    '🌟 Truhla – prům. skóre': round(s_truhla) if not math.isnan(s_truhla) else None,
    '🏆 Truhla – max. skóre': truhla_record_display,
    '🌟 Hrady – prům. skóre': round(s_hrady) if not math.isnan(s_hrady) else None,
    '🏆 Hrady – max. skóre': hrady_record_display,
})

vystup_df = pd.DataFrame(vystup)
vystup_df = vystup_df.sort_values(by='⭐ Vážený průměr', ascending=False, na_position='last').reset_index(drop=True)
vystup_df.insert(0, 'Pořadí', range(1, len(vystup_df) + 1))

vystup_df.rename(columns={
    '⭐ Vážený průměr': '⌀ skóre',
    '👤 Hráč': 'Hráč'
}, inplace=True)

vystup_df['⌀ skóre'] = vystup_df['⌀ skóre'].round(0)

vystup_df.insert(
    vystup_df.columns.get_loc('⌀ skóre') + 1, 
    '__SEP1__', 
    ''
)
vystup_df.insert(
    vystup_df.columns.get_loc('🏆 Truhla – max. skóre') + 1, 
    '__SEP2__', 
    ''
)

vystup_df.columns = pd.MultiIndex.from_tuples([
    ('Rebelové', 'Pořadí'),
    ('Rebelové', 'Hráč'),
    ('Rebelové', '⌀ skóre'),
    (' ', ' '),
    ('Truhla', '⌀ body'),
    ('Truhla', 'Osobní rekord'),
    ('  ', '  '),
    ('Hrady/Bomby', '⌀ body'),
    ('Hrady/Bomby', 'Osobní rekord'),
])

def get_color_by_rank(rank, force_text_color=None):
    try:
        rank = int(rank)
        bg_color = ''
        text_color = 'black'

        if 1 <= rank <= 50:
            bg_color = '#cfe8ff'
            text_color = 'black'
        else:
            return ''

        if force_text_color:
            text_color = force_text_color

        return f'background-color: {bg_color}; color: {text_color};'
    except (ValueError, TypeError):
        return ''

def apply_row_styles(row):
    styles = pd.Series('', index=row.index)
    rank = row[('Rebelové', 'Pořadí')]
    base_style = get_color_by_rank(rank, force_text_color='black')
    if base_style:
        styles[('Rebelové', 'Pořadí')] = base_style
    styles[('Rebelové', '⌀ skóre')] = 'background-color: #e6f3ff; color: black; font-weight: bold;'
    styles[(' ', ' ')] = 'background-color: black;'
    styles[('  ', '  ')] = 'background-color: black;'
    return styles

styled_df = vystup_df.style
styled_df = styled_df.apply(apply_row_styles, axis=1)

def format_score(x):
    if isinstance(x, str):
        return x
    return f"{int(x):_}".replace('_', ' ') if pd.notna(x) else '-'

styled_df = styled_df.format({
    ('Rebelové', '⌀ skóre'): format_score,
    ('Truhla', '⌀ body'): format_score,
    ('Truhla', 'Osobní rekord'): format_score,
    ('Hrady/Bomby', '⌀ body'): format_score,
    ('Hrady/Bomby', 'Osobní rekord'): format_score,
})

styled_df = styled_df.set_table_styles([
    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#444'), ('color', 'orange')]},
    {'selector': '.dataframe thead tr:first-child th', 'props': [
        ('border-bottom', '1px solid #ffcc00'),
        ('background-color', '#444'),
        ('color', '#ffcc00')
    ]},
    {'selector': 'th.col_heading.level1', 'props': [
        ('background-color', '#e0e0e0'),
        ('color', 'black'),
        ('font-weight', 'bold'),
        ('text-align', 'center')
    ]},
    {'selector': 'td', 'props': [('text-align', 'center')]},
    {'selector': '.dataframe th:nth-child(4), .dataframe td:nth-child(4)',
     'props': [('width', '20px !important'), ('min-width', '20px !important'), ('max-width', '20px !important'),
               ('background-color', 'black !important'),
               ('color', 'black !important'), ('font-size', '0 !important'),
               ('border', 'none !important'), ('padding', '0 !important'),
               ('text-indent', '-9999px !important'), ('overflow', 'hidden !important'),
               ('white-space', 'nowrap !important')]},
    {'selector': '.dataframe th:nth-child(7), .dataframe td:nth-child(7)',
     'props': [('width', '20px !important'), ('min-width', '20px !important'), ('max-width', '20px !important'),
               ('background-color', 'black !important'),
               ('color', 'black !important'), ('font-size', '0 !important'),
               ('border', 'none !important'), ('padding', '0 !important'),
               ('text-indent', '-9999px !important'), ('overflow', 'hidden !important'),
               ('white-space', 'nowrap !important')]},
])

styled_df = styled_df.hide(axis='index')

# ============================================
# NAVIGAČNÍ LIŠTA
# ============================================

tab1, tab2, tab3 = st.tabs(["📊 Tabulka", "🏆 Rekordy", "📚 Návody"])

# ============================================
# ZÁLOŽKA 1: TABULKA POŘADÍ (PŮVODNÍ STRÁNKA)
# ============================================
with tab1:
    st.title("Přehled hráčů Coin Master")

    posledni_truhla = df[df['Event'].str.lower() == 'truhla']['Datum'].max()
    posledni_hrady = df[df['Event'].str.lower() == 'hrady/bomby']['Datum'].max()

    def format_date(d):
        return d.strftime('%d.%m.%Y') if pd.notna(d) else '-'

    st.markdown(f"""
<div style="margin-top: -0.3rem; margin-bottom: 2rem; font-size: 1.1rem;">
    <strong>📦 Poslední Truhla:</strong> {format_date(posledni_truhla)} &nbsp;&nbsp;|&nbsp;&nbsp;
    <strong>🏰 Poslední Hrady/Bomby:</strong> {format_date(posledni_hrady)}
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="expander-wrap">', unsafe_allow_html=True)
    with st.expander("Jak se počítá Vaše skore?"):
        st.markdown("""
Tvoje celkové skóre se skládá ze dvou částí, které se na konci sečtou dohromady.

Část 1 — Truhly (počítají se naplno)  
Vezmeš svých posledních 10 her v Truhlách.  
Sečteš skóre ze všech těchto her a výsledek vydělíš deseti.  
Tím získáš průměr v Truhlách, který se započítává celý, bez jakékoliv úpravy.

Část 2 — Hrady / Bomby (počítá se jen třetina)  
Vezmeš svých posledních 10 her v Hradech/Bombách.  
Opět sečteš všechna skóre a výsledek vydělíš deseti.  
Získáš průměr v Hradech, ale ten se ještě vydělí třemi – do celkového skóre se tedy počítá jen jedna třetina.

Celkové skóre  
Nakonec sečteš obě části dohromady:  
Průměr z Truhel (100 %) + průměr z Hradů (⅓) = celkové skóre

Příklad  
Průměr v Truhlách: 1 000 → započítává se celých 1 000  
Průměr v Hradech: 900 → započítává se jen třetina, tedy 300  
Celkové skóre = 1 000 + 300 = 1 300
""")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="expander-wrap">', unsafe_allow_html=True)
    with st.expander("Proč je Truhla důležitější než Hrady/Bomby?"):
        st.markdown("""
Výsledky v Truhle určují jakou budeme hrát ligu a podle toho v jaké jsme lize, máme určené odměny v Hradech a Bombách.

Pokud budeme v nejlepší lize, budeme v těchto turnajích mít odměny např. 50-75 tisíc za splnění celého hradu, pokud by jsme ale hráli nejnižší ligu, dostaneme jen např. 1000 spinů za splnění celého hradu a jednotlivé odměny budou také malé (místo 7000 spinů třeba jen 500 spinů atd.)

Proto je pro nás Truhla nejdůležitější událostí ve hře, Hrady a Bomby jsou velmi praktické k získání zásob.
""")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="expander-wrap danger-expander">', unsafe_allow_html=True)
    with st.expander("Kdy jsem v ohrožení?"):
        st.markdown("""
Abys byl 100% v bezpečí, musíš mít nahráno minimálně 200 000 bodů (v průměrném skore, to je ten modrý sloupec se skóre vedle tvého jména). Pokud plníš toto číslo, nemůžeš být kvůli výkonům vyhozený.

Pokud máš méně, neznamená to, že hned končíš, ale zamysli se, jak bys mohl zlepšit svoje výkony. Protože pokud bysme mohli získat nějakého velmi silného hráče a nebude v klanu místo, tvoje pozice může být ohrožena.

Stále platí, že prioritou je pro nás týmovost a slušné chování :)
""")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="expander-wrap">', unsafe_allow_html=True)
    with st.expander("Proč mám u jména NOVÁČEK?"):
        st.markdown("""
Pokud jsi u nás nový a nemáš ještě odehraných alespoň 5 her v Truhle a 5 her v Hradech/Bombách, bereme na tebe speciální ohledy a za tvým jménem, bude po tuto dobu napsáno "NOVÁČEK".

Přechod do nového klanu může být náročný, takže Ti chceme dát dostatek času na aklimatizaci a přizpůsobení se :)
""")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    st.markdown(
        styled_df.to_html(escape=False, index=False),
        unsafe_allow_html=True
    )

    st.markdown("---")

    plain_player_names = df['Hráč'].unique().tolist()
    plain_player_names.sort()

    selected_player = st.selectbox(
        "Vyber hráče pro zobrazení detailů:",
        options=[''] + plain_player_names,
        index=0
    )

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
    st.title("Přehled hráčů Coin Master")
    
    # Vytvoření DataFrame pro rekordy
    truhly_df = df[df['Event'].str.lower() == 'truhla'].copy()
    truhly_df = truhly_df.sort_values(by='Skóre', ascending=False).head(50).reset_index(drop=True)
    truhly_df.insert(0, 'Pořadí', range(1, len(truhly_df) + 1))
    
    # Formátování sloupce Hráč s obrázkem
    def format_player_for_records(row):
        player_name = row['Hráč']
        player_lower = player_name.lower()
        
        if player_lower in player_images:
            avatar_url = player_images[player_lower]
        else:
            normalized = (
                unicodedata.normalize('NFKD', player_name)
                .encode('ascii', 'ignore')
                .decode('utf-8')
                .strip()
                .lower()
            )
            avatar_url = player_images.get(normalized, None)
        
        if avatar_url:
            img_html = f'<img src="{avatar_url}" width="60" style="border-radius:50%; object-fit: cover; margin-right: 10px; vertical-align: middle;">'
        else:
            img_html = ''
        
        return f'<div style="display: flex; align-items: center;"><div style="min-width: 60px;">{img_html}</div><span style="font-size: 1.2rem; font-weight: bold;">{player_name}</span></div>'
    
    truhly_df['Hráč'] = truhly_df.apply(format_player_for_records, axis=1)
    
    # Vyber jen sloupce: Pořadí, Hráč, Datum, Skóre
    records_display = truhly_df[['Pořadí', 'Hráč', 'Datum', 'Skóre']].copy()
    records_display['Datum'] = pd.to_datetime(records_display['Datum'], errors='coerce')
    records_display['Datum'] = records_display['Datum'].dt.strftime('%d.%m.%Y')
    
    # Vytvoříme MultiIndex stejně jako v původní tabulce
    records_display.columns = pd.MultiIndex.from_tuples([
        ('Rebelové', 'Pořadí'),
        ('Rebelové', 'Hráč'),
        ('Truhla', 'Datum'),
        ('Truhla', 'Skóre'),
    ])
    
    # Aplikuj stejné styly jako v původní tabulce
    def apply_row_styles_records(row):
        styles = pd.Series('', index=row.index)
        rank = row[('Rebelové', 'Pořadí')]
        base_style = get_color_by_rank(rank, force_text_color='black')
        if base_style:
            styles[('Rebelové', 'Pořadí')] = base_style
        return styles
    
    styled_records = records_display.style
    styled_records = styled_records.apply(apply_row_styles_records, axis=1)
    
    styled_records = styled_records.format({
        ('Truhla', 'Skóre'): format_score,
    })
    
    styled_records = styled_records.set_table_styles([
        {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#444'), ('color', 'orange')]},
        {'selector': '.dataframe thead tr:first-child th', 'props': [
            ('border-bottom', '1px solid #ffcc00'),
            ('background-color', '#444'),
            ('color', '#ffcc00')
        ]},
        {'selector': 'th.col_heading.level1', 'props': [
            ('background-color', '#e0e0e0'),
            ('color', 'black'),
            ('font-weight', 'bold'),
            ('text-align', 'center')
        ]},
        {'selector': 'td', 'props': [('text-align', 'center')]},
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
    st.title("Přehled hráčů Coin Master")
    
    st.info("💡 Návody a tipy budou přidány později. Sleduj tuto sekci!")
