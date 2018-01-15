#!/bin/bash
# Original:
# https://stackoverflow.com/a/25498342/2877698
# I've made a couple of tweaks; nothing substantial
start=$(date +%s%3N)
eval $(xdotool getmouselocation --shell)
xwd -root -screen -silent \
    | convert xwd:- -crop "1x1+$X+$Y" txt:- \
    | awk '/^[^#]/{\
        a = gensub(/\(|\)/, "", "g", $2);\
        split(a, b, ",");\
        printf "RGB: (%d,%d,%d)\n", b[1] / 256, b[2] / 256, b[3] / 256;\
    }'
end=$(date +%s%3N)

echo "Mouse: ($X,$Y)"
echo "Start: $start"
echo "End: $end"
echo "Difference: $(($end - $start))"
