import streamlit as st
from math import comb

# Set page configuration
st.set_page_config(page_title="Recombinator Calculator", layout="wide")

# Custom CSS for compact UI
st.markdown("""
    <style>
    .stTextInput > div > div > input {
        height: 25px;
        padding: 1px 6px;
        font-size: 12px;
    }
    .stSelectbox > div > div {
        font-size: 11px;
    }
    .stSelectbox > div > div > div {
        padding: 2px;
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
    .input-group {
        border: 2px solid #dc3545;
        padding: 4px;
        margin-bottom: 3px;
        border-radius: 4px;
    }
    label {
        font-size: 12px;
    }
    .stCheckbox label {
        font-size: 11px;
    }
    </style>
    """, unsafe_allow_html=True)

# Calculation functions
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
            
            if item1_base_desired:
                selection_prob = prob_base1
            else:
                selection_prob = prob_base2
        else:
            prob_base1 = calculate_selection_probability(all_mods_list, unique_mods, desired_mods, not_desired_mods, outcome_count, 1)
            prob_base2 = calculate_selection_probability(all_mods_list, unique_mods, desired_mods, not_desired_mods, outcome_count, 2)
            selection_prob = (prob_base1 + prob_base2) / 2
        
        total_prob += count_prob * selection_prob
    
    return total_prob

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
    
    for i in range(6):
        mod_type = 'prefix' if i < 3 else 'suffix'
        
        # Item 1
        if st.session_state['item1_inputs'][i]:
            mod_type_option = st.session_state.get(f'item1_type_{i}', 'None')
            is_exclusive = mod_type_option in ['Exclusive', 'Both']
            is_non_native = mod_type_option in ['Non-Native', 'Both']
            
            mod_info = {
                'mod': st.session_state['item1_inputs'][i],
                'non_native': is_non_native,
                'exclusive': is_exclusive,
                'item': 1
            }
            
            if mod_type == 'prefix':
                prefixes_item1.append(mod_info)
            else:
                suffixes_item1.append(mod_info)
            
            preference = st.session_state.get(f'item1_pref_{i}', "Doesn't Matter")
            if preference == 'Desired':
                if mod_type == 'prefix':
                    desired_prefixes.add(st.session_state['item1_inputs'][i])
                else:
                    desired_suffixes.add(st.session_state['item1_inputs'][i])
            elif preference == 'Not Desired':
                if mod_type == 'prefix':
                    not_desired_prefixes.add(st.session_state['item1_inputs'][i])
                else:
                    not_desired_suffixes.add(st.session_state['item1_inputs'][i])
            
            if is_exclusive:
                exclusive_mods.append((st.session_state['item1_inputs'][i], 
                                     preference == 'Desired',
                                     mod_type, 1))
        
        # Item 2
        if st.session_state['item2_inputs'][i]:
            mod_type_option = st.session_state.get(f'item2_type_{i}', 'None')
            is_exclusive = mod_type_option in ['Exclusive', 'Both']
            is_non_native = mod_type_option in ['Non-Native', 'Both']
            
            mod_info = {
                'mod': st.session_state['item2_inputs'][i],
                'non_native': is_non_native,
                'exclusive': is_exclusive,
                'item': 2
            }
            
            if mod_type == 'prefix':
                prefixes_item2.append(mod_info)
            else:
                suffixes_item2.append(mod_info)
            
            preference = st.session_state.get(f'item2_pref_{i}', "Doesn't Matter")
            if preference == 'Desired':
                if mod_type == 'prefix':
                    desired_prefixes.add(st.session_state['item2_inputs'][i])
                else:
                    desired_suffixes.add(st.session_state['item2_inputs'][i])
            elif preference == 'Not Desired':
                if mod_type == 'prefix':
                    not_desired_prefixes.add(st.session_state['item2_inputs'][i])
                else:
                    not_desired_suffixes.add(st.session_state['item2_inputs'][i])
            
            if is_exclusive:
                exclusive_mods.append((st.session_state['item2_inputs'][i],
                                     preference == 'Desired',
                                     mod_type, 2))
    
    if len(exclusive_mods) > 1:
        if len(exclusive_mods) == 2:
            ex1, ex2 = exclusive_mods
            if (ex1[2] == 'prefix' and ex2[2] == 'suffix' and ex1[1] and not ex2[1]) or \
               (ex2[2] == 'prefix' and ex1[2] == 'suffix' and ex2[1] and not ex1[1]):
                return 0.5, None
        return None, t['error_exclusive']
    
    base_prob = 1.0
    if st.session_state['item1_base_desired'] and st.session_state['item2_base_desired']:
        return None, t['error_both_bases']
    elif st.session_state['item1_base_desired']:
        base_prob = 0.5
    elif st.session_state['item2_base_desired']:
        base_prob = 0.5
    
    prefix_prob = calculate_modifier_probability(prefixes_item1, prefixes_item2, desired_prefixes, not_desired_prefixes,
                                                  st.session_state['item1_base_desired'], 
                                                  st.session_state['item2_base_desired'])
    
    suffix_prob = calculate_modifier_probability(suffixes_item1, suffixes_item2, desired_suffixes, not_desired_suffixes,
                                                  st.session_state['item1_base_desired'],
                                                  st.session_state['item2_base_desired'])
    
    total_prob = base_prob * prefix_prob * suffix_prob
    
    return total_prob, None

