

To make MPEG4 movies out of the pngs :

convert the pngs to jpg :

mogrify -format jpg -quality 100% *.png

(eventually rename the files "squencially" 0001, 0002, ... in any order you like)


Encode using :
explicitly specify the number of frames to be sure you get 1 mpeg frame for each image

ffmpeg -i %04d.jpg -dframes 2145 -sameq test2.mp4







###################################################



ffmpeg -i %04d.jpg -r 20 -sameq test.mp4
this skipps some frames...



ffmpeg -i %03d.jpg -r 20 -qmax 2 test.mov

not working :
ffmpeg -i %03d.jpg -r 20 -vcodec h264 test.mov

rsync -vr --stats ~/Desktop/HCT/ HCTnewNov2008/
