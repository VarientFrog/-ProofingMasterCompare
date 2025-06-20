#!/usr/bin/env python3

import os
import subprocess
import re
import csv
from tkinter import Tk, filedialog
from datetime import datetime
from tqdm import tqdm  # pip install tqdm

def seconds_to_mins_secs(seconds):
    mins = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{mins}:{secs:02d}"

def extract_chapter_number(filename):
    match = re.match(r"^0*([0-9]+)[^0-9]", filename)
    if match:
        return int(match.group(1))
    match = re.match(r"^0*([0-9]+)$", filename)
    if match:
        return int(match.group(1))
    match = re.search(r"([0-9]+)", filename)
    if match:
        num = int(match.group(1))
        if num < 1000:
            return num
    return None

def list_audio_files(folder):
    files = []
    for f in os.listdir(folder):
        if f.lower().endswith(('.mp3', '.wav')):
            if any(x in f.lower() for x in ['intro', 'outro', 'sample']):
                continue
            chap = extract_chapter_number(f)
            if chap is not None:
                files.append( (chap, f) )
    files.sort(key=lambda x: x[0])
    return files

def get_duration(filepath):
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', filepath],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        return float(result.stdout.strip())
    except Exception:
        return 0.0

def select_file(prompt):
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title=prompt)
    root.destroy()
    return file_path

def main():
    print("Select the FIRST file in the PROOFING folder")
    proofing_first = select_file("Select the FIRST file in the PROOFING folder")
    if not proofing_first:
        print("No file selected for Proofing. Exiting.")
        return
    proofing_folder = os.path.dirname(proofing_first)

    print("Select the FIRST file in the MASTER folder")
    master_first = select_file("Select the FIRST file in the MASTER folder")
    if not master_first:
        print("No file selected for Master. Exiting.")
        return
    master_folder = os.path.dirname(master_first)

    proofing_files = list_audio_files(proofing_folder)
    master_files = list_audio_files(master_folder)

    proofing_filenames = [f for _, f in proofing_files]
    master_filenames = [f for _, f in master_files]

    try:
        proofing_start_index = proofing_filenames.index(os.path.basename(proofing_first))
    except ValueError:
        print("Selected proofing start file not found in folder listing.")
        return
    try:
        master_start_index = master_filenames.index(os.path.basename(master_first))
    except ValueError:
        print("Selected master start file not found in folder listing.")
        return

    total_matches = min(len(proofing_files) - proofing_start_index,
                        len(master_files) - master_start_index)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_csv = os.path.expanduser(f"~/Desktop/duration_compare_{timestamp}.csv")

    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Proofing File','Master File','Proofing Length','Master Length','Difference','Match'])

        for i in tqdm(range(total_matches), desc="Comparing files"):
            pf_file = proofing_files[proofing_start_index + i][1]
            m_file = master_files[master_start_index + i][1]

            pf_path = os.path.join(proofing_folder, pf_file)
            m_path = os.path.join(master_folder, m_file)

            pf_dur = get_duration(pf_path)
            m_dur = get_duration(m_path)

            diff = abs(pf_dur - m_dur)

            pf_dur_fmt = seconds_to_mins_secs(pf_dur)
            m_dur_fmt = seconds_to_mins_secs(m_dur)
            diff_fmt = seconds_to_mins_secs(diff)

            status = "Matched" if diff <= 6 else "Duration mismatch >6s"

            writer.writerow([pf_file, m_file, pf_dur_fmt, m_dur_fmt, diff_fmt, status])

        # Unmatched proofing files
        for i in range(proofing_start_index + total_matches, len(proofing_files)):
            pf_file = proofing_files[i][1]
            pf_path = os.path.join(proofing_folder, pf_file)
            pf_dur = get_duration(pf_path)
            pf_dur_fmt = seconds_to_mins_secs(pf_dur)
            writer.writerow([pf_file, '', pf_dur_fmt, '', '', 'Unmatched Proofing File'])

        # Unmatched master files
        for i in range(master_start_index + total_matches, len(master_files)):
            m_file = master_files[i][1]
            m_path = os.path.join(master_folder, m_file)
            m_dur = get_duration(m_path)
            m_dur_fmt = seconds_to_mins_secs(m_dur)
            writer.writerow(['', m_file, '', m_dur_fmt, '', 'Unmatched Master File'])

    print(f"\nDone! CSV saved to: {output_csv}")

if __name__ == "__main__":
    main()