# Language picker
col_lang, col_space = st.columns([1, 5])
with col_lang:
    language = st.selectbox("", ["English", "Turkish"], key="language_selector", label_visibility="collapsed")

# Translations
translations = {
    "English": {
        "title": "Recombinator Calculator",
        "first_item": "First Item",
        "second_item": "Second Item",
        "desired_base": "Desired Base",
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
        "doesnt_matter": "Doesn't Matter"
    },
    "Turkish": {
        "title": "Recombinator Hesaplayıcısı",
        "first_item": "İlk Item",
        "second_item": "İkinci Item",
        "desired_base": "İstediğiniz Base",
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
        "doesnt_matter": "Farketmez"
    }
}

t = translations[language]

st.markdown(f"<h1>{t['title']}</h1>", unsafe_allow_html=True)

# Initialize session state
for key in ['item1_inputs', 'item2_inputs']:
    if key not in st.session_state:
        st.session_state[key] = [''] * 6
for key in ['item1_base_desired', 'item2_base_desired']:
    if key not in st.session_state:
        st.session_state[key] = False

labels = ["Prefix 1", "Prefix 2", "Prefix 3", "Suffix 1", "Suffix 2", "Suffix 3"]

# Create two columns for items
col1, col2 = st.columns(2)

# First Item
with col1:
    st.markdown(f"<h3>{t['first_item']}</h3>", unsafe_allow_html=True)
    st.session_state['item1_base_desired'] = st.checkbox(t['desired_base'], key="item1_base_check")
    
    for i in range(6):
        st.markdown('<div class="input-group">', unsafe_allow_html=True)
        
        input_col, type_col, pref_col = st.columns([2, 1, 1])
        
        with input_col:
            input_value = st.text_input(labels[i], key=f"item1_input_{i}", label_visibility="visible")
            st.session_state['item1_inputs'][i] = input_value.lower().strip() if input_value else ''
        
        with type_col:
            st.selectbox("Type", [t['none'], t['exclusive'], t['non_native'], t['both']], 
                        key=f"item1_type_{i}", label_visibility="collapsed")
        
        with pref_col:
            st.selectbox("Pref", [t['doesnt_matter'], t['desired'], t['not_desired']], 
                        key=f"item1_pref_{i}", label_visibility="collapsed")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Second Item
with col2:
    st.markdown(f"<h3>{t['second_item']}</h3>", unsafe_allow_html=True)
    st.session_state['item2_base_desired'] = st.checkbox(t['desired_base'], key="item2_base_check")
    
    for i in range(6):
        st.markdown('<div class="input-group">', unsafe_allow_html=True)
        
        input_col, type_col, pref_col = st.columns([2, 1, 1])
        
        with input_col:
            input_value = st.text_input(labels[i], key=f"item2_input_{i}", label_visibility="visible")
            st.session_state['item2_inputs'][i] = input_value.lower().strip() if input_value else ''
        
        with type_col:
            st.selectbox("Type", [t['none'], t['exclusive'], t['non_native'], t['both']], 
                        key=f"item2_type_{i}", label_visibility="collapsed")
        
        with pref_col:
            st.selectbox("Pref", [t['doesnt_matter'], t['desired'], t['not_desired']], 
                        key=f"item2_pref_{i}", label_visibility="collapsed")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Calculate and Reset buttons
st.write("")
col_calc, col_reset = st.columns([1, 1])

with col_calc:
    if st.button(t['calculate'], type="primary"):
        prob, error = calculate_combined_probability()
        
        if error:
            st.markdown(f'<div class="error-text">{error}</div>', unsafe_allow_html=True)
        elif prob is not None:
            st.markdown(f'<div class="result-text">{t["probability"]} {prob*100:.2f}%</div>', 
                       unsafe_allow_html=True)

with col_reset:
    if st.button(t['reset'], type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()