import streamlit as st
from math import comb

# Set page configuration
st.set_page_config(page_title="Recombinator Calculator", layout="wide")

# Custom CSS for compact UI
st.markdown("""
    <style>
    .stTextInput > div > div > input {
        height: 30px;
        padding: 2px 8px;
    }
    .stCheckbox {
        margin-top: 0px;
        margin-bottom: 2px;
    }
    div[data-testid="stVerticalBlock"] > div {
        padding-top: 0.2rem;
        padding-bottom: 0.2rem;
    }
    .main > div {
        padding-top: 1rem;
    }
    h1 {
        text-align: center;
        margin-bottom: 1rem;
    }
    h3 {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
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
    </style>
    """, unsafe_allow_html=True)

# Title
st.markdown("<h1>Recombinator Calculator</h1>", unsafe_allow_html=True)

# Initialize session state
for key in ['item1_inputs', 'item2_inputs']:
    if key not in st.session_state:
        st.session_state[key] = [''] * 6
for key in ['item1_desired', 'item2_desired', 'item1_non_native', 'item1_exclusive', 
            'item2_non_native', 'item2_exclusive']:
    if key not in st.session_state:
        st.session_state[key] = [False] * 6
for key in ['item1_base_desired', 'item2_base_desired']:
    if key not in st.session_state:
        st.session_state[key] = False

# Labels for inputs
labels = ["Prefix 1", "Prefix 2", "Prefix 3", "Suffix 1", "Suffix 2", "Suffix 3"]

# Create two columns for items
col1, col2 = st.columns(2)

# First Item
with col1:
    st.subheader("First Item")
    st.session_state['item1_base_desired'] = st.checkbox("Desired Base", key="item1_base_check")
    
    for i in range(6):
        # Desired modifier checkbox
        st.session_state['item1_desired'][i] = st.checkbox("✓ Desired", key=f"item1_desired_{i}")
        
        check_col, input_col = st.columns([1, 2])
        
        with check_col:
            st.session_state['item1_non_native'][i] = st.checkbox("Non-Native", key=f"item1_non_native_{i}")
            st.session_state['item1_exclusive'][i] = st.checkbox("Exclusive", key=f"item1_exclusive_{i}")
        
        with input_col:
            input_value = st.text_input(labels[i], key=f"item1_input_{i}")
            st.session_state['item1_inputs'][i] = input_value.lower() if input_value else ''

# Second Item
with col2:
    st.subheader("Second Item")
    st.session_state['item2_base_desired'] = st.checkbox("Desired Base", key="item2_base_check")
    
    for i in range(6):
        # Desired modifier checkbox
        st.session_state['item2_desired'][i] = st.checkbox("✓ Desired", key=f"item2_desired_{i}")
        
        input_col, check_col = st.columns([2, 1])
        
        with input_col:
            input_value = st.text_input(labels[i], key=f"item2_input_{i}")
            st.session_state['item2_inputs'][i] = input_value.lower() if input_value else ''
        
        with check_col:
            st.session_state['item2_non_native'][i] = st.checkbox("Non-Native", key=f"item2_non_native_{i}")
            st.session_state['item2_exclusive'][i] = st.checkbox("Exclusive", key=f"item2_exclusive_{i}")

# Calculation functions
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

def calculate_combined_probability():
    """Calculate probability of getting desired modifiers"""
    
    # Collect modifier data
    prefixes_item1 = []
    prefixes_item2 = []
    suffixes_item1 = []
    suffixes_item2 = []
    
    desired_prefixes = set()
    desired_suffixes = set()
    
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
            else:
                suffixes_item1.append(mod_info)
            
            if st.session_state['item1_desired'][i]:
                if mod_type == 'prefix':
                    desired_prefixes.add(st.session_state['item1_inputs'][i])
                else:
                    desired_suffixes.add(st.session_state['item1_inputs'][i])
            
            if st.session_state['item1_exclusive'][i]:
                exclusive_mods.append((st.session_state['item1_inputs'][i], st.session_state['item1_desired'][i], mod_type, 1))
        
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
            else:
                suffixes_item2.append(mod_info)
            
            if st.session_state['item2_desired'][i]:
                if mod_type == 'prefix':
                    desired_prefixes.add(st.session_state['item2_inputs'][i])
                else:
                    desired_suffixes.add(st.session_state['item2_inputs'][i])
            
            if st.session_state['item2_exclusive'][i]:
                exclusive_mods.append((st.session_state['item2_inputs'][i], st.session_state['item2_desired'][i], mod_type, 2))
    
    # Check exclusive modifier rules
    if len(exclusive_mods) > 1:
        # Special case: 1 desired prefix with non-desired exclusive suffix + 1 desired suffix with non-desired exclusive prefix
        if len(exclusive_mods) == 2:
            ex1, ex2 = exclusive_mods
            if (ex1[2] == 'prefix' and ex2[2] == 'suffix' and ex1[1] and not ex2[1]) or \
               (ex2[2] == 'prefix' and ex1[2] == 'suffix' and ex2[1] and not ex1[1]):
                # Special case: 50% chance
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
    prefix_prob = calculate_modifier_probability(prefixes_item1, prefixes_item2, desired_prefixes, 
                                                  st.session_state['item1_base_desired'], 
                                                  st.session_state['item2_base_desired'])
    
    # Calculate suffix probability
    suffix_prob = calculate_modifier_probability(suffixes_item1, suffixes_item2, desired_suffixes,
                                                  st.session_state['item1_base_desired'],
                                                  st.session_state['item2_base_desired'])
    
    # Combine probabilities
    total_prob = base_prob * prefix_prob * suffix_prob
    
    return total_prob, None

