import streamlit as st
from math import comb

# -------------------------
# Page config & CSS
# -------------------------
st.set_page_config(page_title="Recombinator Calculator", layout="wide")

st.markdown("""
    <style>
    /* Streamlit widget styling */
    .stTextInput > div > div > input { height: 28px; padding: 2px 8px; font-size: 13px; }
    .stSelectbox > div > div { font-size: 13px; }
    .stSelectbox > div > div > div { padding: 4px; height: 28px; }
    .stSelectbox select { font-size: 13px; }
    div[data-testid="stVerticalBlock"] > div { padding-top: 0rem; padding-bottom: 0rem; }
    .main > div { padding-top: 0.5rem; }
    h1 { text-align: center; margin-bottom: 0.5rem; font-size: 24px; }
    h3 { margin-top: 0.2rem; margin-bottom: 0.2rem; font-size: 16px; }
    .stButton > button { width: 100%; padding: 4px; font-size: 13px; }
    .result-text { text-align: center; font-size: 18px; font-weight: bold; margin-top: 10px; color: #1f77b4; }
    .error-text { text-align: center; font-size: 16px; font-weight: bold; margin-top: 10px; color: #d62728; }

    /* Fix 1: CSS for the red border wrapper (mod-row) */
    .mod-row {
        border: 2px solid red;
        padding: 5px;
        border-radius: 5px;
        display: flex;
        gap: 10px;
        align-items: center;
        margin-bottom: 6px; /* Added to separate rows */
    }

    /* Fix 2: CSS for the tooltip */
    .tooltip-container {
        position: relative;
        display: inline-block;
        text-align: center;
    }
    .tooltip-icon {
        cursor: pointer;
        color: #007bff;
        margin-top: 2px;
        display: block;
        font-weight: bold; /* Make the '?' more visible */
        font-size: 12px;
    }
    .tooltip-text {
        visibility: hidden;
        width: 300px;
        background-color: #333;
        color: #fff;
        text-align: left;
        padding: 10px;
        border-radius: 5px;
        position: absolute;
        z-index: 10;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        opacity: 0;
        transition: opacity 0.3s;
    }
    .tooltip-container.show .tooltip-text {
        visibility: visible;
        opacity: 1;
    }
    /* Style for the selectbox in the tooltip container */
    .tooltip-container .stSelectbox {
        margin-bottom: 0; /* Remove default margin to place ? closer */
    }

    /* General label styling */
    label { font-size: 13px; }
    .stCheckbox label { font-size: 13px; }
    .stTextArea label { font-size: 13px; }
    .stCheckbox [disabled] { opacity: 0.6; }
    </style>
    
    <script>
    /* Fix 2: JavaScript function for toggling tooltip visibility */
    function showTooltip(elem) {
        const container = elem.parentElement;
        container.classList.toggle('show');
    }
    </script>
""", unsafe_allow_html=True)

# -------------------------
# Safe rerun helper
# -------------------------
def safe_rerun():
    """Call a rerun function if available, but avoid AttributeError in older/newer Streamlit builds."""
    if hasattr(st, "experimental_rerun"):
        try:
            st.experimental_rerun()
        except Exception:
            # fallback: try st.rerun if present
            if hasattr(st, "rerun"):
                try:
                    st.rerun()
                except Exception:
                    pass
    elif hasattr(st, "rerun"):
        try:
            st.rerun()
        except Exception:
            pass
    else:
        # no rerun available; do nothing (UI will update on next interaction)
        pass

# -------------------------
# Calculation functions (original logic preserved)
# -------------------------
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
    
    for desired in desired_mods:
        if desired not in selectable_mods:
            return 0.0
    
    if len(selectable_mods) < outcome_count:
        return 0.0
    
    if len(desired_mods) > outcome_count:
        return 0.0
    
    total_combinations = comb(len(selectable_mods), outcome_count)
    if total_combinations == 0: # Avoid division by zero
        return 0.0
        
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
        
        # Calculate selection probability for base 1 and base 2
        prob_base1 = calculate_selection_probability(all_mods_list, unique_mods, desired_mods, not_desired_mods, outcome_count, 1)
        prob_base2 = calculate_selection_probability(all_mods_list, unique_mods, desired_mods, not_desired_mods, outcome_count, 2)
        
        if item1_base_desired and item2_base_desired:
             # Should be caught by the base selection rule in the wrapper, but for completeness:
             selection_prob = 0.0
        elif item1_base_desired:
            selection_prob = prob_base1
        elif item2_base_desired:
            selection_prob = prob_base2
        else:
            # If neither is desired, equal chance of inheriting either base (0.5 * prob1 + 0.5 * prob2)
            selection_prob = (prob_base1 + prob_base2) / 2
        
        total_prob += count_prob * selection_prob
    
    return total_prob

