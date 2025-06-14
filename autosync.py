import librosa
import numpy as np
from scipy import signal
import argparse
from pathlib import Path
import warnings
import os

# suppress warnings for PySoundFile because it warns about mp3 files
warnings.filterwarnings("ignore", category=UserWarning, module='librosa')
warnings.filterwarnings(action='ignore',category=FutureWarning,module='librosa.core.audio')



def calculate_offset_between_two(y1,y2,samplerate=44100):

  # Cross-correlate
  correlation = signal.correlate(y1, y2, mode='full', method='fft')
  lags = signal.correlation_lags(len(y1), len(y2), mode="full")
  lag_samples = lags[np.argmax(correlation)]
  time_offset_seconds = lag_samples / samplerate
  return time_offset_seconds


def calculate_delays_for_n_files(file_paths, common_correlation_sr=None):
  print(f"Processing {len(file_paths)} files...")

  file_info = []

  # load all files
  for i in range(0, len(file_paths)):
    current_path = file_paths[i]
    print(f"Loading: {os.path.basename(current_path)}")
    y_curr, sr_curr = librosa.load(current_path, sr=44100, mono=True)
    file_info.append({
      'index': i,
      'path': current_path,
      'basename': os.path.basename(current_path),
      'y': y_curr,
      'sr': sr_curr
    })
  file_info[0]["offset"] = 0
  for i in range(1, len(file_paths)):
    offset_curr_vs_ref = calculate_offset_between_two(file_info[0].get("y"), file_info[i].get("y"))
    file_info[i]["offset"] = offset_curr_vs_ref
    # print(f"  -> Raw offset of '{file_info[0].get("basename")}' relative to '{file_info[i].get("basename")}': {offset_curr_vs_ref:.6f}s")

  
  file_info.sort(key=lambda x: x.get('offset'))
  
  min_offset = file_info[0].get("offset")
  # print(min_offset)
  
  for i in range(0, len(file_paths)):
    file_info[i]["offset"] -= min_offset
    
  file_info.sort(key=lambda x: x.get('index'))
  
  # print(*file_info,sep="\n")
  
  for i in range(0, len(file_paths)):
    print(f"File: {file_info[i].get('basename'):<30} | Delay from start: {file_info[i].get('offset'):9.5f} s")
  
  return file_info


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Calculate delays for N audio files relative to the earliest starting one.")
  parser.add_argument("audio_files", nargs='+', help="Paths to the audio files (e.g., file1.wav file2.mp3 ...).")

  args = parser.parse_args()

  if len(args.audio_files) < 1:
    print("Error: Please provide at least one audio file.")
    exit(1)
  
  for f_path in args.audio_files:
    if not os.path.exists(f_path):
      print(f"Error: File not found: {f_path}")
      exit(1)

  if len(args.audio_files) == 1:
     print(f"Only one file provided: {os.path.basename(args.audio_files[0])}")
     print("No delay calculation needed. Trim amount: 0.000 ms")
     exit(0)


  delays = calculate_delays_for_n_files(args.audio_files)
  
  with open(Path(args.audio_files[0]).stem+".lof", "w") as f:
    f.write("window # open new window\n")
    for i in range(len(delays)):
      f.write(f"file \"{delays[i]['path']}\" offset {delays[i]['offset']}\n")
  
  print("To delay songs run these")
  for i in range(len(delays)):
    print(f'ffmpeg -i \"{Path(delays[i]["path"])}\" -af \"adelay={(delays[i]["offset"]*1000)}ms:all=1\" -c:a pcm_s16le \"{Path(delays[i]["path"]).stem}.offset.wav\"')
  # The detailed print is now inside calculate_delays_for_n_files