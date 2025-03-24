import streamlit as st
import pandas as pd
import json
import os
import requests
from streamlit_lottie import st_lottie

# Load Lottie Animation
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception as e:
        st.error(f"Error loading Lottie animation: {e}")
        return None

lottie_books = load_lottieurl("https://assets7.lottiefiles.com/packages/lf20_x62chJ.json")

# Set Page Configuration
st.set_page_config(
    page_title="Personal Library System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Styling
st.markdown(
    """
    <style>
    .main-header { font-size: 3rem; color: #0D47A1; text-align: center; font-weight: 800; }
    .sub-header { font-size: 1.5rem; color: #1976D2; font-weight: 600; margin-bottom: 10px; }
    .book-card { background: #E3F2FD; border-radius: 10px; padding: 15px; margin: 10px 0; box-shadow: 2px 4px 10px rgba(0,0,0,0.2); }
    .sidebar .css-1d391kg { background-color: #0D47A1; }
    </style>
    """, unsafe_allow_html=True
)

# Load Library Data from File
def load_library():
    if os.path.exists("library.json"):
        with open("library.json", "r") as f:
            st.session_state.library = json.load(f)

# Save Library Data to File
def save_library():
    with open("library.json", "w") as f:
        json.dump(st.session_state.library, f)

# Initialize Library Storage
if 'library' not in st.session_state:
    st.session_state.library = []
    load_library()  # Load data at startup

# Add a Book Function
def add_book():
    st.markdown("<h2 class='sub-header'>📖 Add a New Book</h2>", unsafe_allow_html=True)
    title = st.text_input("Book Title:")
    author = st.text_input("Author:")
    year = st.number_input("Publication Year:", min_value=1800, max_value=2100, step=1)
    genre = st.text_input("Genre:")
    image_url = st.text_input("Book Cover Image URL (optional):")
    read_status = st.radio("Read Status:", ["Read", "Unread"], horizontal=True)
    
    if st.button("📚 Add Book", use_container_width=True):
        if not title or not author or not genre:
            st.error("Please fill in all fields.")
        else:
            book = {
                "title": title,
                "author": author,
                "year": year,
                "genre": genre,
                "image_url": image_url,
                "read": read_status == "Read"
            }
            st.session_state.library.append(book)
            save_library()
            st.success(f"✅ Book '{title}' added successfully!")

# Remove a Book Function
def remove_book():
    st.markdown("<h2 class='sub-header'>🗑 Remove a Book</h2>", unsafe_allow_html=True)
    title = st.text_input("Enter book title to remove:")
    
    if st.button("🗑 Remove Book", use_container_width=True):
        initial_count = len(st.session_state.library)
        st.session_state.library = [b for b in st.session_state.library if b["title"].lower() != title.lower()]
        if len(st.session_state.library) < initial_count:
            save_library()
            st.warning(f"❌ Book '{title}' removed.")
        else:
            st.error(f"❌ Book '{title}' not found.")

# Search a Book Function
def search_book():
    st.markdown("<h2 class='sub-header'>🔎 Search a Book</h2>", unsafe_allow_html=True)
    search_term = st.text_input("Enter title or author:")
    
    if st.button("🔍 Search", use_container_width=True):
        results = [b for b in st.session_state.library if search_term.lower() in b["title"].lower() or search_term.lower() in b["author"].lower()]
        
        if results:
            for book in results:
                st.markdown(f"<div class='book-card'><strong>{book['title']}</strong> - {book['author']} ({book['year']}) [{book['genre']}]</div>", unsafe_allow_html=True)
        else:
            st.error("❌ No books found.")

# Display All Books Function
def display_all_books():
    st.markdown("<h2 style='text-align: center; color: #333;'>📚 All Books in Library</h2>", unsafe_allow_html=True)
    
    # Filter Options
    filter_genre = st.selectbox("Filter by Genre", ["All"] + list(set(book["genre"] for book in st.session_state.library)))
    filter_status = st.radio("Filter by Status", ["All", "Read", "Unread"], horizontal=True)
    
    filtered_books = st.session_state.library
    if filter_genre != "All":
        filtered_books = [b for b in filtered_books if b["genre"] == filter_genre]
    if filter_status != "All":
        filtered_books = [b for b in filtered_books if b["read"] == (filter_status == "Read")]
    
    if not filtered_books:
        st.warning("⚠️ No books match the filter criteria.")
    else:
        for i, book in enumerate(filtered_books):
            # Book Card
            st.markdown(f"""
                <div class='book-card'>
                    <h3>{book['title']}</h3>
                    <p><strong>Author:</strong> {book['author']}</p>
                    <p><strong>Year:</strong> {book['year']}</p>
                    <p><strong>Genre:</strong> {book['genre']}</p>
                    {f"<img src='{book['image_url']}' alt='Book Cover' style='width: 150px;'>" if 'image_url' in book and book['image_url'] else ""}
                    <p><strong>Status:</strong> {"✅ Read" if book["read"] else "❌ Unread"}</p>
                </div>
            """, unsafe_allow_html=True)

            # Toggle Read/Unread Button
            if st.button(f"Toggle Status for {book['title']}", key=f"button_{i}"):
                st.session_state.library[i]["read"] = not st.session_state.library[i]["read"]
                save_library()
                st.experimental_rerun()  # Refresh the page to update the status

# Display Library Statistics
def display_statistics():
    st.markdown("<h2 class='sub-header'>📊 Library Statistics</h2>", unsafe_allow_html=True)
    total_books = len(st.session_state.library)
    read_books = sum(book["read"] for book in st.session_state.library)
    unread_books = total_books - read_books
    
    if total_books > 0:
        st.write(f"📚 Total Books: {total_books}")
        st.write(f"✅ Read Books: {read_books}")
        st.write(f"❌ Unread Books: {unread_books}")
    else:
        st.warning("📉 No books to display statistics.")

# Export Library Data
def export_library():
    st.markdown("<h2 class='sub-header'>📤 Export Library Data</h2>", unsafe_allow_html=True)
    export_format = st.radio("Export Format", ["CSV", "JSON"])
    
    if st.button("📤 Export", use_container_width=True):
        if export_format == "CSV":
            df = pd.DataFrame(st.session_state.library)
            df.to_csv("library_export.csv", index=False)
            st.success("✅ Library exported to CSV successfully!")
        elif export_format == "JSON":
            with open("library_export.json", "w") as f:
                json.dump(st.session_state.library, f)
            st.success("✅ Library exported to JSON successfully!")

# Sidebar Navigation
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2232/2232688.png", width=150)
st.sidebar.title("📖 Library Menu")
menu = ["Home", "Add a Book", "Remove a Book", "Search for a Book", "Display All Books", "Library Statistics", "Export Library"]
choice = st.sidebar.radio("Navigate", menu)

# Main Content
def main():
    load_library()  # Load library data at startup
    if choice == "Home":
        st.markdown("<h1 class='main-header'>📚 Personal Library Management</h1>", unsafe_allow_html=True)
        if lottie_books:
            st_lottie(lottie_books, height=300)
    elif choice == "Add a Book":
        add_book()
    elif choice == "Remove a Book":
        remove_book()
    elif choice == "Search for a Book":
        search_book()
    elif choice == "Display All Books":
        display_all_books()
    elif choice == "Library Statistics":
        display_statistics()
    elif choice == "Export Library":
        export_library()

if __name__ == "__main__":
    main()