def parse_item_text(item_text):
    """Parse item text and extract prefixes and suffixes"""
    lines = item_text.strip().split('\n')
    prefixes = []
    suffixes = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check if this is a prefix modifier line
        if 'Prefix Modifier' in line:
            # The actual mod is on the next line
            if i + 1 < len(lines):
                mod_line = lines[i + 1].strip()
                prefixes.append(mod_line)
        
        # Check if this is a suffix modifier line
        elif 'Suffix Modifier' in line:
            # The actual mod is on the next line
            if i + 1 < len(lines):
                mod_line = lines[i + 1].strip()
                suffixes.append(mod_line)
        
        i += 1
    
    return prefixes, suffixes

# -------------------------
# Calculation wrapper (reads widgets directly)
# -------------------------
def calculate_combined_probability():
    t = translations[st.session_state.get('language_selector', 'English')]
    
    prefixes_item1 = []
    prefixes_item2 = []
    suffixes_item1 = []
    suffixes_item2 = []
    
    desired_prefixes = set()
    desired_suffixes = set()
    not_desired_prefixes = set()
    not_desired_suffixes = set()
    
    exclusive_mods = []
    
    # Read widget-backed keys directly
    for i in range(6):
        mod_type = 'prefix' if i < 3 else 'suffix'
        
        # Item 1
        val1 = st.session_state.get(f'item1_input_{i}', '').strip()
        if val1:
            # Standardize type for checks
            type_val1 = st.session_state.get(f'item1_type_{i}', t['none'])
            is_exclusive = type_val1 in [t['exclusive'], 'Exclusive']
            is_non_native = type_val1 in [t['non_native'], 'Non-Native']
            
            mod_info = {
                'mod': val1,
                'non_native': is_non_native,
                'exclusive': is_exclusive,
                'item': 1
            }
            if mod_type == 'prefix':
                prefixes_item1.append(mod_info)
            else:
                suffixes_item1.append(mod_info)
            
            # Preference standardization
            preference = st.session_state.get(f'item1_pref_{i}', t['not_desired'])
            if preference == t['desired']:
                pref_standard = 'Desired'
            elif preference == t['not_desired']:
                pref_standard = 'Not Desired'
            else:
                pref_standard = "Doesn't Matter"
            
            if pref_standard == 'Desired':
                if mod_type == 'prefix':
                    desired_prefixes.add(val1)
                else:
                    desired_suffixes.add(val1)
            elif pref_standard == 'Not Desired':
                if mod_type == 'prefix':
                    not_desired_prefixes.add(val1)
                else:
                    not_desired_suffixes.add(val1)
            
            if is_exclusive:
                exclusive_mods.append((val1, pref_standard == 'Desired', mod_type, 1))
        
        # Item 2
        val2 = st.session_state.get(f'item2_input_{i}', '').strip()
        if val2:
            # Standardize type for checks
            type_val2 = st.session_state.get(f'item2_type_{i}', t['none'])
            is_exclusive = type_val2 in [t['exclusive'], 'Exclusive']
            is_non_native = type_val2 in [t['non_native'], 'Non-Native']
            
            mod_info = {
                'mod': val2,
                'non_native': is_non_native,
                'exclusive': is_exclusive,
                'item': 2
            }
            if mod_type == 'prefix':
                prefixes_item2.append(mod_info)
            else:
                suffixes_item2.append(mod_info)
            
            # Preference standardization
            preference = st.session_state.get(f'item2_pref_{i}', t['not_desired'])
            if preference == t['desired']:
                pref_standard = 'Desired'
            elif preference == t['not_desired']:
                pref_standard = 'Not Desired'
            else:
                pref_standard = "Doesn't Matter"
            
            if pref_standard == 'Desired':
                if mod_type == 'prefix':
                    desired_prefixes.add(val2)
                else:
                    desired_suffixes.add(val2)
            elif pref_standard == 'Not Desired':
                if mod_type == 'prefix':
                    not_desired_prefixes.add(val2)
                else:
                    not_desired_suffixes.add(val2)
            
            if is_exclusive:
                exclusive_mods.append((val2, pref_standard == 'Desired', mod_type, 2))
    
    # If user picked no desired modifiers on either item, prompt them
    if len(desired_prefixes) == 0 and len(desired_suffixes) == 0:
        return None, "Please pick at least 1 desired modifier"
    
    # Exclusive-mod rules (unchanged)
    if len(exclusive_mods) > 1:
        if len(exclusive_mods) == 2:
            ex1, ex2 = exclusive_mods
            if (ex1[2] == 'prefix' and ex2[2] == 'suffix' and ex1[1] and not ex2[1]) or \
               (ex2[2] == 'prefix' and ex1[2] == 'suffix' and ex2[1] and not ex1[1]):
                return 0.5, None
        return None, t['error_exclusive']
    
    # Base selection rules
    base_prob = 1.0
    item1_base_desired = st.session_state.get('item1_base_desired', False)
    item2_base_desired = st.session_state.get('item2_base_desired', False)
    
    if item1_base_desired and item2_base_desired:
        return None, t['error_both_bases']
    elif item1_base_desired or item2_base_desired:
        # If one is desired, the overall base probability is 50%
        base_prob = 0.5
    
    # Calculate prefix and suffix probabilities using original helper
    prefix_prob = calculate_modifier_probability(prefixes_item1, prefixes_item2, desired_prefixes, not_desired_prefixes,
                                                 item1_base_desired, 
                                                 item2_base_desired)
    
    suffix_prob = calculate_modifier_probability(suffixes_item1, suffixes_item2, desired_suffixes, not_desired_suffixes,
                                                 item1_base_desired,
                                                 item2_base_desired)
    
    total_prob = base_prob * prefix_prob * suffix_prob
    
    return total_prob, None

