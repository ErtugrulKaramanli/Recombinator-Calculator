import streamlit as st
from math import comb

# Set page configuration
st.set_page_config(page_title="Recombinator Calculator", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .stTextInput > div > div > input {
        height: 28px;
        padding: 2px 8px;
        font-size: 13px;
    }
    .stSelectbox > div > div {
        font-size: 13px;
    }
    .stSelectbox > div > div > div {
        padding: 4px;
        height: 28px;
    }
    .stSelectbox select {
        font-size: 13px;
    }
    div[data-testid="stVerticalBlock"] > div {
        padding-top: 0rem;
        padding-bottom: 0rem;
    }
    .main > div {
        padding-top: 0.5rem;
    }
    h1 {
        text-align: center;
        margin-bottom: 0.5rem;
        font-size: 24px;
    }
    h3 {
        margin-top: 0.2rem;
        margin-bottom: 0.2rem;
        font-size: 16px;
    }
    .stButton > button {
        width: 100%;
        padding: 4px;
        font-size: 13px;
    }
    .result-text {
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        margin-top: 10px;
        color: #1f77b4;
    }
    .error-text {
        text-align: center;
        font-size: 16px;
        font-weight: bold;
        margin-top: 10px;
        color: #d62728;
    }
    div[data-testid="stHorizontalBlock"] {
        border: 2px solid #dc3545 !important;
        border-radius: 6px;
        padding: 4px;
        margin-bottom: 6px;
        background-color: #f8f9fa;
    }
    label {
        font-size: 13px;
    }
    .stCheckbox label {
        font-size: 13px;
    }
    .stTextArea label {
        font-size: 13px;
    }
    </style>
    """, unsafe_allow_html=True)

# === Probability and Parsing Functions ===
def get_count_probabilities(count):
    if count == 0:
        return {0: 1.0}
    elif count == 1:
        return {0: 0.41, 1: 0.59}
    elif count == 2:
        return {1: 0.667, 2: 0.333}
    elif count == 3:
        return {1: 0.50, 2: 0.40, 3: 0.10}
    elif count == 4:
        return {1: 0.10, 2: 0.60, 3: 0.30}
    elif count == 5:
        return {2: 0.43, 3: 0.57}
    elif count == 6:
        return {2: 0.30, 3: 0.70}
    return {}

def calculate_selection_probability(all_mods_list, unique_mods, desired_mods, not_desired_mods, outcome_count, winning_base):
    available_mods = []
    for mod_info in all_mods_list:
        if mod_info['non_native'] and mod_info['item'] != winning_base:
            continue
        available_mods.append(mod_info['mod'])
    
    available_unique = list(set(available_mods))
    
    for desired in desired_mods:
        if desired not in available_unique:
            return 0.0
    
    selectable_mods = [m for m in available_unique if m not in not_desired_mods]
    
    if len(selectable_mods) < outcome_count or len(desired_mods) > outcome_count:
        return 0.0
    
    total_combinations = comb(len(selectable_mods), outcome_count)
    remaining_slots = outcome_count - len(desired_mods)
    non_desired_selectable = [m for m in selectable_mods if m not in desired_mods]
    
    if remaining_slots > len(non_desired_selectable):
        return 0.0
    
    favorable_combinations = comb(len(non_desired_selectable), remaining_slots)
    return favorable_combinations / total_combinations

def calculate_modifier_probability(mods_item1, mods_item2, desired_mods, not_desired_mods, item1_base_desired, item2_base_desired):
    if len(desired_mods) == 0 and len(not_desired_mods) == 0:
        return 1.0
    
    all_mods_list = mods_item1 + mods_item2
    total_count = len(all_mods_list)
    
    if total_count == 0:
        return 0.0 if len(desired_mods) > 0 else 1.0
    
    unique_mods = list(set([m['mod'] for m in all_mods_list]))
    count_probs = get_count_probabilities(total_count)
    total_prob = 0.0
    
    for outcome_count, count_prob in count_probs.items():
        if outcome_count == 0:
            if len(desired_mods) == 0:
                total_prob += count_prob
            continue
        
        if item1_base_desired or item2_base_desired:
            prob_base1 = calculate_selection_probability(all_mods_list, unique_mods, desired_mods, not_desired_mods, outcome_count, 1)
            prob_base2 = calculate_selection_probability(all_mods_list, unique_mods, desired_mods, not_desired_mods, outcome_count, 2)
            selection_prob = prob_base1 if item1_base_desired else prob_base2
        else:
            prob_base1 = calculate_selection_probability(all_mods_list, unique_mods, desired_mods, not_desired_mods, outcome_count, 1)
            prob_base2 = calculate_selection_probability(all_mods_list, unique_mods, desired_mods, not_desired_mods, outcome_count, 2)
            selection_prob = (prob_base1 + prob_base2) / 2
        
        total_prob += count_prob * selection_prob
    
    return total_prob

def parse_item_text(item_text):
    """Parse item text and extract prefixes and suffixes"""
    lines = item_text.strip().split('\n')
    prefixes, suffixes = [], []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if 'Prefix Modifier' in line and i + 1 < len(lines):
            prefixes.append(lines[i + 1].strip())
        elif 'Suffix Modifier' in line and i + 1 < len(lines):
            suffixes.append(lines[i + 1].strip())
        i += 1
    
    return prefixes, suffixes

# === Language Setup ===
col_lang, _ = st.columns([1, 5])
with col_lang:
    language = st.selectbox("", ["English", "Turkish"], key="language_selector", label_visibility="collapsed")

translations = {
    "English": {
        "title": "Recombinator Calculator",
        "first_item": "First Item",
        "second_item": "Second Item",
        "desired_base": "Desired Final Base",
        "calculate": "Calculate",
        "probability": "Probability of getting desired affixes:",
        "reset": "Reset",
        "error_exclusive": "There can only be 1 exclusive modifier on an item",
        "error_both_bases": "Cannot select both bases as desired",
        "none": "None",
        "exclusive": "Exclusive",
        "non_native": "Non-Native",
        "both": "Both",
        "desired": "Desired",
        "not_desired": "Not Desired",
        "doesnt_matter": "Doesn't Matter",
        "paste_item": "Paste Item"
    },
    "Turkish": {
        "title": "Recombinator Hesaplayıcısı",
        "first_item": "İlk Item",
        "second_item": "İkinci Item",
        "desired_base": "İstediğiniz Final Base",
        "calculate": "Hesapla",
        "probability": "İstediğiniz affixlerin gelme olasılığı:",
        "reset": "Sıfırla",
        "error_exclusive": "Bir itemde sadece 1 exclusive modifier olabilir",
        "error_both_bases": "Her iki base'i de istediğiniz olarak seçemezsiniz",
        "none": "Yok",
        "exclusive": "Exclusive",
        "non_native": "Non-Native",
        "both": "İkisi de",
        "desired": "İstiyorum",
        "not_desired": "İstemiyorum",
        "doesnt_matter": "Farketmez",
        "paste_item": "Item Yapıştır"
    }
}
t = translations[language]
st.markdown(f"<h1>{t['title']}</h1>", unsafe_allow_html=True)

# === Session State Initialization ===
for key in ['item1_base_desired', 'item2_base_desired', 'show_paste_item1', 'show_paste_item2']:
    if key not in st.session_state:
        st.session_state[key] = False

labels = ["Prefix 1", "Prefix 2", "Prefix 3", "Suffix 1", "Suffix 2", "Suffix 3"]

# === ITEM 1 COLUMN ===
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"<h3>{t['first_item']}</h3>", unsafe_allow_html=True)
    base_col, paste_col = st.columns([1, 1])
    with base_col:
        item1_base = st.checkbox(t['desired_base'], key="item1_base_check")
        if item1_base and st.session_state.get('item2_base_desired', False):
            st.session_state['item2_base_desired'] = False
        st.session_state['item1_base_desired'] = item1_base
    with paste_col:
        if st.button(t['paste_item'], key="paste_btn_item1"):
            st.session_state['show_paste_item1'] = not st.session_state.get('show_paste_item1', False)

    if st.session_state.get('show_paste_item1', False):
        item_text = st.text_area("Paste item text here:", key="item1_paste_area", height=150)
        if st.button("Parse", key="parse_item1"):
            prefixes, suffixes = parse_item_text(item_text)
            for idx, prefix in enumerate(prefixes[:3]):
                st.session_state[f'item1_input_{idx}'] = prefix
            for idx, suffix in enumerate(suffixes[:3]):
                st.session_state[f'item1_input_{idx + 3}'] = suffix
            st.session_state['show_paste_item1'] = False
            st.rerun()

    for i in range(6):
        input_col, type_col, pref_col = st.columns([2, 1, 1])
        with input_col:
            st.text_input(labels[i], key=f"item1_input_{i}", label_visibility="visible")
        with type_col:
            st.selectbox("", [t['none'], t['exclusive'], t['non_native'], t['both']], key=f"item1_type_{i}", label_visibility="collapsed")
        with pref_col:
            st.selectbox("", [t['doesnt_matter'], t['not_desired'], t['desired']], key=f"item1_pref_{i}", label_visibility="collapsed", index=1)

# === ITEM 2 COLUMN ===
with col2:
    st.markdown(f"<h3>{t['second_item']}</h3>", unsafe_allow_html=True)
    base_col, paste_col = st.columns([1, 1])
    with base_col:
        item2_base = st.checkbox(t['desired_base'], key="item2_base_check")
        if item2_base and st.session_state.get('item1_base_desired', False):
            st.session_state['item1_base_desired'] = False
        st.session_state['item2_base_desired'] = item2_base
    with paste_col:
        if st.button(t['paste_item'], key="paste_btn_item2"):
            st.session_state['show_paste_item2'] = not st.session_state.get('show_paste_item2', False)

    if st.session_state.get('show_paste_item2', False):
        item_text = st.text_area("Paste item text here:", key="item2_paste_area", height=150)
        if st.button("Parse", key="parse_item2"):
            prefixes, suffixes = parse_item_text(item_text)
            for idx, prefix in enumerate(prefixes[:3]):
                st.session_state[f'item2_input_{idx}'] = prefix
            for idx, suffix in enumerate(suffixes[:3]):
                st.session_state[f'item2_input_{idx + 3}'] = suffix
            st.session_state['show_paste_item2'] = False
            st.rerun()

    for i in range(6):
        input_col, type_col, pref_col = st.columns([2, 1, 1])
        with input_col:
            st.text_input(labels[i], key=f"item2_input_{i}", label_visibility="visible")
        with type_col:
            st.selectbox("", [t['none'], t['exclusive'], t['non_native'], t['both']], key=f"item2_type_{i}", label_visibility="collapsed")
        with pref_col:
            st.selectbox("", [t['doesnt_matter'], t['not_desired'], t['desired']], key=f"item2_pref_{i}", label_visibility="collapsed", index=1)

# === Calculate & Reset Buttons ===
st.write("")
col_calc, col_reset = st.columns([1, 1])

with col_calc:
    if st.button(t['calculate'], type="primary"):
        st.markdown('<div class="result-text">Calculation logic connected here.</div>', unsafe_allow_html=True)

with col_reset:
    if st.button(t['reset'], type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
