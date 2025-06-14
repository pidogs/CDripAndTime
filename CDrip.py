import subprocess
import os
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s][%(name)s] %(message)s')
ripLogger = logging.getLogger("CDrip")

def rip_cd(t,cdDevice,dir=".rawRip", samplerate=44100):
  if not os.path.exists(dir):
    os.makedirs(dir)
  for i in range(1, int(t) + 1):
    ripLogger.info(f"Ripping track {i} of {t}")
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
  wav_files = [f for f in os.listdir(dir) if f.endswith('.wav')]
  return sorted(wav_files)
      
def cdTrackNames(cdDevice,t=None):
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
  return track_titles

if __name__ == '__main__':
  # Example usage:
  cd = "cdda:///dev/sr0"
  trackNames = cdTrackNames(cdDevice=cd)
  tracks = rip_cd(len(trackNames), cdDevice=cd)
  print(f"Ripped tracks: {tracks}")
  print(f"Track names: {trackNames}")
  