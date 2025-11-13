import streamlit as st
from math import comb

# Set page configuration
st.set_page_config(page_title="Recombinator Calculator", layout="wide")

# -----------------------
# CSS
# -----------------------
st.markdown("""
    <style>
    /* Input sizing */
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

    /* Red rectangle only for the affix rows (input-group) */
    .input-group {
        border: 2px solid #dc3545;
        border-radius: 6px;
        padding: 6px;
        margin-bottom: 8px;
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

    /* Make disabled checkboxes look grayed - streamlit handles disabled but this helps visually */
    .stCheckbox [disabled] {
        opacity: 0.6;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------
# Probability & Parsing Helpers (kept the logic from your original)
# -----------------------
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

# This function builds the modifier lists and computes final probability by reading widget keys directly
def calculate_combined_probability_from_widgets(translations_map):
    t = translations_map
    # Build lists for prefixes/suffixes for both items
    prefixes_item1, prefixes_item2 = [], []
    suffixes_item1, suffixes_item2 = [], []
    desired_prefixes, desired_suffixes = set(), set()
    not_desired_prefixes, not_desired_suffixes = set(), set()
    exclusive_mods = []
    
    # iterate over 6 affix slots
    for i in range(6):
        mod_type = 'prefix' if i < 3 else 'suffix'
        # Item 1
        key_input = f'item1_input_{i}'
        val = st.session_state.get(key_input, '').strip()
        if val:
            type_key = st.session_state.get(f'item1_type_{i}', t['none'])
            is_exclusive = type_key in [t['exclusive'], 'Exclusive', 'Exclusive']
            is_non_native = type_key in [t['non_native'], 'Non-Native', 'Non-Native']
            mod_info = {'mod': val, 'non_native': is_non_native, 'exclusive': is_exclusive, 'item': 1}
            if mod_type == 'prefix':
                prefixes_item1.append(mod_info)
            else:
                suffixes_item1.append(mod_info)
            pref = st.session_state.get(f'item1_pref_{i}', t['not_desired'])
            if pref in [t['desired'], 'Desired', 'İstiyorum']:
                if mod_type == 'prefix':
                    desired_prefixes.add(val)
                else:
                    desired_suffixes.add(val)
            elif pref in [t['not_desired'], 'Not Desired', 'İstemiyorum']:
                if mod_type == 'prefix':
                    not_desired_prefixes.add(val)
                else:
                    not_desired_suffixes.add(val)
            if is_exclusive:
                exclusive_mods.append((val, pref in [t['desired'], 'Desired', 'İstiyorum'], mod_type, 1))
        # Item 2
        key_input = f'item2_input_{i}'
        val = st.session_state.get(key_input, '').strip()
        if val:
            type_key = st.session_state.get(f'item2_type_{i}', t['none'])
            is_exclusive = type_key in [t['exclusive'], 'Exclusive', 'Exclusive']
            is_non_native = type_key in [t['non_native'], 'Non-Native', 'Non-Native']
            mod_info = {'mod': val, 'non_native': is_non_native, 'exclusive': is_exclusive, 'item': 2}
            if mod_type == 'prefix':
                prefixes_item2.append(mod_info)
            else:
                suffixes_item2.append(mod_info)
            pref = st.session_state.get(f'item2_pref_{i}', t['not_desired'])
            if pref in [t['desired'], 'Desired', 'İstiyorum']:
                if mod_type == 'prefix':
                    desired_prefixes.add(val)
                else:
                    desired_suffixes.add(val)
            elif pref in [t['not_desired'], 'Not Desired', 'İstemiyorum']:
                if mod_type == 'prefix':
                    not_desired_prefixes.add(val)
                else:
                    not_desired_suffixes.add(val)
            if is_exclusive:
                exclusive_mods.append((val, pref in [t['desired'], 'Desired', 'İstiyorum'], mod_type, 2))
    
    # exclusive-mod rules
    if len(exclusive_mods) > 1:
        if len(exclusive_mods) == 2:
            ex1, ex2 = exclusive_mods
            if (ex1[2] == 'prefix' and ex2[2] == 'suffix' and ex1[1] and not ex2[1]) or \
               (ex2[2] == 'prefix' and ex1[2] == 'suffix' and ex2[1] and not ex1[1]):
                return 0.5, None
        return None, t['error_exclusive']
    
    # base desired handling
    if st.session_state.get('item1_base_desired', False) and st.session_state.get('item2_base_desired', False):
        return None, t['error_both_bases']
    base_prob = 1.0
    if st.session_state.get('item1_base_desired', False):
        base_prob = 0.5
    elif st.session_state.get('item2_base_desired', False):
        base_prob = 0.5
    
    prefix_prob = calculate_modifier_probability(prefixes_item1, prefixes_item2, desired_prefixes, not_desired_prefixes,
                                                  st.session_state.get('item1_base_desired', False), 
                                                  st.session_state.get('item2_base_desired', False))
    suffix_prob = calculate_modifier_probability(suffixes_item1, suffixes_item2, desired_suffixes, not_desired_suffixes,
                                                  st.session_state.get('item1_base_desired', False),
                                                  st.session_state.get('item2_base_desired', False))
    total_prob = base_prob * prefix_prob * suffix_prob
    return total_prob, None

# -----------------------
# Translations & Title
# -----------------------
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

# -----------------------
# Session init (only for keys this app uses)
# -----------------------
def ensure_keys():
    # item input keys
    for prefix in ['item1', 'item2']:
        for i in range(6):
            k_input = f'{prefix}_input_{i}'
            if k_input not in st.session_state:
                st.session_state[k_input] = ''
            k_type = f'{prefix}_type_{i}'
            if k_type not in st.session_state:
                st.session_state[k_type] = t['none']
            k_pref = f'{prefix}_pref_{i}'
            if k_pref not in st.session_state:
                st.session_state[k_pref] = t['not_desired']
    # base & paste toggles
    for k in ['item1_base_desired', 'item2_base_desired', 'show_paste_item1', 'show_paste_item2']:
        if k not in st.session_state:
            st.session_state[k] = False
    # paste areas
    if 'item1_paste_area' not in st.session_state:
        st.session_state['item1_paste_area'] = ''
    if 'item2_paste_area' not in st.session_state:
        st.session_state['item2_paste_area'] = ''
ensure_keys()

labels = ["Prefix 1", "Prefix 2", "Prefix 3", "Suffix 1", "Suffix 2", "Suffix 3"]

# -----------------------
# Layout: Two columns for items
# -----------------------
col1, col2 = st.columns(2)

# ITEM 1
with col1:
    st.markdown(f"<h3>{t['first_item']}</h3>", unsafe_allow_html=True)
    base_col, paste_col = st.columns([1, 1])
    # Make the base checkboxes exclusive and visually disabled for the other
    item1_base_selected = st.session_state.get('item1_base_desired', False)
    item2_base_selected = st.session_state.get('item2_base_desired', False)
    # Checkbox: disable if the other is selected
    with base_col:
        # We use a temporary variable and write back to session_state to ensure exclusivity
        new_item1_base = st.checkbox(t['desired_base'], key="item1_base_check", value=item1_base_selected, disabled=item2_base_selected)
        if new_item1_base and item2_base_selected:
            # if turned on, force other off
            st.session_state['item2_base_desired'] = False
        st.session_state['item1_base_desired'] = new_item1_base
    with paste_col:
        if st.button(t['paste_item'], key="paste_btn_item1"):
            st.session_state['show_paste_item1'] = not st.session_state.get('show_paste_item1', False)

    if st.session_state.get('show_paste_item1', False):
        # textarea binds to session state value so it persists
        st.session_state['item1_paste_area'] = st.text_area("Paste item text here:", key="item1_paste_area", value=st.session_state.get('item1_paste_area',''), height=150)
        if st.button("Parse", key="parse_item1"):
            prefixes, suffixes = parse_item_text(st.session_state['item1_paste_area'])
            for idx, prefix in enumerate(prefixes[:3]):
                st.session_state[f'item1_input_{idx}'] = prefix
            for idx, suffix in enumerate(suffixes[:3]):
                st.session_state[f'item1_input_{idx + 3}'] = suffix
            st.session_state['show_paste_item1'] = False
            st.experimental_rerun()

    # Render the 6 affix rows. Each row is wrapped in an element with class "input-group"
    for i in range(6):
        st.markdown('<div class="input-group">', unsafe_allow_html=True)
        input_col, type_col, pref_col = st.columns([2, 1, 1])
        with input_col:
            st.text_input(labels[i], key=f"item1_input_{i}", value=st.session_state.get(f'item1_input_{i}',''), label_visibility="visible")
        with type_col:
            st.selectbox("", [t['none'], t['exclusive'], t['non_native'], t['both']], key=f"item1_type_{i}", index=[t['none'], t['exclusive'], t['non_native'], t['both']].index(st.session_state.get(f'item1_type_{i}', t['none'])), label_visibility="collapsed")
        with pref_col:
            st.selectbox("", [t['doesnt_matter'], t['not_desired'], t['desired']], key=f"item1_pref_{i}", index=[t['doesnt_matter'], t['not_desired'], t['desired']].index(st.session_state.get(f'item1_pref_{i}', t['not_desired'])), label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

# ITEM 2
with col2:
    st.markdown(f"<h3>{t['second_item']}</h3>", unsafe_allow_html=True)
    base_col, paste_col = st.columns([1, 1])
    # Exclusive logic mirrored for item2
    # item2 checkbox disabled if item1 selected
    with base_col:
        new_item2_base = st.checkbox(t['desired_base'], key="item2_base_check", value=st.session_state.get('item2_base_desired', False), disabled=st.session_state.get('item1_base_desired', False))
        if new_item2_base and st.session_state.get('item1_base_desired', False):
            st.session_state['item1_base_desired'] = False
        st.session_state['item2_base_desired'] = new_item2_base
    with paste_col:
        if st.button(t['paste_item'], key="paste_btn_item2"):
            st.session_state['show_paste_item2'] = not st.session_state.get('show_paste_item2', False)

    if st.session_state.get('show_paste_item2', False):
        st.session_state['item2_paste_area'] = st.text_area("Paste item text here:", key="item2_paste_area", value=st.session_state.get('item2_paste_area',''), height=150)
        if st.button("Parse", key="parse_item2"):
            prefixes, suffixes = parse_item_text(st.session_state['item2_paste_area'])
            for idx, prefix in enumerate(prefixes[:3]):
                st.session_state[f'item2_input_{idx}'] = prefix
            for idx, suffix in enumerate(suffixes[:3]):
                st.session_state[f'item2_input_{idx + 3}'] = suffix
            st.session_state['show_paste_item2'] = False
            st.experimental_rerun()

    for i in range(6):
        st.markdown('<div class="input-group">', unsafe_allow_html=True)
        input_col, type_col, pref_col = st.columns([2, 1, 1])
        with input_col:
            st.text_input(labels[i], key=f"item2_input_{i}", value=st.session_state.get(f'item2_input_{i}',''), label_visibility="visible")
        with type_col:
            st.selectbox("", [t['none'], t['exclusive'], t['non_native'], t['both']], key=f"item2_type_{i}", index=[t['none'], t['exclusive'], t['non_native'], t['both']].index(st.session_state.get(f'item2_type_{i}', t['none'])), label_visibility="collapsed")
        with pref_col:
            st.selectbox("", [t['doesnt_matter'], t['not_desired'], t['desired']], key=f"item2_pref_{i}", index=[t['doesnt_matter'], t['not_desired'], t['desired']].index(st.session_state.get(f'item2_pref_{i}', t['not_desired'])), label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
# Buttons row (Calculate + Reset)
# -----------------------
st.write("")
col_calc, col_reset = st.columns([1, 1])

with col_calc:
    if st.button(t['calculate'], type="primary"):
        prob, error = calculate_combined_probability_from_widgets(t)
        if error:
            st.markdown(f'<div class="error-text">{error}</div>', unsafe_allow_html=True)
        elif prob is not None:
            st.markdown(f'<div class="result-text">{t["probability"]} {prob*100:.2f}%</div>', unsafe_allow_html=True)

# Reset behavior: clear all item-related keys (keep language selector)
def reset_to_fresh():
    prefixes = ['item1', 'item2']
    # keys to remove / reset (inputs, types, prefs, paste areas, base flags, show paste toggles)
    for p in prefixes:
        for i in range(6):
            k_input = f'{p}_input_{i}'
            if k_input in st.session_state:
                st.session_state[k_input] = ''
            k_type = f'{p}_type_{i}'
            if k_type in st.session_state:
                st.session_state[k_type] = t['none']
            k_pref = f'{p}_pref_{i}'
            if k_pref in st.session_state:
                st.session_state[k_pref] = t['not_desired']
    # paste areas and toggles
    for k in ['item1_paste_area', 'item2_paste_area', 'show_paste_item1', 'show_paste_item2']:
        st.session_state[k] = '' if 'paste_area' in k else False
    # base desired flags
    st.session_state['item1_base_desired'] = False
    st.session_state['item2_base_desired'] = False
    # also ensure the underlying checkbox widget values reflect that
    st.session_state['item1_base_check'] = False
    st.session_state['item2_base_check'] = False
    # after resetting, rerun to reflect cleared UI
    st.experimental_rerun()

with col_reset:
    if st.button(t['reset'], type="secondary"):
        reset_to_fresh()
