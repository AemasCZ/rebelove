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
    
    /* Všechny Streamlit elementy s tmavým pozadím */
    .st-emotion-cache-*, 
    [class*="st-emotion-cache"] {
        background-color: white !important;
        color: black !important;
    }
    
    /* Konkrétní override pro select elementy */
    *[role="listbox"], *[role="option"] {
        background-color: white !important;
        color: black !important;
    }

</style>
""", unsafe_allow_html=True)
# Definováni obrázků pro hráče
player_images = {
    'niki': "https://i.imgur.com/dQiv8NF.png",
    'janulik': "https://i.imgur.com/x2gGMZK.jpeg",
    'λουση': "https://i.imgur.com/q490sNO.jpeg", # Ponechávám řecké písmeno
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
    'petr..': "https://i.imgur.com/A8Lgia3.jpeg",
     'radek': "https://i.imgur.com/QCWxEBh.png",
    'renáta': "https://i.imgur.com/stD6IGc.png",
    'rysnerova': "https://i.imgur.com/UNL0TLd.png",
    'stanislav': "https://i.imgur.com/JQ7Aver.png",
     'terez': "https://i.imgur.com/54Slb4J.png",
    'veronika': "https://i.imgur.com/4J9AKEO.png",
    'zuzanka': "https://i.imgur.com/8dnuwQM.png",
    'pavla': "https://i.imgur.com/VC72RkP.png",
    'evča': "https://i.imgur.com/uoJFsEE.png",
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
      
      
}

# Výpočet dat pro tabulku
hraci = df['Hráč'].unique()
vystup = []

for hrac in hraci:
    d = df[df['Hráč'] == hrac]
    truhly = d[d['Event'].str.lower() == 'truhla'].sort_values(by='Datum', ascending=False).head(10)
    hrady = d[d['Event'].str.lower() == 'hrady/bomby'].sort_values(by='Datum', ascending=False).head(10)

    # Přeskoč hráče bez relevantních dat
    if truhly.empty and hrady.empty:
        continue

    # Průměrné pořadí a skóre pro truhly (z posledních 10 her)
    p_truhla = truhly['Pořadí'].mean()
    s_truhla = truhly['Skóre'].mean()
    
    # Osobní rekord pro truhly (ze VŠECH her, ne jen posledních 10)
    truhly_vsechny = d[d['Event'].str.lower() == 'truhla']
    max_truhla = truhly_vsechny['Skóre'].max()

    # Průměrné pořadí a skóre pro hrady (z posledních 10 her)
    p_hrady = hrady['Pořadí'].mean()
    s_hrady = hrady['Skóre'].mean()
    
    # Osobní rekord pro hrady (ze VŠECH her, ne jen posledních 10)
    hrady_vsechny = d[d['Event'].str.lower() == 'hrady/bomby']
    max_hrady = hrady_vsechny['Skóre'].max()

    # Zjistit, zda byla poslední hra právě new record
    last_truhla_is_new = False
    if not truhly_vsechny.empty and pd.notna(max_truhla):
        last_truhla = truhly_vsechny.sort_values(by='Datum', ascending=False).iloc[0]
        last_truhla_is_new = pd.notna(last_truhla['Skóre']) and last_truhla['Skóre'] == max_truhla

    last_hrady_is_new = False
    if not hrady_vsechny.empty and pd.notna(max_hrady):
        last_hrady = hrady_vsechny.sort_values(by='Datum', ascending=False).iloc[0]
        last_hrady_is_new = pd.notna(last_hrady['Skóre']) and last_hrady['Skóre'] == max_hrady

    # Formátování maxima + případný červený tag
    def fmt_score_with_tag(score, is_new):
        if pd.isna(score):
            return '-'
        s = f"{int(score):_}".replace('_', ' ')
        if is_new:
            return f'{s} <span style="color:red; font-weight:bold;">NEW RECORD</span>'
        return s

    # Vážený průměr pořadí
    vazeny = float('nan')
    if not math.isnan(p_truhla) and not math.isnan(p_hrady):
        vazeny = (p_truhla * 1 + p_hrady * 0.5) / 1.5
    elif not math.isnan(p_truhla):
        vazeny = p_truhla
    elif not math.isnan(p_hrady):
        vazeny = p_hrady * 1 

    # Vzhled hráče s obrázkem
    hrac_lower = hrac.lower()
    if hrac_lower in player_images:
        image_url = player_images[hrac_lower]
        jmeno = f'<div style="display: flex; align-items: center; gap: 10px; min-width: 180px;"><img src="{image_url}" width="60" style="border-radius:50%; object-fit: cover;"><span style="font-size: 1.2rem; font-weight: bold;">{hrac}</span></div>'
    else:
        jmeno = hrac

    # Přidání dat do výstupního seznamu - použijeme původní názvy pro snadnější manipulaci
    vystup.append({
        '👤 Hráč': jmeno,
        '⭐ Vážený průměr': round(vazeny, 2) if not math.isnan(vazeny) else None,
        '🔹 Truhla – prům. pořadí': round(p_truhla, 2) if not math.isnan(p_truhla) else '-',
        '🌟 Truhla – prům. skóre': round(s_truhla) if not math.isnan(s_truhla) else '-',
        '🏆 Truhla – max. skóre': fmt_score_with_tag(max_truhla, last_truhla_is_new),
        '🔹 Hrady – prům. pořadí': round(p_hrady, 2) if not math.isnan(p_hrady) else '-',
        '🌟 Hrady – prům. skóre': round(s_hrady) if not math.isnan(s_hrady) else '-',
        '🏆 Hrady – max. skóre': fmt_score_with_tag(max_hrady, last_hrady_is_new),
    })

# Vytvoření DataFrame z výstupního seznamu
vystup_df = pd.DataFrame(vystup)
# Seřazení podle váženého průměru
vystup_df = vystup_df.sort_values(by='⭐ Vážený průměr', na_position='last').reset_index(drop=True)
# Vložení sloupce 'Pořadí' na začátek
vystup_df.insert(0, 'Pořadí', range(1, len(vystup_df) + 1))

# Přejmenování sloupců pro MultiIndex
# Používáme zde spíše finální názvy pro MultiIndex
vystup_df.rename(columns={
    '⭐ Vážený průměr': '⌀ pořadí', # Stále stejný název pro usnadnění
    '👤 Hráč': 'Hráč' # Stále stejný název pro usnadnění
}, inplace=True)

# Zaokrouhlení na 2 desetinná místa v rámci dat DataFrame
vystup_df['⌀ pořadí'] = vystup_df['⌀ pořadí'].round(2)

# Vložení separátorů jako obyčejných sloupců s unikátními názvy
vystup_df.insert(
    vystup_df.columns.get_loc('⌀ pořadí') + 1, 
    '__SEP1__', 
    ''
)
vystup_df.insert(
    vystup_df.columns.get_loc('🏆 Truhla – max. skóre') + 1, 
    '__SEP2__', 
    ''
)

# Nyní přiřadíme MultiIndex na základě pozic a požadovaných názvů
# Použijeme prázdný znak místo názvů pro separátory
vystup_df.columns = pd.MultiIndex.from_tuples([
    # Skupina "Rebelové"
    ('Rebelové', 'Pořadí'),
    ('Rebelové', 'Hráč'),
    ('Rebelové', '⌀ pořadí'),
    
    (' ', ' '), # První oddělovací sloupec - prázdný znak
    
    # Skupina "Truhla"
    ('Truhla', '⌀ pořadí'),
    ('Truhla', '⌀ body'),
    ('Truhla', 'Osobní rekord'),
    
    ('  ', '  '), # Druhý oddělovací sloupec - dva prázdné znaky
    
    # Skupina "Hrady/Bomby"
    ('Hrady/Bomby', '⌀ pořadí'),
    ('Hrady/Bomby', '⌀ body'),
    ('Hrady/Bomby', 'Osobní rekord'),
])


# Funkce pro barevné škály podle pořadí
def get_color_by_rank(rank, force_text_color=None):
    try:
        rank = int(rank)
        bg_color = ''
        text_color = 'black'

        if 1 <= rank <= 10:
            bg_color = '#00cc00'
            text_color = 'black'
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
            text_color = 'black'
        else:
            return ''

        if force_text_color:
            text_color = force_text_color

        return f'background-color: {bg_color}; color: {text_color};'
    except (ValueError, TypeError):
        return ''

# Funkce, která aplikuje styly na CELÝ ŘÁDEK
def apply_row_styles(row):
    # Vytvoříme Series s prázdnými styly pro všechny sloupce v daném řádku
    styles = pd.Series('', index=row.index)

    # Přistupujeme k hodnotám podle tuple (top_level, bottom_level)
    rank = row[('Rebelové', 'Pořadí')]

    # 1) Styl pro sloupec 'Pořadí' (uvnitř skupiny Rebelové)
    styles[('Rebelové', 'Pořadí')] = get_color_by_rank(rank, force_text_color='black')

    # 3) Styl pro sloupec '⌀ pořadí' (uvnitř skupiny Rebelové)
    styles[('Rebelové', '⌀ pořadí')] = get_color_by_rank(rank, force_text_color='black') + 'font-weight: bold;'

    # Stylování černých separátorů
    styles[(' ', ' ')] = 'background-color: black;'
    styles[('  ', '  ')] = 'background-color: black;'

    return styles

# Stylování DataFrame
styled_df = vystup_df.style

# Použijeme apply s axis=1, abychom mohli stylovat sloupce na základě hodnoty z jiného sloupce v řádku
styled_df = styled_df.apply(apply_row_styles, axis=1)

# 1) Formátování čísel na 2 desetinná místa pro zobrazení
# Zde také používáme tuple pro odkazování na sloupec
# Lambda funkce pro formátování čísel s mezerou jako oddělovačem tisíců a bez desetinných míst
# a s ošetřením pro NaN (Not a Number) hodnoty, které se zobrazí jako '-'
format_score = lambda x: f"{int(x):_}".replace('_', ' ') if pd.notna(x) else '-'

styled_df = styled_df.format({
    ('Rebelové', '⌀ pořadí'): '{:.2f}', # Vážený průměr - 2 desetinná místa
    ('Truhla', '⌀ pořadí'): '{:.2f}',    # Průměrné pořadí Truhly - 2 desetinná místa
    ('Truhla', '⌀ body'): format_score,  # Průměrné skóre Truhly - formát s mezerami
    ('Truhla', 'Osobní rekord'): format_score, # Osobní rekord Truhly - formát s mezerami
    ('Hrady/Bomby', '⌀ pořadí'): '{:.2f}', # Průměrné pořadí Hradů/Bomb - 2 desetinná místa
    ('Hrady/Bomby', '⌀ body'): format_score,  # Průměrné skóre Hradů/Bomb - formát s mezerami
    ('Hrady/Bomby', 'Osobní rekord'): format_score, # Osobní rekord Hradů/Bomb - formát s mezerami
})

# 5) Styly pro hlavičky a buňky tabulky
styled_df = styled_df.set_table_styles([
    # Obecné styly pro všechny hlavičky
    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#444'), ('color', 'orange')]},
    
    # Styly pro horní úroveň hlaviček (Rebelové, Truhla, Hrady/Bomby)
    {'selector': '.dataframe thead tr:first-child th', 'props': [
        ('border-bottom', '1px solid #ffcc00'), # Oranžová linka pod první úrovní
        ('background-color', '#444'), # Barva pozadí pro horní úroveň
        ('color', '#ffcc00') # Barva textu pro horní úroveň
    ]},

# Styly pro dolní úroveň hlaviček (např. ⌀ pořadí, ⌀ body, Osobní rekord, atd.)
{'selector': 'th.col_heading.level1', 'props': [
    ('background-color', '#e0e0e0'),
    ('color', 'black'),
    ('font-weight', 'bold'),
    ('text-align', 'center')
]},



    # Obecné styly pro všechny buňky
    {'selector': 'td', 'props': [('text-align', 'center')]},
    
    # Styly pro PRVNÍ ČERNÝ SLOUPEC (4. vizuální sloupec)
    # Kompletně černý sloupec bez jakéhokoliv textu
    {'selector': '.dataframe th:nth-child(4), .dataframe td:nth-child(4)',
     'props': [('width', '20px !important'), ('min-width', '20px !important'), ('max-width', '20px !important'),
               ('background-color', 'black !important'),
               ('color', 'black !important'), ('font-size', '0 !important'),
               ('border', 'none !important'), ('padding', '0 !important'),
               ('text-indent', '-9999px !important'), ('overflow', 'hidden !important'),
               ('white-space', 'nowrap !important')]},

    # Styly pro DRUHÝ ČERNÝ SLOUPEC (8. vizuální sloupec)
    # Kompletně černý sloupec bez jakéhokoliv textu
    {'selector': '.dataframe th:nth-child(8), .dataframe td:nth-child(8)',
     'props': [('width', '20px !important'), ('min-width', '20px !important'), ('max-width', '20px !important'),
               ('background-color', 'black !important'),
               ('color', 'black !important'), ('font-size', '0 !important'),
               ('border', 'none !important'), ('padding', '0 !important'),
               ('text-indent', '-9999px !important'), ('overflow', 'hidden !important'),
               ('white-space', 'nowrap !important')]},
   
])

# Skrytí indexu řádků
styled_df = styled_df.hide(axis='index')

# Titulek a úvodní oddělovač
st.title("Přehled hráčů Coin Master")

# Výpis posledních dat událostí
# Vyhledání posledních dat pro Truhla a Hrady/Bomby
posledni_truhla = df[df['Event'].str.lower() == 'truhla']['Datum'].max()
posledni_hrady = df[df['Event'].str.lower() == 'hrady/bomby']['Datum'].max()

# Zformátujeme datum do čitelného formátu (např. 01.08.2025)
def format_date(d):
    return d.strftime('%d.%m.%Y') if pd.notna(d) else '-'

# Vykreslení do aplikace
st.markdown(f"""
<div style="margin-top: -1rem; margin-bottom: 2rem; font-size: 1.1rem;">
    <strong>📦 Poslední Truhla:</strong> {format_date(posledni_truhla)} &nbsp;&nbsp;|&nbsp;&nbsp;
    <strong>🏰 Poslední Hrady/Bomby:</strong> {format_date(posledni_hrady)}
