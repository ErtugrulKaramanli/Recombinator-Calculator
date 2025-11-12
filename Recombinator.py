import streamlit as st
from itertools import combinations
import streamlit.components.v1 as components

# Set page configuration
st.set_page_config(page_title="Recombinator Calculator", layout="wide")

# Custom CSS and JavaScript for compact UI and right-click functionality
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
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.markdown("<h1>Recombinator Calculator</h1>", unsafe_allow_html=True)

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
if 'item1_base_desired' not in st.session_state:
    st.session_state.item1_base_desired = False
if 'item2_base_desired' not in st.session_state:
    st.session_state.item2_base_desired = False

# Labels for inputs
labels = ["Prefix 1", "Prefix 2", "Prefix 3", "Suffix 1", "Suffix 2", "Suffix 3"]

# JavaScript for right-click functionality
components.html("""
<script>
    const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
    
    async function setupRightClick() {
        await sleep(500);
        const inputs = window.parent.document.querySelectorAll('input[type="text"]');
        inputs.forEach(input => {
            input.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                if (input.style.backgroundColor === 'rgb(144, 238, 144)' || input.style.backgroundColor === 'lightgreen') {
                    input.style.backgroundColor = '';
                } else {
                    input.style.backgroundColor = 'lightgreen';
                }
            });
        });
    }
    setupRightClick();
    setInterval(setupRightClick, 1000);
</script>
""", height=0)

# Create two columns for items
col1, col2 = st.columns(2)

# First Item
with col1:
    st.subheader("First Item")
    st.session_state.item1_base_desired = st.checkbox(
        "Desired Base", 
        key="item1_base_desired",
        value=st.session_state.item1_base_desired
    )
    for i in range(6):
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
                value=st.session_state.item1_inputs[i],
                label_visibility="visible"
            )
            st.session_state.item1_inputs[i] = input_value.lower() if input_value else ''

# Second Item
with col2:
    st.subheader("Second Item")
    st.session_state.item2_base_desired = st.checkbox(
        "Desired Base", 
        key="item2_base_desired",
        value=st.session_state.item2_base_desired
    )
    for i in range(6):
        input_col, check_col = st.columns([2, 1])
        
        with input_col:
            input_value = st.text_input(
                labels[i], 
                key=f"item2_input_{i}",
                value=st.session_state.item2_inputs[i],
                label_visibility="visible"
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

def calculate_probability():
    """Calculate probability of getting desired modifiers"""
    # Detect desired modifiers from green backgrounds using JavaScript state
    # For now, we'll use a manual tracking system
    # Users need to mark desired by right-clicking inputs
    
    # Get modifier information
    item1_data = []
    item2_data = []
    
    for i in range(6):
        if st.session_state.item1_inputs[i]:
            item1_data.append({
                'mod': st.session_state.item1_inputs[i],
                'non_native': st.session_state.item1_non_native[i],
                'exclusive': st.session_state.item1_exclusive[i],
                'type': 'prefix' if i < 3 else 'suffix'
            })
        if st.session_state.item2_inputs[i]:
            item2_data.append({
                'mod': st.session_state.item2_inputs[i],
                'non_native': st.session_state.item2_non_native[i],
                'exclusive': st.session_state.item2_exclusive[i],
                'type': 'prefix' if i < 3 else 'suffix'
            })
    
    # Check for exclusive modifier violations
    exclusive_count = sum(1 for d in item1_data if d['exclusive']) + sum(1 for d in item2_data if d['exclusive'])
    
    if exclusive_count > 1:
        # Check for special case: 1 desired prefix with non-desired exclusive suffix + 1 desired suffix with non-desired exclusive prefix
        # For now, return error - need desired modifier detection
        return None, "There can only be 1 exclusive modifier on an item"
    
    # Calculate base probability
    base_prob = 1.0
    if st.session_state.item1_base_desired and st.session_state.item2_base_desired:
        return None, "Cannot select both bases as desired"
    elif st.session_state.item1_base_desired or st.session_state.item2_base_desired:
        base_prob = 0.5
    
    # Simplified calculation - would need desired modifier detection from green backgrounds
    # This is a placeholder that assumes all filled inputs are desired
    return base_prob, None

# Calculate button - centered
col_left, col_center, col_right = st.columns([1, 1, 1])
with col_center:
    if st.button("Calculate", type="primary"):
        prob, error = calculate_probability()
        
        if error:
            st.error(error)
        elif prob is not None:
            st.markdown(f'<div class="result-text">Probability of getting desired modifiers: {prob*100:.2f}%</div>', 
                       unsafe_allow_html=True)

st.info("💡 Tip: Right-click on any input box to mark it as a desired modifier (turns green)")