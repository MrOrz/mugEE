#!/bin/bash

rm *-mask.png

for i in `ls *.png`; do
  echo "Generating mask for $i"
  convert $i -channel Alpha -negate -separate ${i%.png}-mask.png
done

echo 'Done!'
