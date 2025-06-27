import subprocess
import os
import logging
import json

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][%(levelname)s][%(name)s] %(message)s')
ripLogger = logging.getLogger("CDrip")

def rip_cd(trackNum: int,cdDevice: str,dir: str=".rawRip", samplerate: int=44100) -> list[str]:
  if not os.path.exists(dir):
    os.makedirs(dir)
  for i in range(1, int(trackNum) + 1):
    ripLogger.info(f"Ripping track {i} of {trackNum}")
    filename = os.path.join(dir,f"T{i:02d}.wav")
    if os.path.isfile(filename):
      ripLogger.info(f"{filename} already exists, skipping")
    else:
      while not os.path.isfile(filename):
        command = [
          "cvlc",
          f"{cdDevice}",
          "--noloop",
          f"--cdda-track={i}",
          f'--sout=#transcode{{vcodec=none,acodec=s16l,channels=2,samplerate={samplerate}}}:standard{{access="file",mux="wav",dst="{filename}"}}',
          "vlc://quit"
        ]
        subprocess.run(command,stderr=subprocess.DEVNULL)
        if not os.path.isfile(filename):
          ripLogger.error(f"Retrying to rip track {i}")
  wav_files = [os.path.join(dir,f) for f in os.listdir(dir) if f.endswith('.wav')]
  return sorted(wav_files)
      
def cdTrackNames(cdDevice: str) -> list[str]:
  languages = []
  while len(languages) < 1:
    if languages != []:
      ripLogger.error("No songs found, trying again...")
    command = [
      "cd-info",
      "--no-header",
      "-q",
      f"-C {cdDevice}"
      ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = result.stdout.decode("utf-8")
    languages = output.strip().split("Language")
  ripLogger.info(f"Found languages: {languages}")
  for i in range(1, len(languages)):
    if languages[i].split("'")[1] == "English":
      index = i
    else:
      ripLogger.error("No English found")
      return None
  output = languages[index].split("CD-TEXT for Track")
  track_titles = []
  for i in range(1, len(output)):
    track_info = output[i].split(":")
    if len(track_info) > 2 and "TITLE" in track_info[1]:
        title = track_info[2].strip().split("\n")[0]
        track_titles.append(title)
    else:
      ripLogger.error(f"Couldn't find track {i}")
      track_titles.append(None)
  ripLogger.info(f"Found {len(track_titles)} tracks with titles {track_titles}")

  # Save track titles to JSON file
  json_filename = os.path.join(".rawRip", "track_titles.json")
  if not os.path.exists(".rawRip"):
    os.makedirs(".rawRip")
  with open(json_filename, 'w') as f:
    json.dump(track_titles, f, indent=4)
  ripLogger.info(f"Track titles saved to {json_filename}")

  return track_titles

if __name__ == '__main__':
  print("START")
  cd = "cdda:///dev/sr0"
  trackNames = cdTrackNames(cdDevice=cd)
  tracks = rip_cd(len(trackNames), cdDevice=cd)
  for i in range(len(tracks)):
    print(f"{tracks[i]} - {trackNames[i]}")
  
  # print(f"Ripped tracks: {tracks}")
  # print(f"Track names: {trackNames}")
  