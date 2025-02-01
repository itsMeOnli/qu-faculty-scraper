import streamlit as st
import pandas as pd
import requests
import json

def scrape_faculty_info(search_term):
    # Base URL for the SharePoint API
    base_url = "https://www.qu.edu.qa/_api/Web/lists/getbytitle('upinventory')/items"
    
    # Parameters for the API request
    params = {
        '$top': '100',
        '$orderby': 'Title asc',
        '$filter': f"""xfhg ne null and (
            substringof('{search_term}', Title) or 
            substringof('{search_term}', i0p3) or 
            substringof('{search_term}', OData__x006d_zy6) or 
            substringof('{search_term}', fcqq) or 
            substringof('{search_term}', qUArabicDepartment) or 
            substringof('{search_term}', qUArabicName) or 
            substringof('{search_term}', qUArabicTitle))""",
        '$select': '*'
    }
    
    # Headers required for SharePoint API
    headers = {
        'Accept': 'application/json;odata=verbose',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(base_url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if we have results in the response
            if 'd' in data and 'results' in data['d']:
                faculty_list = []
                
                for item in data['d']['results']:
                    faculty_info = {
                        'Name': item.get('Title', ''),
                        'Role': item.get('i0p3', ''),  # You might need to adjust these field names
                        'Department': item.get('OData__x006d_zy6', ''),
                        'Email': item.get('fcqq', ''),
                        'Phone': item.get('xfhg', '')
                    }
                    faculty_list.append(faculty_info)
                
                return pd.DataFrame(faculty_list)
            else:
                st.error('No results found in the API response')
                return None
        else:
            st.error(f'API request failed with status code: {response.status_code}')
            return None
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Response content: " + response.text if 'response' in locals() else "No response received")
        return None

# Streamlit UI
st.title('QU Faculty Directory Search')

# Search input box
search_term = st.text_input('Enter search term (e.g., "chemical" for Chemical Engineering faculty)')

# Debug mode checkbox
debug_mode = st.checkbox('Enable debug mode')

if st.button('Search Faculty'):
    if search_term:
        with st.spinner('Searching faculty directory...'):
            df = scrape_faculty_info(search_term)
            
            if debug_mode:
                st.write("API Response Debug Info:")
                try:
                    response = requests.get(
                        "https://www.qu.edu.qa/_api/Web/lists/getbytitle('upinventory')/items",
                        params={'$top': '1'},
                        headers={'Accept': 'application/json;odata=verbose'}
                    )
                    st.json(response.json())
                except Exception as e:
                    st.error(f"Debug request failed: {str(e)}")
            
            if df is not None and not df.empty:
                st.success(f'Found {len(df)} faculty members!')
                
                # Display the dataframe
                st.dataframe(df)
                
                # Download button for CSV
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name=f"qu_faculty_{search_term.lower().replace(' ', '_')}.csv",
                    mime='text/csv'
                )
            else:
                st.warning('No faculty members found for the given search term.')
    else:
        st.warning('Please enter a search term.')

# Instructions
st.markdown("""
### Instructions:
1. Enter a search term (e.g., "chemical" for Chemical Engineering faculty)
2. Click 'Search Faculty' button
3. If results are found, they will be displayed in a table
4. Use the download button to save results as CSV

Note: The search looks for faculty members across names, departments, and titles.
""")

# Added debug information section
if debug_mode:
    st.markdown("""
    ### Debug Information
    The app is using the SharePoint API endpoint to fetch faculty information.
    If you're not getting results, check:
    1. Network connectivity to qu.edu.qa
    2. API endpoint accessibility
    3. Search term spelling
    """)
