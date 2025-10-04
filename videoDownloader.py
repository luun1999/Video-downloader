import tkinter as tk
import subprocess
import threading
from tkinter import ttk

STATUS_ROW = 20

window = tk.Tk()
window.title("Video Downloader")
window.geometry("400x400")

isBestVideo = tk.IntVar()
canExportMp4 = tk.IntVar()
canEmbedMeta = tk.IntVar()
canExportEmbedMeta = tk.IntVar()
usingCookieChrome = tk.IntVar()
usingVrVideoClient = tk.IntVar()
isDownloading = False

title = tk.Label(window, text="YT-DLP - Video Downloader", font=("Arial", 16, "bold")).grid(row=0, sticky=tk.W)
bestVideoCheckBox = tk.Checkbutton(window, text=" Download with best quality", variable=isBestVideo).grid(row=1, sticky=tk.W)
exportMp4CheckBox = tk.Checkbutton(window, text=" Export MP4", variable=canExportMp4).grid(row=2, sticky=tk.W)
embedMetaCheckBox = tk.Checkbutton(window, text=" Embed Metadata (require ffmpeg)", variable=canEmbedMeta).grid(row=3, sticky=tk.W)
exportEmbedMetaCheckBox = tk.Checkbutton(window, text=" Export Metadata", variable=canExportEmbedMeta).grid(row=4, sticky=tk.W)
usingCookieChromeCheckBox = tk.Checkbutton(window, text=" Use Chrome Cookie", variable=usingCookieChrome).grid(row=5, sticky=tk.W)
usingVrVideoClientCheckBox = tk.Checkbutton(window, text=" Use Android Vr Client", variable=usingVrVideoClient).grid(row=6, sticky=tk.W)

urlString = tk.StringVar()
urlLabel = tk.Label(window, text="URL: ").grid(row=10, sticky=tk.W, padx=5)
urlEntry = tk.Entry(window, textvariable=urlString, width=50).grid(row=11, sticky=tk.W, padx=5)

def on_download_done(progressbar:ttk.Progressbar):
    reset_state()
    progressbar.stop()
    progressbar.destroy()

    print("Finished!" )
    tk.Label(window, text="FINISHED: Downloaded Video", fg="green").grid(row=STATUS_ROW, sticky=tk.W)

def on_download_err(progressbar:ttk.Progressbar, err:str):
    reset_state()
    progressbar.stop()
    progressbar.destroy()

    tk.Label(window, text=err, fg="red").grid(row=STATUS_ROW, sticky=tk.W)

def reset_state():
    isDownloading = False
    downloadButton.config(state=tk.NORMAL)

def download_video(command:str, progressbar:ttk.Progressbar, window):
    hasException = False
    
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    except:
        hasException = True

    if (process.stdout is not None):
        for line in process.stdout:
            print(line, end="")
            tk.Label(window, text=line, fg="black").grid(row=STATUS_ROW, sticky=tk.W)

    if (process.stderr is not None):
        for line in process.stderr:
            print(line, end="")
            tk.Label(window, text=line, fg="red").grid(row=STATUS_ROW, sticky=tk.W)
        hasException = True

    process.wait()

    if process.returncode != 0 and hasException:
        window.after(0, lambda: on_download_err(progressbar, "Error Occured!"))
    else:
        window.after(0, lambda: on_download_done(progressbar))


def download_video_runner():
    isDownloading = True
    downloadButton.config(state=tk.DISABLED)
    print("Repairing to download...")
    tk.Label(window, text="", width=100).grid(row=STATUS_ROW, sticky=tk.W)
    command = 'yt-dlp'

    if usingVrVideoClient.get():
        command += ' --extractor-arg "youtube:player_client=android_vr" --user-agent ""'

    if isBestVideo.get():
        command += " -f bestvideo+bestaudio/best"

    if canExportMp4.get():
        command += " --merge-output-format mp4"
    
    if canEmbedMeta.get():
        command += " --embed-metadata"

    if canExportEmbedMeta.get():
        command += " --write-info-json"

    if usingCookieChrome.get():
        command += " --cookies-from-browser chrome"
    
    urlValue = urlString.get()
    if urlValue == "":
        print("URL is empty")
        tk.Label(window, text="URL is empty", fg="red").grid(row=STATUS_ROW, sticky=tk.W)
        reset_state()
        return
    
    command += " " + urlString.get().strip()
    print("downloading video, url: " + command)

    try:
        progressbar = ttk.Progressbar(mode="indeterminate", orient=tk.HORIZONTAL, length=200)
        progressbar.grid(row=19, sticky=tk.W)
        progressbar.start(10)

        threading.Thread(target=download_video, args=(command, progressbar, window), daemon=True).start()

    except:
        print("[EXCEPTION]" )
        tk.Label(window, text="Exception when downloading video", fg="red").grid(row=STATUS_ROW, sticky=tk.W)
        reset_state()
        return

downloadButton = tk.Button(window, text="Download", command=download_video_runner)
downloadButton.grid(row=15, sticky=tk.W, pady=10, ipadx=10)

window.mainloop()