# -------------------------
# UI: Translations, labels, init defaults
# -------------------------
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
        "paste_item": "Paste Item",
        "tooltip_pref": "Desired modifiers are modifiers that you want on your final item,\nNot desired modifiers are modifiers that you do not want on your final item,\nDoesn't matter means you don't care if that item appears on the final item or not.",
        "tooltip_type": "Exclusive mods: cannot appear with other exclusive mods.\nNon-Native mods: only appear if their original base is selected (or if neither base is desired)."
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
        "paste_item": "Item Yapıştır",
        "tooltip_pref": "İstiyorum: Son itemde olmasını istediğiniz modifierlar.\nİstemiyorum: Son itemde olmamasını istediğiniz modifierlar.\nFarketmez: Son itemde olup olmaması umurunuzda değil.",
        "tooltip_type": "Exclusive modlar: Başka exclusive modlarla birlikte gelemezler.\nNon-Native modlar: Yalnızca kendi orijinal base'i seçilirse (veya iki base de istenmezse) gelebilirler."
    }
}

t = translations[language]
st.markdown(f"<h1>{t['title']}</h1>", unsafe_allow_html=True)

labels = ["Prefix 1", "Prefix 2", "Prefix 3", "Suffix 1", "Suffix 2", "Suffix 3"]

# Initialize widget-backed keys with safe defaults
for i in range(6):
    if f'item1_input_{i}' not in st.session_state:
        st.session_state[f'item1_input_{i}'] = ''
    if f'item2_input_{i}' not in st.session_state:
        st.session_state[f'item2_input_{i}'] = ''
    if f'item1_type_{i}' not in st.session_state:
        st.session_state[f'item1_type_{i}'] = t['none']
    if f'item2_type_{i}' not in st.session_state:
        st.session_state[f'item2_type_{i}'] = t['none']
    if f'item1_pref_{i}' not in st.session_state:
        st.session_state[f'item1_pref_{i}'] = t['not_desired']
    if f'item2_pref_{i}' not in st.session_state:
        st.session_state[f'item2_pref_{i}'] = t['not_desired']

# Paste area keys
if 'item1_paste_area' not in st.session_state:
    st.session_state['item1_paste_area'] = ''
if 'item2_paste_area' not in st.session_state:
    st.session_state['item2_paste_area'] = ''

# Base flags
if 'item1_base_desired' not in st.session_state:
    st.session_state['item1_base_desired'] = False
if 'item2_base_desired' not in st.session_state:
    st.session_state['item2_base_desired'] = False

# Show paste toggles
if 'show_paste_item1' not in st.session_state:
    st.session_state['show_paste_item1'] = False
if 'show_paste_item2' not in st.session_state:
    st.session_state['show_paste_item2'] = False

# -------------------------
# Layout: two item columns
# -------------------------
col1, col2 = st.columns(2)

