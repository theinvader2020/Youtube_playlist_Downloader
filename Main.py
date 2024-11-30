import os
import sys
import threading
from math import ceil
from pytubefix import YouTube, Playlist
from tkinter import Tk, filedialog, simpledialog


def downloader(video_links, thread_name, output_directory):
    for link in video_links:
        try:
            yt = YouTube(link)
            ys = yt.streams.get_highest_resolution()
            filename = ys.download(output_path=output_directory)
            print(f"{thread_name} --> {os.path.basename(filename)} Downloaded")
        except Exception as e:
            print(f"{thread_name} Failed to download {link}: {e}")


# Initialize Tkinter root
root = Tk()
root.withdraw()  # Hide the main Tkinter window

# Step 1: Ask user for the playlist URL
playlist_url = simpledialog.askstring("Input Playlist URL", "Enter the YouTube Playlist URL:")
if not playlist_url:
    print("No URL provided. Exiting...")
    sys.exit(0)

# Step 2: Load the playlist and validate
try:
    p = Playlist(playlist_url)
    print(f"Loaded Playlist: {p.title}")
    print(f"Total Videos: {len(p.video_urls)}")
except Exception as e:
    print(f"Error loading playlist: {e}")
    sys.exit(0)

# Validate that videos were found
if not p.video_urls:
    print("No videos found in the playlist. Please check the URL.")
    sys.exit(0)

# Step 3: Ask user to choose download location
download_dir = filedialog.askdirectory(title="Select Download Folder")
if not download_dir:
    print("No folder selected. Exiting...")
    sys.exit(0)

# Create a subfolder with the playlist name
playlist_folder_name = p.title.replace(" ", "_").replace("/", "_")
playlist_folder = os.path.join(download_dir, playlist_folder_name)
os.makedirs(playlist_folder, exist_ok=True)
print(f"Downloading to: {playlist_folder}")

# Step 4: Prepare video links and split into chunks
links = list(p.video_urls)
chunk_size = max(1, ceil(len(links) / 4))  # Ensure at least one video per thread
link_chunks = [links[i:i + chunk_size] for i in range(0, len(links), chunk_size)]
link_chunks = [chunk for chunk in link_chunks if chunk]  # Remove empty chunks
print(f"Chunked links for threads: {link_chunks}")

# Step 5: Create and start threads
threads = []
for idx, chunk in enumerate(link_chunks):
    thread_name = f"Thread-{idx + 1}"
    thread = threading.Thread(target=downloader, args=(chunk, thread_name, playlist_folder))
    threads.append(thread)
    thread.start()

# Wait for threads to finish
for thread in threads:
    thread.join()

print("All downloads completed.")
