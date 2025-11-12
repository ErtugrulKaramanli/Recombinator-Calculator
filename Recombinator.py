import streamlit as st

# Set page configuration
st.set_page_config(page_title="Input Form with Modifiers", layout="wide")

# Title
st.title("Input Form with Modifiers")

# Initialize session state for storing inputs if not already present
if 'left_inputs' not in st.session_state:
    st.session_state.left_inputs = [''] * 6
if 'right_inputs' not in st.session_state:
    st.session_state.right_inputs = [''] * 6
if 'left_non_native' not in st.session_state:
    st.session_state.left_non_native = [False] * 6
if 'left_exclusive' not in st.session_state:
    st.session_state.left_exclusive = [False] * 6
if 'right_non_native' not in st.session_state:
    st.session_state.right_non_native = [False] * 6
if 'right_exclusive' not in st.session_state:
    st.session_state.right_exclusive = [False] * 6

# Create two columns for left and right sections
col1, col2 = st.columns(2)

# Left side - 6 input boxes
with col1:
    st.subheader("Left Section")
    for i in range(6):
        # Create columns for checkbox and input
        check_col, input_col = st.columns([1, 3])
        
        with check_col:
            st.session_state.left_non_native[i] = st.checkbox(
                "Non-Native Modifier", 
                key=f"left_non_native_{i}",
                value=st.session_state.left_non_native[i]
            )
            st.session_state.left_exclusive[i] = st.checkbox(
                "Exclusive Modifier", 
                key=f"left_exclusive_{i}",
                value=st.session_state.left_exclusive[i]
            )
        
        with input_col:
            # Convert input to lowercase for case-insensitive handling
            input_value = st.text_input(
                f"Left Input {i+1}", 
                key=f"left_input_{i}",
                value=st.session_state.left_inputs[i]
            )
            st.session_state.left_inputs[i] = input_value.lower() if input_value else ''
        
        st.markdown("---")

# Right side - 6 input boxes
with col2:
    st.subheader("Right Section")
    for i in range(6):
        # Create columns for input and checkbox
        input_col, check_col = st.columns([3, 1])
        
        with input_col:
            # Convert input to lowercase for case-insensitive handling
            input_value = st.text_input(
                f"Right Input {i+1}", 
                key=f"right_input_{i}",
                value=st.session_state.right_inputs[i]
            )
            st.session_state.right_inputs[i] = input_value.lower() if input_value else ''
        
        with check_col:
            st.session_state.right_non_native[i] = st.checkbox(
                "Non-Native Modifier", 
                key=f"right_non_native_{i}",
                value=st.session_state.right_non_native[i]
            )
            st.session_state.right_exclusive[i] = st.checkbox(
                "Exclusive Modifier", 
                key=f"right_exclusive_{i}",
                value=st.session_state.right_exclusive[i]
            )
        
        st.markdown("---")

# Optional: Display collected data (for testing)
if st.button("Show Collected Data"):
    st.write("### Left Section Data:")
    for i in range(6):
        st.write(f"Input {i+1}: '{st.session_state.left_inputs[i]}' | "
                f"Non-Native: {st.session_state.left_non_native[i]} | "
                f"Exclusive: {st.session_state.left_exclusive[i]}")
    
    st.write("### Right Section Data:")
    for i in range(6):
        st.write(f"Input {i+1}: '{st.session_state.right_inputs[i]}' | "
                f"Non-Native: {st.session_state.right_non_native[i]} | "
                f"Exclusive: {st.session_state.right_exclusive[i]}")