# --- ITEM 1 ---
with col1:
    st.markdown(f"<h3>{t['first_item']}</h3>", unsafe_allow_html=True)
    base_col, paste_col = st.columns([1, 1])

    with base_col:
        item1_base = st.checkbox(t['desired_base'], key="item1_base_check", value=st.session_state.get('item1_base_desired', False), disabled=st.session_state.get('item2_base_desired', False))
        st.session_state['item1_base_desired'] = item1_base
        # The disabled state handles the check, but ensure session state is consistent on init/rerun
        if item1_base and st.session_state.get('item2_base_desired', False):
            st.session_state['item2_base_desired'] = False

    with paste_col:
        if st.button(t['paste_item'], key="paste_btn_item1"):
            st.session_state['show_paste_item1'] = not st.session_state.get('show_paste_item1', False)

    if st.session_state.get('show_paste_item1', False):
        st.text_area(t["paste_item"] + " " + t["first_item"] + " " + "text here:", key="item1_paste_area", value=st.session_state.get('item1_paste_area',''), height=150)
        if st.button("Parse", key="parse_item1"):
            item_text = st.session_state.get('item1_paste_area', '')
            prefixes, suffixes = parse_item_text(item_text)
            # fill inputs directly (widget-backed keys)
            for idx in range(6):
                st.session_state[f'item1_input_{idx}'] = ''
            for idx, prefix in enumerate(prefixes[:3]):
                st.session_state[f'item1_input_{idx}'] = prefix
            for idx, suffix in enumerate(suffixes[:3]):
                st.session_state[f'item1_input_{idx + 3}'] = suffix
            st.session_state['show_paste_item1'] = False
            safe_rerun()

    # Render each affix row with Fix 1 (mod-row wrapper) and Fix 2/3 (tooltips/fallback)
    for i in range(6):
        # Fix 1: Wrap the input group in the mod-row div
        st.markdown('<div class="mod-row">', unsafe_allow_html=True) 
        input_col, type_col, pref_col = st.columns([2, 1, 1])

        with input_col:
            st.text_input(labels[i], key=f'item1_input_{i}', value=st.session_state.get(f'item1_input_{i}',''), label_visibility="visible")

        # Modifier Type Dropdown (with tooltip)
        with type_col:
            st.markdown('<div class="tooltip-container">', unsafe_allow_html=True)
            st.selectbox("", [t['none'], t['exclusive'], t['non_native'], t['both']], key=f'item1_type_{i}', label_visibility="collapsed")
            st.markdown(f'''
                <span class="tooltip-icon" onclick="showTooltip(this)">?</span>
                <div class="tooltip-text">{t['tooltip_type'].replace('\n', '<br>')}</div>
            </div>''', unsafe_allow_html=True)

        # Preference Dropdown (with tooltip and Fix 3: Turkish/Fallback fix)
        with pref_col:
            st.markdown('<div class="tooltip-container">', unsafe_allow_html=True)
            
            # Fix 3: Use a fallback index to prevent ValueError if session state is corrupted
            options = [t['doesnt_matter'], t['not_desired'], t['desired']]
            value = st.session_state.get(f'item1_pref_{i}', t['not_desired'])
            try:
                idx = options.index(value)
            except ValueError:
                idx = 1 # default to 'Not Desired' (t['not_desired'] is index 1)
            
            st.selectbox("", options, key=f'item1_pref_{i}', index=idx, label_visibility="collapsed")
            
            st.markdown(f'''
                <span class="tooltip-icon" onclick="showTooltip(this)">?</span>
                <div class="tooltip-text">{t['tooltip_pref'].replace('\n', '<br>')}</div>
            </div>''', unsafe_allow_html=True)

        # Close Fix 1 wrapper
        st.markdown('</div>', unsafe_allow_html=True) 

