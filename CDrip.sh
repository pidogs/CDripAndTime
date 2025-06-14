if [[ ! "$1" =~ ^-d ]]; then
  echo "Error: Missing -d flag. Please use -d followed by a number."
  exit 1
fi
t=10
while getopts ":d:t:" opt; do
  case $opt in
    d)
      d="${OPTARG}"
      ;;
    t)
      t="${OPTARG}"
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done

if [[ ! "$d" =~ ^[0-9]+$ ]]; then
  echo "Error: Invalid disk. Please provide a number after -d."
  exit 1
fi

if [[ ! "$t" =~ ^[0-9]+$ ]]; then
  echo "Error: Invalid track. Please provide a number after -t." >&2
  exit 1
fi

for i in $(seq 1 $t); do
	if [ -f "D${d}T${i}.wav" ]; then
		echo "D${d}T${i}.wav already exits skipping"
	else
		echo "Ripping D${d}T${i}.wav"
		while [ ! -f "D${d}T${i}.wav" ]
		do
		cvlc cdda:///dev/sr0 --noloop --cdda-track $i --sout="#transcode{vcodec=none,acodec=s16l,channels=2,samplerate=44100}:standard{access="file",mux="wav",dst="D${d}T${i}.wav"}" vlc://quit
		done
	fi
done
eject
