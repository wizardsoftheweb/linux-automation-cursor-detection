#!/bin/bash
# Original:
# https://stackoverflow.com/a/25498342/2877698
# I've made a couple of tweaks; nothing substantial
start=$(date +%s%3N)
eval $(xdotool getmouselocation --shell)
xwd -root -screen -silent | convert xwd:- -crop "1x1+$X+$Y" txt:- | awk '/^[^#]/{ print gensub("srgb", "RGB: ", "g", $4) }'
end=$(date +%s%3N)

echo "Start: $start"
echo "End: $end"
echo "Difference: $(($end - $start))"
