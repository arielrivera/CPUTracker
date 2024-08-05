import streamlit as st
import sqlite3
import streamlit.components.v1 as components

# Connect to the database
conn = sqlite3.connect('cputracker.db')
cursor = conn.cursor()

# Function to get unique part numbers from the database
def get_unique_part_numbers():
    cursor.execute("SELECT DISTINCT part_number FROM UNITS")
    return [row[0] for row in cursor.fetchall()]

# Function to get data for the table based on search criteria
def get_table_data(search_query, part_number, search_mode):
    if search_mode:
        # Search mode
        if "_" in search_query:
            # Combined search (serial number and part number)
            serial_number, part_number = search_query.split("_")
            cursor.execute(
                "SELECT * FROM UNITS WHERE serial_number LIKE ? AND part_number LIKE ?",
                (f"%{serial_number}%", f"%{part_number}%"),
            )
        elif "-" in search_query and "_" not in search_query:
            # Part number search
            cursor.execute("SELECT * FROM UNITS WHERE part_number LIKE ?", (f"%{search_query}%",))
        else:
            # Serial number search
            cursor.execute("SELECT * FROM UNITS WHERE serial_number LIKE ?", (f"%{search_query}%",))
    else:
        # Input mode
        if part_number == "Any":
            cursor.execute("SELECT * FROM UNITS")
        else:
            cursor.execute("SELECT * FROM UNITS WHERE part_number = ?", (part_number,))
    return cursor.fetchall()

# Streamlit UI
st.title("CPUTracker")

# Topbar (Modified for Inline Layout)
st.write("## Search")  # Add a heading for the search section
col1, col2, col3, col4 = st.columns(4)  # Create three columns for inline layout

# Initialize search_mode
search_mode = st.session_state.get("search_mode", True)  # Start in search mode

with col1:
    # Use st.session_state to track search_mode
    search_mode = st.radio("Mode", ("Search", "Input"), key="search_mode")

with col2:
    search_query = st.text_input("Unit", key="search_query")

with col3:
    part_number_dropdown = st.selectbox("Part Number", ["Any"] + get_unique_part_numbers())

with col4:
    search_button = st.button("Search" if search_mode == "Search" else "Add")

# Bottom Table
table_data = get_table_data(search_query, part_number_dropdown, search_mode == "Search")
if "table_data" not in st.session_state:
    st.session_state.table_data = table_data
st.dataframe(st.session_state.table_data, use_container_width=True)

# Handle Search/Input Mode
if search_button or st.session_state.get("enter_pressed", False):
    if search_mode == "Search":
        # Search mode - Handle search logic here
        st.write("Search results:")
        # ... (Display search results)
    else:
        # Input mode - Handle adding new records here
        # Add the record
        if search_query and (search_query.isalnum() or "-" in search_query or "_" in search_query):
            cursor.execute(
                "INSERT INTO UNITS (serial_number, part_number, datecode, country, composite_snpn) VALUES (?, ?, ?, ?, ?)",
                (search_query, part_number_dropdown, None, None, None),
            )
            conn.commit()
            st.success("Record added successfully!")
            # Reload the table to show the new record
            # Instead of creating a new dataframe, update the existing one
            st.session_state.table_data = get_table_data(search_query, part_number_dropdown, search_mode == "Search")
            # Clear the existing dataframe and re-render it
            # st.experimental_rerun()  <-- Removed

# Handle Enter Key Press
if st.session_state.get("enter_pressed", False):
    st.session_state.enter_pressed = False

# Close the database connection
conn.close()

# Add custom JavaScript
st.markdown(
    """
    <script>
        // Your custom JavaScript code here
        document.addEventListener('keyup', function(event) {
            if (event.key === 'Enter' && document.activeElement.id === 'search_query') {
                // Trigger the button click
                document.getElementById('search_button').click();
            }
        });
    </script>
    """,
    unsafe_allow_html=True,
)