def calculate_modifier_probability(mods_item1, mods_item2, desired_mods, item1_base_desired, item2_base_desired):
    """Calculate probability for prefixes or suffixes"""
    
    if len(desired_mods) == 0:
        return 1.0
    
    # Combine all modifiers (accounting for double-ups)
    all_mods_list = []
    
    for mod_info in mods_item1:
        all_mods_list.append(mod_info)
    for mod_info in mods_item2:
        all_mods_list.append(mod_info)
    
    # Total count including double-ups
    total_count = len(all_mods_list)
    
    if total_count == 0:
        return 0.0
    
    # Get unique modifiers
    unique_mods = list(set([m['mod'] for m in all_mods_list]))
    
    # Get count probabilities
    count_probs = get_count_probabilities(total_count)
    
    total_prob = 0.0
    
    # For each possible outcome count
    for outcome_count, count_prob in count_probs.items():
        if outcome_count == 0:
            continue
        
        # Calculate probability that random selection contains all desired mods
        # considering non-native restrictions
        
        # We need to consider which base wins (50/50 if one base is desired)
        if item1_base_desired or item2_base_desired:
            # Calculate for each base scenario
            prob_base1 = calculate_selection_probability(all_mods_list, unique_mods, desired_mods, outcome_count, 1)
            prob_base2 = calculate_selection_probability(all_mods_list, unique_mods, desired_mods, outcome_count, 2)
            
            if item1_base_desired:
                selection_prob = prob_base1
            else:  # item2_base_desired
                selection_prob = prob_base2
        else:
            # No base preference, average both scenarios
            prob_base1 = calculate_selection_probability(all_mods_list, unique_mods, desired_mods, outcome_count, 1)
            prob_base2 = calculate_selection_probability(all_mods_list, unique_mods, desired_mods, outcome_count, 2)
            selection_prob = (prob_base1 + prob_base2) / 2
        
        total_prob += count_prob * selection_prob
    
    return total_prob

def calculate_selection_probability(all_mods_list, unique_mods, desired_mods, outcome_count, winning_base):
    """Calculate probability of getting desired mods given winning base and outcome count"""
    
    # Filter out non-native mods that can't appear on the winning base
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
    
    if len(available_unique) < outcome_count:
        return 0.0
    
    # Calculate combinations
    total_combinations = comb(len(available_unique), outcome_count)
    
    if len(desired_mods) > outcome_count:
        return 0.0
    
    # Number of combinations that include all desired mods
    remaining_slots = outcome_count - len(desired_mods)
    non_desired = [m for m in available_unique if m not in desired_mods]
    
    if remaining_slots > len(non_desired):
        return 0.0
    
    favorable_combinations = comb(len(non_desired), remaining_slots)
    
    return favorable_combinations / total_combinations

# Calculate button - centered
st.write("")
col_left, col_center, col_right = st.columns([1, 1, 1])
with col_center:
    if st.button("Calculate", type="primary"):
        prob, error = calculate_combined_probability()
        
        if error:
            st.markdown(f'<div class="error-text">{error}</div>', unsafe_allow_html=True)
        elif prob is not None:
            st.markdown(f'<div class="result-text">Probability of getting desired modifiers: {prob*100:.2f}%</div>', 
                       unsafe_allow_html=True)