</div>
""", unsafe_allow_html=True)

st.markdown("---")


# Výstup do Streamlitu jako HTML - ZDE SE VYKRESLÍ HLAVNÍ TABULKA
# escape=False je nezbytné pro zobrazení HTML obsahu ve sloupci 'Hráč' (např. obrázek)
# index=False zajistí, že se nebude zobrazovat index Pandas DataFrame
st.markdown(
    styled_df.to_html(escape=False, index=False),
    unsafe_allow_html=True
)

# Oddělovač mezi tabulkou a výběrem hráče
st.markdown("---")

# Vezmeme jména hráčů z původního DataFrame, abychom měli čisté názvy bez HTML
plain_player_names = df['Hráč'].unique().tolist()
plain_player_names.sort()  # Abecední řazení

# Vytvoření selectboxu pro výběr hráče
selected_player = st.selectbox(
    "Vyber hráče pro zobrazení detailů:",
    options=[''] + plain_player_names,
    index=0
)

# ==========================================================
# ZDE ZAČÍNÁ KÓD PRO DETAIL HRÁČE
# ==========================================================
import unicodedata
import pandas as pd # Důležité pro pd.notna() a DataFrame stylování!

# Funkce pro normalizaci jména
def normalize_name(name):
    return (
        unicodedata.normalize('NFKD', name)
        .encode('ascii', 'ignore')
        .decode('utf-8')
        .strip()
        .lower()
    )

# Funkce get_color_by_rank by měla být definována globálně na začátku vašeho skriptu
# (tak jak ji již máš pro hlavní tabulku). Pro referenci:
# Je důležité, aby tato funkce VRACELA i barvu textu, tak jak byla původně.
# Globální CSS pravidla v display_event_section pak toto přepsají pro konkrétní tabulky.
# def get_color_by_rank(rank, force_text_color=None):
#     try:
#         rank = int(rank)
#         bg_color = ''
#         text_color = 'black' # Default text color if no specific rule is hit
#         if 1 <= rank <= 10:
#             bg_color = '#00cc00'
#             text_color = 'white' # Text color for dark green
#         elif 11 <= rank <= 30:
#             bg_color = '#c6efce'
#             text_color = 'black' # Text color for light green
#         elif 31 <= rank <= 40:
#             bg_color = '#ffeb9c'
#             text_color = 'black' # Text color for yellow
#         elif 41 <= rank <= 47:
#             bg_color = '#f4cccc'
#             text_color = 'black' # Text color for light red/pink
#         elif 48 <= rank <= 50:
#             bg_color = '#ff0000'
#             text_color = 'white' # Text color for dark red
#         else:
#             return '' # No specific style, let general CSS apply
#         
#         # If force_text_color is provided, it overrides the calculated text_color
#         if force_text_color:
#             text_color = force_text_color
#             
#         return f'background-color: {bg_color}; color: {text_color};'
#     except (ValueError, TypeError):
#         return ''


# Funkce pro zobrazení detailů konkrétního typu eventu (např. Truhly nebo Hrady/Bomby)
# Najděte tuto funkci v kódu a nahraďte ji:

def display_event_section(title_icon, event_name, event_df):
    st.subheader(f"{title_icon} {event_name}")
    if not event_df.empty:
        st.markdown(f"**Všechny zaznamenané hry ({event_name}):**")
        # Vybereme pouze potřebné sloupce (a ignorujeme případný levý index z Google Sheets)
        df_display = event_df[['Datum', 'Event', 'Pořadí', 'Skóre']].copy()
        df_display = df_display.sort_values(by='Datum', ascending=False)
        # ✅ Změna: pouze datum bez času
        df_display['Datum'] = pd.to_datetime(df_display['Datum'], errors='coerce')
        df_display['Datum'] = df_display['Datum'].dt.strftime('%d.%m.%Y')
        
        # ✅ NOVÁ ZMĚNA: Převedeme pořadí na celé číslo
        df_display['Pořadí'] = df_display['Pořadí'].astype('Int64')  # Int64 umožňuje NaN hodnoty
        
        # Barvení Pořadí
        def color_rank_cell(val):
            return get_color_by_rank(val)
        styled_df_display = df_display.style \
            .applymap(color_rank_cell, subset=['Pořadí']) \
            .format({
                'Skóre': lambda x: "{:,.0f}".format(x).replace(',', ' ') if pd.notna(x) else '-',
                'Pořadí': lambda x: str(int(x)) if pd.notna(x) else '-'  # ✅ NOVÁ ZMĚNA: Formátování pořadí jako celé číslo
            }, na_rep='-') \
            .set_table_styles([
                {'selector': 'thead th', 'props': [('text-align', 'center')]},
                {'selector': 'tbody td', 'props': [('text-align', 'center')]}
            ])
        # Skryjte index
        styled_df_display = styled_df_display.hide(axis='index')
        # Zobrazit jako HTML (nutné pro barvení + styling)
        st.markdown(styled_df_display.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.info(f"Žádná data pro {event_name}.")






# Zbytek vašeho kódu pro selected_player a metriky zůstává nezměněn:
if selected_player:
    st.markdown("---") # Oddělovač
    # --- Hlavička s obrázkem a jménem hráče ---
    avatar_url = None
    # 1. Pokusit se najít obrázek pomocí jména převedeného jen na malá písmena
    player_name_lower = selected_player.lower()
    if player_name_lower in player_images:
        avatar_url = player_images[player_name_lower]
    else:
        # 2. Pokud se nenajde přímo, zkusit normalizované jméno (bez diakritiky)
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
    st.markdown("---") # Oddělovač
    # --- Vyfiltruj a připrav data pro vybraného hráče ---
    player_data = df[df['Hráč'] == selected_player].copy()
    if not player_data.empty:
        player_data['Datum'] = pd.to_datetime(player_data['Datum'], errors='coerce')
        player_data['Pořadí_inv'] = 51 - player_data['Pořadí']
        # Rozdělení dat podle typu eventu
        truhly_data = player_data[player_data['Event'].str.lower() == 'truhla'].copy()
        hrady_data = player_data[player_data['Event'].str.lower() == 'hrady/bomby'].copy()
        # --- Souhrnné statistiky ---
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
