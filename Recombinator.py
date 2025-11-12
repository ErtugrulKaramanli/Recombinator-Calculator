import streamlit as st
from itertools import combinations

# Set page configuration
st.set_page_config(page_title="Modifier Recombination Calculator", layout="wide")

# Custom CSS to make UI more compact
st.markdown("""
    <style>
    .stTextInput > div > div > input {
        height: 35px;
    }
    .stCheckbox {
        margin-top: 0px;
        margin-bottom: 0px;
    }
    div[data-testid="stVerticalBlock"] > div {
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.title("Modifier Recombination Calculator")

# Initialize session state
if 'item1_inputs' not in st.session_state:
    st.session_state.item1_inputs = [''] * 6
if 'item2_inputs' not in st.session_state:
    st.session_state.item2_inputs = [''] * 6
if 'item1_desired' not in st.session_state:
    st.session_state.item1_desired = [False] * 6
if 'item2_desired' not in st.session_state:
    st.session_state.item2_desired = [False] * 6
if 'item1_non_native' not in st.session_state:
    st.session_state.item1_non_native = [False] * 6
if 'item1_exclusive' not in st.session_state:
    st.session_state.item1_exclusive = [False] * 6
if 'item2_non_native' not in st.session_state:
    st.session_state.item2_non_native = [False] * 6
if 'item2_exclusive' not in st.session_state:
    st.session_state.item2_exclusive = [False] * 6

# Labels for inputs
labels = ["Prefix 1", "Prefix 2", "Prefix 3", "Suffix 1", "Suffix 2", "Suffix 3"]

# Create two columns for items
col1, col2 = st.columns(2)

# First Item
with col1:
    st.subheader("First Item")
    for i in range(6):
        st.session_state.item1_desired[i] = st.checkbox(
            "Desired Modifier", 
            key=f"item1_desired_{i}",
            value=st.session_state.item1_desired[i]
        )
        
        check_col, input_col = st.columns([1, 2])
        
        with check_col:
            st.session_state.item1_non_native[i] = st.checkbox(
                "Non-Native", 
                key=f"item1_non_native_{i}",
                value=st.session_state.item1_non_native[i]
            )
            st.session_state.item1_exclusive[i] = st.checkbox(
                "Exclusive", 
                key=f"item1_exclusive_{i}",
                value=st.session_state.item1_exclusive[i]
            )
        
        with input_col:
            input_value = st.text_input(
                labels[i], 
                key=f"item1_input_{i}",
                value=st.session_state.item1_inputs[i]
            )
            st.session_state.item1_inputs[i] = input_value.lower() if input_value else ''

# Second Item
with col2:
    st.subheader("Second Item")
    for i in range(6):
        st.session_state.item2_desired[i] = st.checkbox(
            "Desired Modifier", 
            key=f"item2_desired_{i}",
            value=st.session_state.item2_desired[i]
        )
        
        input_col, check_col = st.columns([2, 1])
        
        with input_col:
            input_value = st.text_input(
                labels[i], 
                key=f"item2_input_{i}",
                value=st.session_state.item2_inputs[i]
            )
            st.session_state.item2_inputs[i] = input_value.lower() if input_value else ''
        
        with check_col:
            st.session_state.item2_non_native[i] = st.checkbox(
                "Non-Native", 
                key=f"item2_non_native_{i}",
                value=st.session_state.item2_non_native[i]
            )
            st.session_state.item2_exclusive[i] = st.checkbox(
                "Exclusive", 
                key=f"item2_exclusive_{i}",
                value=st.session_state.item2_exclusive[i]
            )

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

def calculate_probability(item1_mods, item2_mods, desired_item1, desired_item2):
    """Calculate probability of getting desired modifiers"""
    # Combine all modifiers and track which are desired
    all_mods = []
    desired_mods = set()
    
    # Add item1 modifiers
    for mod in item1_mods:
        if mod:
            all_mods.append(mod)
            if mod in desired_item1:
                desired_mods.add(mod)
    
    # Add item2 modifiers (check for double-ups)
    for mod in item2_mods:
        if mod:
            all_mods.append(mod)
            if mod in desired_item2:
                desired_mods.add(mod)
    
    # Count unique modifiers and total (for double-ups)
    unique_mods = list(set(all_mods))
    total_count = len(all_mods)  # Total including double-ups
    
    if total_count == 0 or len(desired_mods) == 0:
        return 0.0
    
    # Get probability distribution for number of mods we'll get
    count_probs = get_count_probabilities(total_count)
    
    # Calculate probability for each possible outcome count
    total_prob = 0.0
    
    for outcome_count, count_prob in count_probs.items():
        if outcome_count == 0:
            continue
        
        # Calculate probability that a random selection contains all desired mods
        # Number of ways to choose outcome_count mods from unique_mods
        from math import comb
        total_combinations = comb(len(unique_mods), outcome_count)
        
        # Number of ways that include all desired mods
        if len(desired_mods) <= outcome_count:
            # Choose the remaining from non-desired mods
            remaining_to_choose = outcome_count - len(desired_mods)
            non_desired_mods = [m for m in unique_mods if m not in desired_mods]
            
            if remaining_to_choose <= len(non_desired_mods):
                favorable_combinations = comb(len(non_desired_mods), remaining_to_choose)
                prob_getting_desired = favorable_combinations / total_combinations
                total_prob += count_prob * prob_getting_desired
    
    return total_prob

# Calculate button
if st.button("Calculate", type="primary"):
    # Get desired modifiers for prefixes and suffixes
    desired_prefixes_item1 = [st.session_state.item1_inputs[i] for i in range(3) 
                              if st.session_state.item1_desired[i] and st.session_state.item1_inputs[i]]
    desired_prefixes_item2 = [st.session_state.item2_inputs[i] for i in range(3) 
                              if st.session_state.item2_desired[i] and st.session_state.item2_inputs[i]]
    
    desired_suffixes_item1 = [st.session_state.item1_inputs[i] for i in range(3, 6) 
                              if st.session_state.item1_desired[i] and st.session_state.item1_inputs[i]]
    desired_suffixes_item2 = [st.session_state.item2_inputs[i] for i in range(3, 6) 
                              if st.session_state.item2_desired[i] and st.session_state.item2_inputs[i]]
    
    # Get all prefixes and suffixes
    prefixes_item1 = [st.session_state.item1_inputs[i] for i in range(3) if st.session_state.item1_inputs[i]]
    prefixes_item2 = [st.session_state.item2_inputs[i] for i in range(3) if st.session_state.item2_inputs[i]]
    
    suffixes_item1 = [st.session_state.item1_inputs[i] for i in range(3, 6) if st.session_state.item1_inputs[i]]
    suffixes_item2 = [st.session_state.item2_inputs[i] for i in range(3, 6) if st.session_state.item2_inputs[i]]
    
    # Calculate probabilities
    prefix_prob = calculate_probability(prefixes_item1, prefixes_item2, 
                                       desired_prefixes_item1, desired_prefixes_item2)
    suffix_prob = calculate_probability(suffixes_item1, suffixes_item2, 
                                       desired_suffixes_item1, desired_suffixes_item2)
    
    # Display results
    st.write("---")
    st.subheader("Results")
    
    if len(desired_prefixes_item1) + len(desired_prefixes_item2) > 0:
        st.write(f"**Probability of getting desired prefixes:** {prefix_prob*100:.2f}%")
    
    if len(desired_suffixes_item1) + len(desired_suffixes_item2) > 0:
        st.write(f"**Probability of getting desired suffixes:** {suffix_prob*100:.2f}%")
    
    if (len(desired_prefixes_item1) + len(desired_prefixes_item2) > 0 and 
        len(desired_suffixes_item1) + len(desired_suffixes_item2) > 0):
        combined_prob = prefix_prob * suffix_prob
        st.write(f"**Combined probability (prefixes AND suffixes):** {combined_prob*100:.2f}%")
    
    if (len(desired_prefixes_item1) + len(desired_prefixes_item2) == 0 and 
        len(desired_suffixes_item1) + len(desired_suffixes_item2) == 0):
        st.warning("Please select at least one desired modifier to calculate probabilities.")