# --- ITEM 2 ---
with col2:
    st.markdown(f"<h3>{t['second_item']}</h3>", unsafe_allow_html=True)
    base_col, paste_col = st.columns([1, 1])

    with base_col:
        item2_base = st.checkbox(t['desired_base'], key="item2_base_check", value=st.session_state.get('item2_base_desired', False), disabled=st.session_state.get('item1_base_desired', False))
        st.session_state['item2_base_desired'] = item2_base
        if item2_base and st.session_state.get('item1_base_desired', False):
            st.session_state['item1_base_desired'] = False

    with paste_col:
        if st.button(t['paste_item'], key="paste_btn_item2"):
            st.session_state['show_paste_item2'] = not st.session_state.get('show_paste_item2', False)

    if st.session_state.get('show_paste_item2', False):
        st.text_area(t["paste_item"] + " " + t["second_item"] + " " + "text here:", key="item2_paste_area", value=st.session_state.get('item2_paste_area',''), height=150)
        if st.button("Parse", key="parse_item2"):
            item_text = st.session_state.get('item2_paste_area', '')
            prefixes, suffixes = parse_item_text(item_text)
            for idx in range(6):
                st.session_state[f'item2_input_{idx}'] = ''
            for idx, prefix in enumerate(prefixes[:3]):
                st.session_state[f'item2_input_{idx}'] = prefix
            for idx, suffix in enumerate(suffixes[:3]):
                st.session_state[f'item2_input_{idx + 3}'] = suffix
            st.session_state['show_paste_item2'] = False
            safe_rerun()

    for i in range(6):
        # Fix 1: Wrap the input group in the mod-row div
        st.markdown('<div class="mod-row">', unsafe_allow_html=True) 
        input_col, type_col, pref_col = st.columns([2, 1, 1])
        
        with input_col:
            st.text_input(labels[i], key=f'item2_input_{i}', value=st.session_state.get(f'item2_input_{i}',''), label_visibility="visible")
        
        # Modifier Type Dropdown (with tooltip)
        with type_col:
            st.markdown('<div class="tooltip-container">', unsafe_allow_html=True)
            st.selectbox("", [t['none'], t['exclusive'], t['non_native'], t['both']], key=f'item2_type_{i}', label_visibility="collapsed")
            st.markdown(f'''
                <span class="tooltip-icon" onclick="showTooltip(this)">?</span>
                <div class="tooltip-text">{t['tooltip_type'].replace('\n', '<br>')}</div>
            </div>''', unsafe_allow_html=True)
        
        # Preference Dropdown (with tooltip and Fix 3: Turkish/Fallback fix)
        with pref_col:
            st.markdown('<div class="tooltip-container">', unsafe_allow_html=True)
            
            # Fix 3: Use a fallback index to prevent ValueError if session state is corrupted
            options = [t['doesnt_matter'], t['not_desired'], t['desired']]
            value = st.session_state.get(f'item2_pref_{i}', t['not_desired'])
            try:
                idx = options.index(value)
            except ValueError:
                idx = 1 # default to 'Not Desired' (t['not_desired'] is index 1)
                
            st.selectbox("", options, key=f'item2_pref_{i}', index=idx, label_visibility="collapsed")
            
            st.markdown(f'''
                <span class="tooltip-icon" onclick="showTooltip(this)">?</span>
                <div class="tooltip-text">{t['tooltip_pref'].replace('\n', '<br>')}</div>
            </div>''', unsafe_allow_html=True)

        # Close Fix 1 wrapper
        st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# Buttons: Calculate and Reset
# -------------------------
st.write("")
col_calc, col_reset = st.columns([1, 1])

with col_calc:
    if st.button(t['calculate'], type="primary"):
        prob, error = calculate_combined_probability()
        if error:
            st.markdown(f'<div class="error-text">{error}</div>', unsafe_allow_html=True)
        elif prob is not None:
            st.markdown(f'<div class="result-text">{t["probability"]} {prob*100:.2f}%</div>', unsafe_allow_html=True)

# Reset: clear everything except language selection, safe & deterministic
def reset_preserve_language():
    # Save the current language and translations for re-initialization
    saved_lang = st.session_state.get('language_selector', 'English')
    current_t = translations[saved_lang]
    
    st.session_state.clear()
    
    # restore language and minimal defaults so UI can render
    st.session_state['language_selector'] = saved_lang
    st.session_state['item1_base_desired'] = False
    st.session_state['item2_base_desired'] = False
    st.session_state['show_paste_item1'] = False
    st.session_state['show_paste_item2'] = False
    st.session_state['item1_paste_area'] = ''
    st.session_state['item2_paste_area'] = ''
    
    # initialize all input/type/pref keys so subsequent code can use them reliably
    for i in range(6):
        st.session_state[f'item1_input_{i}'] = ''
        st.session_state[f'item2_input_{i}'] = ''
        st.session_state[f'item1_type_{i}'] = current_t['none']
        st.session_state[f'item2_type_{i}'] = current_t['none']
        st.session_state[f'item1_pref_{i}'] = current_t['not_desired']
        st.session_state[f'item2_pref_{i}'] = current_t['not_desired']
        
    safe_rerun()

with col_reset:
    if st.button(t['reset'], type="secondary"):
        reset_preserve_language()