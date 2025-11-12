import streamlit as st
from math import comb

# Set page configuration
st.set_page_config(page_title="Recombinator Calculator", layout="wide")

# Custom CSS for compact UI and red boxes
st.markdown("""
    <style>
    .stTextInput > div > div > input {
        height: 30px;
        padding: 2px 8px;
    }
    .stCheckbox {
        margin-top: 0px;
        margin-bottom: 0px;
    }
    div[data-testid="stVerticalBlock"] > div {
        padding-top: 0.1rem;
        padding-bottom: 0.1rem;
    }
    .main > div {
        padding-top: 1rem;
    }
    h1 {
        text-align: center;
        margin-bottom: 1rem;
    }
    h3 {
        margin-top: 0.2rem;
        margin-bottom: 0.3rem;
    }
    .stButton > button {
        width: 100%;
    }
    .result-text {
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        margin-top: 20px;
        color: #1f77b4;
    }
    .error-text {
        text-align: center;
        font-size: 20px;
        font-weight: bold;
        margin-top: 20px;
        color: #d62728;
    }
    .input-group {
        border: 2px solid #dc3545;
        padding: 8px;
        margin-bottom: 5px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# Calculation functions (defined at the top)
def get_count_probabilities(count):
    """Returns probability distribution for getting X modifiers given total count"""
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
    """Calculate probability of getting desired mods and avoiding not desired mods"""
    
    # Filter available mods based on non-native restrictions
    available_mods = []
    for mod_info in all_mods_list:
        if mod_info['non_native'] and mod_info['item'] != winning_base:
            continue
        available_mods.append(mod_info['mod'])
    
    available_unique = list(set(available_mods))
    
    # Check if all desired mods are available
    for desired in desired_mods:
        if desired not in available_unique:
            return 0.0
    
    # Remove not desired mods from available pool
    selectable_mods = [m for m in available_unique if m not in not_desired_mods]
    
    # Check if we can still get all desired mods
    for desired in desired_mods:
        if desired not in selectable_mods:
            return 0.0
    
    if len(selectable_mods) < outcome_count:
        return 0.0
    
    if len(desired_mods) > outcome_count:
        return 0.0
    
    # Calculate combinations
    total_combinations = comb(len(selectable_mods), outcome_count)
    remaining_slots = outcome_count - len(desired_mods)
    non_desired_selectable = [m for m in selectable_mods if m not in desired_mods]
    
    if remaining_slots > len(non_desired_selectable):
        return 0.0
    
    favorable_combinations = comb(len(non_desired_selectable), remaining_slots)
    
    return favorable_combinations / total_combinations

def calculate_modifier_probability(mods_item1, mods_item2, desired_mods, not_desired_mods, item1_base_desired, item2_base_desired):
    """Calculate probability for prefixes or suffixes including not desired mods"""
    
    if len(desired_mods) == 0 and len(not_desired_mods) == 0:
        return 1.0
    
    # Combine all modifiers
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
    """Calculate probability of getting desired modifiers and avoiding not desired ones"""
    
    # Collect modifier data
    prefixes_item1 = []
    prefixes_item2 = []
    suffixes_item1 = []
    suffixes_item2 = []
    
    desired_prefixes = set()
    desired_suffixes = set()
    not_desired_prefixes = set()
    not_desired_suffixes = set()
    
    # Check for exclusive modifier violations
    exclusive_mods = []
    
    for i in range(6):
        mod_type = 'prefix' if i < 3 else 'suffix'
        
        # Item 1
        if st.session_state['item1_inputs'][i]:
            mod_info = {
                'mod': st.session_state['item1_inputs'][i],
                'non_native': st.session_state['item1_non_native'][i],
                'exclusive': st.session_state['item1_exclusive'][i],
                'item': 1
            }
            
            if mod_type == 'prefix':
                prefixes_item1.append(mod_info)
                if st.session_state['affix_preferences'].get(st.session_state['item1_inputs'][i]) == 'desired':
                    desired_prefixes.add(st.session_state['item1_inputs'][i])
                elif st.session_state['affix_preferences'].get(st.session_state['item1_inputs'][i]) == 'not_desired':
                    not_desired_prefixes.add(st.session_state['item1_inputs'][i])
            else:
                suffixes_item1.append(mod_info)
                if st.session_state['affix_preferences'].get(st.session_state['item1_inputs'][i]) == 'desired':
                    desired_suffixes.add(st.session_state['item1_inputs'][i])
                elif st.session_state['affix_preferences'].get(st.session_state['item1_inputs'][i]) == 'not_desired':
                    not_desired_suffixes.add(st.session_state['item1_inputs'][i])
            
            if st.session_state['item1_exclusive'][i]:
                exclusive_mods.append((st.session_state['item1_inputs'][i], 
                                     st.session_state['affix_preferences'].get(st.session_state['item1_inputs'][i]) == 'desired',
                                     mod_type, 1))
        
        # Item 2
        if st.session_state['item2_inputs'][i]:
            mod_info = {
                'mod': st.session_state['item2_inputs'][i],
                'non_native': st.session_state['item2_non_native'][i],
                'exclusive': st.session_state['item2_exclusive'][i],
                'item': 2
            }
            
            if mod_type == 'prefix':
                prefixes_item2.append(mod_info)
                if st.session_state['affix_preferences'].get(st.session_state['item2_inputs'][i]) == 'desired':
                    desired_prefixes.add(st.session_state['item2_inputs'][i])
                elif st.session_state['affix_preferences'].get(st.session_state['item2_inputs'][i]) == 'not_desired':
                    not_desired_prefixes.add(st.session_state['item2_inputs'][i])
            else:
                suffixes_item2.append(mod_info)
                if st.session_state['affix_preferences'].get(st.session_state['item2_inputs'][i]) == 'desired':
                    desired_suffixes.add(st.session_state['item2_inputs'][i])
                elif st.session_state['affix_preferences'].get(st.session_state['item2_inputs'][i]) == 'not_desired':
                    not_desired_suffixes.add(st.session_state['item2_inputs'][i])
            
            if st.session_state['item2_exclusive'][i]:
                exclusive_mods.append((st.session_state['item2_inputs'][i],
                                     st.session_state['affix_preferences'].get(st.session_state['item2_inputs'][i]) == 'desired',
                                     mod_type, 2))
    
    # Check exclusive modifier rules
    if len(exclusive_mods) > 1:
        if len(exclusive_mods) == 2:
            ex1, ex2 = exclusive_mods
            if (ex1[2] == 'prefix' and ex2[2] == 'suffix' and ex1[1] and not ex2[1]) or \
               (ex2[2] == 'prefix' and ex1[2] == 'suffix' and ex2[1] and not ex1[1]):
                return 0.5, None
        return None, "There can only be 1 exclusive modifier on an item"
    
    # Calculate base probability
    base_prob = 1.0
    if st.session_state['item1_base_desired'] and st.session_state['item2_base_desired']:
        return None, "Cannot select both bases as desired"
    elif st.session_state['item1_base_desired']:
        base_prob = 0.5
    elif st.session_state['item2_base_desired']:
        base_prob = 0.5
    
    # Calculate prefix probability
    prefix_prob = calculate_modifier_probability(prefixes_item1, prefixes_item2, desired_prefixes, not_desired_prefixes,
                                                  st.session_state['item1_base_desired'], 
                                                  st.session_state['item2_base_desired'])
    
    # Calculate suffix probability
    suffix_prob = calculate_modifier_probability(suffixes_item1, suffixes_item2, desired_suffixes, not_desired_suffixes,
                                                  st.session_state['item1_base_desired'],
                                                  st.session_state['item2_base_desired'])
    
    # Combine probabilities
    total_prob = base_prob * prefix_prob * suffix_prob
    
    return total_prob, None

# Title
st.markdown("<h1>Recombinator Calculator</h1>", unsafe_allow_html=True)

# Initialize session state
for key in ['item1_inputs', 'item2_inputs']:
    if key not in st.session_state:
        st.session_state[key] = [''] * 6
for key in ['item1_non_native', 'item1_exclusive', 'item2_non_native', 'item2_exclusive']:
    if key not in st.session_state:
        st.session_state[key] = [False] * 6
for key in ['item1_base_desired', 'item2_base_desired', 'show_affixes']:
    if key not in st.session_state:
        st.session_state[key] = False
if 'possible_affixes' not in st.session_state:
    st.session_state['possible_affixes'] = {'prefixes': [], 'suffixes': []}
if 'affix_preferences' not in st.session_state:
    st.session_state['affix_preferences'] = {}

# Labels for inputs
labels = ["Prefix 1", "Prefix 2", "Prefix 3", "Suffix 1", "Suffix 2", "Suffix 3"]

# Phase 1: Input modifiers (always shown)
# Create two columns for items
col1, col2 = st.columns(2)
    
# First Item
with col1:
    st.subheader("First Item")
    st.session_state['item1_base_desired'] = st.checkbox("Desired Base", key="item1_base_check")
    
    for i in range(6):
        st.markdown('<div class="input-group">', unsafe_allow_html=True)
        check_col, input_col = st.columns([1, 2])
        
        with check_col:
            st.session_state['item1_non_native'][i] = st.checkbox("Non-Native", key=f"item1_non_native_{i}")
            st.session_state['item1_exclusive'][i] = st.checkbox("Exclusive", key=f"item1_exclusive_{i}")
        
        with input_col:
            input_value = st.text_input(labels[i], key=f"item1_input_{i}", label_visibility="visible")
            st.session_state['item1_inputs'][i] = input_value.lower().strip() if input_value else ''
        
        st.markdown('</div>', unsafe_allow_html=True)

# Second Item
with col2:
    st.subheader("Second Item")
    st.session_state['item2_base_desired'] = st.checkbox("Desired Base", key="item2_base_check")
    
    for i in range(6):
        st.markdown('<div class="input-group">', unsafe_allow_html=True)
        input_col, check_col = st.columns([2, 1])
        
        with input_col:
            input_value = st.text_input(labels[i], key=f"item2_input_{i}", label_visibility="visible")
            st.session_state['item2_inputs'][i] = input_value.lower().strip() if input_value else ''
        
        with check_col:
            st.session_state['item2_non_native'][i] = st.checkbox("Non-Native", key=f"item2_non_native_{i}")
            st.session_state['item2_exclusive'][i] = st.checkbox("Exclusive", key=f"item2_exclusive_{i}")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Pick desired affixes button
st.write("")
col_left, col_center, col_right = st.columns([1, 1, 1])
with col_center:
    if st.button("Pick Desired Affixes", type="primary"):
        # Collect all possible affixes
        all_prefixes = set()
        all_suffixes = set()
        
        for i in range(3):
            if st.session_state['item1_inputs'][i]:
                all_prefixes.add(st.session_state['item1_inputs'][i])
            if st.session_state['item2_inputs'][i]:
                all_prefixes.add(st.session_state['item2_inputs'][i])
        
        for i in range(3, 6):
            if st.session_state['item1_inputs'][i]:
                all_suffixes.add(st.session_state['item1_inputs'][i])
            if st.session_state['item2_inputs'][i]:
                all_suffixes.add(st.session_state['item2_inputs'][i])
        
        st.session_state['possible_affixes'] = {
            'prefixes': sorted(list(all_prefixes)),
            'suffixes': sorted(list(all_suffixes))
        }
        
        # Initialize preferences if not set
        for prefix in st.session_state['possible_affixes']['prefixes']:
            if prefix not in st.session_state['affix_preferences']:
                st.session_state['affix_preferences'][prefix] = 'none'
        for suffix in st.session_state['possible_affixes']['suffixes']:
            if suffix not in st.session_state['affix_preferences']:
                st.session_state['affix_preferences'][suffix] = 'none'
        
        st.session_state['show_affixes'] = True
        st.rerun()

# Phase 2: Select desired/not desired affixes and calculate (shown below Phase 1 when active)
if st.session_state['show_affixes']:
    st.subheader("Select Desired and Not Desired Modifiers")
    
    error_found = False
    
    # Show prefixes
    if st.session_state['possible_affixes']['prefixes']:
        st.write("**Prefixes:**")
        for prefix in st.session_state['possible_affixes']['prefixes']:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(prefix)
            with col2:
                desired = st.checkbox("Desired", key=f"desired_{prefix}")
            with col3:
                not_desired = st.checkbox("Not Desired", key=f"not_desired_{prefix}")
            
            if desired and not_desired:
                error_found = True
            elif desired:
                st.session_state['affix_preferences'][prefix] = 'desired'
            elif not_desired:
                st.session_state['affix_preferences'][prefix] = 'not_desired'
            else:
                st.session_state['affix_preferences'][prefix] = 'none'
    
    # Show suffixes
    if st.session_state['possible_affixes']['suffixes']:
        st.write("**Suffixes:**")
        for suffix in st.session_state['possible_affixes']['suffixes']:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(suffix)
            with col2:
                desired = st.checkbox("Desired", key=f"desired_{suffix}")
            with col3:
                not_desired = st.checkbox("Not Desired", key=f"not_desired_{suffix}")
            
            if desired and not_desired:
                error_found = True
            elif desired:
                st.session_state['affix_preferences'][suffix] = 'desired'
            elif not_desired:
                st.session_state['affix_preferences'][suffix] = 'not_desired'
            else:
                st.session_state['affix_preferences'][suffix] = 'none'
    
    # Calculate button
    st.write("")
    col_left, col_center, col_right = st.columns([1, 1, 1])
    with col_center:
        if st.button("Calculate", type="primary"):
            if error_found:
                st.markdown('<div class="error-text">Please pick desired or not desired or neither for modifiers</div>', 
                           unsafe_allow_html=True)
            else:
                prob, error = calculate_combined_probability()
                
                if error:
                    st.markdown(f'<div class="error-text">{error}</div>', unsafe_allow_html=True)
                elif prob is not None:
                    st.markdown(f'<div class="result-text">Probability of getting desired modifiers: {prob*100:.2f}%</div>', 
                               unsafe_allow_html=True)