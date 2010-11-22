c      PARAMETRE POUR LA DECONVOLUTION PRIVEE: param_dec.f
c      ---------------------------------------------------

       integer nbr1,nbr2,xy1,xy2,npic,nbg
       parameter(nbr1= 1024,nbr2= 4096,xy1= 32,xy2= 64)
       parameter(npic= 5,nbg= 3)

cc     npic: max number of point sources in 1 frame
cc     nbg: max number of images to deconv. simultaneously
cc     nbr1: number of pixels in input image
cc     nbr2: number of pixels in output image
cc     xy1: linear size of input image
cc     xy2: linear size of output image

