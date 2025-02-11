import requests
from bs4 import BeautifulSoup
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import time
import random
import logging
import os

# Set up error logging
logging.basicConfig(filename="scraper_errors.log", level=logging.ERROR)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
]

def scrape_scholar_articles(query, num_pages, start_year=None, end_year=None, sort_by="date"):
    all_articles = []
    for page in range(num_pages):
        # Construct URL with custom parameters
        url = f"https://scholar.google.com/scholar?start={page*10}&q={query}&hl=en&as_sdt=0,5"
        if start_year:
            url += f"&as_ylo={start_year}"
        if end_year:
            url += f"&as_yhi={end_year}"
        if sort_by:
            url += f"&sort={sort_by}"

        headers = {"User-Agent": random.choice(USER_AGENTS)}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an error for bad status codes

            soup = BeautifulSoup(response.text, "html.parser")
            results = soup.find_all("div", class_="gs_ri")

            for result in results:
                title = result.find("h3", class_="gs_rt").text
                authors = result.find("div", class_="gs_a").text
                link = result.find("a")["href"]
                article = {"Title": title, "Authors": authors, "Link": link}
                all_articles.append(article)

            time.sleep(random.randint(3, 5))  # To prevent getting blocked
            update_progress_bar(page + 1, num_pages)  # Update the progress bar

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching page {page}: {e}")
            time.sleep(random.randint(5, 10))  # Wait and retry after some time

    return all_articles

def save_to_excel(articles, filename):
    df = pd.DataFrame(articles)
    df.to_excel(filename, index=False)

def download_full_article(link, download_folder):
    # Here you could implement the logic to download PDFs if available.
    # For example:
    response = requests.get(link)
    if response.status_code == 200:
        with open(f"{download_folder}/article.pdf", "wb") as f:
            f.write(response.content)
        print(f"Article downloaded: {link}")
    else:
        print(f"Failed to download article: {link}")

def update_progress_bar(progress, total):
    progress_bar['value'] = (progress / total) * 100
    window.update_idletasks()

def browse_folder():
    folder_path = filedialog.askdirectory()
    entry_folder.delete(0, tk.END)
    entry_folder.insert(tk.END, folder_path)

def scrape_articles():
    query = entry_query.get()
    num_pages = int(entry_pages.get())
    start_year = entry_start_year.get()
    end_year = entry_end_year.get()
    sort_by = entry_sort_by.get()

    # Call the scraping function
    articles = scrape_scholar_articles(query, num_pages, start_year, end_year, sort_by)

    folder_path = entry_folder.get()
    if folder_path:
        filename = f"{folder_path}/scholar_articles.xlsx"
    else:
        filename = "scholar_articles.xlsx"

    save_to_excel(articles, filename)
    label_status.config(text=f"Extraction complete. Data saved to {filename}.")

# GUI setup
window = tk.Tk()
window.title("Google Scholar Scraper")
window.geometry("400x350")

# Query input
label_query = tk.Label(window, text="Article Title or Keyword:")
label_query.pack()
entry_query = tk.Entry(window, width=40)
entry_query.pack()

# Number of pages input
label_pages = tk.Label(window, text="Number of Pages:")
label_pages.pack()
entry_pages = tk.Entry(window, width=40)
entry_pages.pack()

# Year range input
label_year_range = tk.Label(window, text="Start Year (optional):")
label_year_range.pack()
entry_start_year = tk.Entry(window, width=40)
entry_start_year.pack()

label_end_year = tk.Label(window, text="End Year (optional):")
label_end_year.pack()
entry_end_year = tk.Entry(window, width=40)
entry_end_year.pack()

# Sorting input
label_sort_by = tk.Label(window, text="Sort By (date/cited):")
label_sort_by.pack()
entry_sort_by = tk.Entry(window, width=40)
entry_sort_by.pack()

# Output folder input
label_folder = tk.Label(window, text="Output Folder (optional):")
label_folder.pack()
entry_folder = tk.Entry(window, width=40)
entry_folder.pack()

# Browse button
button_browse = tk.Button(window, text="Browse", command=browse_folder)
button_browse.pack()

# Progress bar
progress_bar = ttk.Progressbar(window, length=300, mode='determinate')
progress_bar.pack()

# Extract button
button_extract = tk.Button(window, text="Extract Data", command=scrape_articles)
button_extract.pack()

# Status label
label_status = tk.Label(window, text="")
label_status.pack()

# Run the main window loop
window.mainloop()
