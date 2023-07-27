re='^[0-9]+$'


while true
do

hw=$(aplay -l | grep USB | head -c 6 | tail -c 1)

if ! [[ $hw =~ $re ]] ; then
   echo "error: Not a number" >&2;
	sleep 1
else
echo "$hw is a number"
break
fi

done


cat > /home/matthew/.asoundrc << EOF
pcm.!default {
  type asym
  playback.pcm {
    type plug
    slave.pcm "output"
  }
  capture.pcm {
    type plug
    slave.pcm "input"
  }
}

pcm.output {
  type hw
  card $hw
}

ctl.!default {
  type hw
  card $hw
}
EOF
