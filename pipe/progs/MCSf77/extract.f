      implicit none

c     DECLARATIONS
c     ------------

      integer nb1,nb2,nbg,xy1,xy2
      parameter(xy1=3000,xy2=3000,nb1=xy1*xy1,nb2=xy2*xy2,nbg=4)

      integer nax1,nax2,k,i,j,indice,indice2,debx,deby,taille,m,pas
      integer taille2,deconv,tailleg,dx,dy,ind2
      real*4 tab(nb1),psf(nb2),psfsig(nb2),g(nb2),sig(nb2)
      real*4 c(2,nbg),max,gain,ecart,expo,cd1,cd2
      character*70 entete
      character*20  nom,nom2,nom3
      character*1 lettre1,lettre2,question

c     OUVERTURE DU FICHIER EXTRACT.TXT
c     --------------------------------

      open(unit=1,file='extract.txt')
      read(1,'(A70)') entete
      read(1,'(A48,A20)') entete,nom
      read(1,'(A70)') entete
      read(1,'(A48,I4)') entete,m
      read(1,'(A70)') entete
      read(1,'(A48,I4)') entete,taille
      if (m .gt. 4) then
         write(*,*) 'Le nombre d images est supérieur à 4'
         stop
      end if
      if ( m .eq. 1) then
         tailleg = taille
      else
         tailleg = taille*2
      end if
      expo = log(real(taille))/log(2.)
      if (int(expo) .ne. expo) then
      write(*,'(''Erreur: la taille n''''est pas une puissance de 2'')')
      stop
      end if
      read(1,'(A70)') entete
      read(1,'(A48,F16.10)') entete,gain
      read(1,'(A70)') entete
      read(1,'(A48,F16.10)') entete,ecart
      read(1,'(A70)') entete
      read(1,'(A48,A1)') entete,question
      if (question .eq. 'n') then
         pas = 1
      else if (question .eq. 'y') then
         pas = 2
      else
         write(*,'(''Erreur: mauvaise entree dans extract.txt'')')
         stop
      end if
      read(1,'(A70)') entete
      read(1,'(A70)') entete
      do i=1,m
         read(1,*) c(1,i),c(2,i)
      end do
      read(1,'(A70)') entete
      read(1,'(A48,A1)') entete,question
      if (question .eq. 'y') then
         deconv = 1
         read(1,'(A70)') entete
         read(1,'(A48,I4)') entete,taille2
         expo = log(real(taille2))/log(2.)
         if (int(expo) .ne. expo) then
            write(*,
     &     '(''Erreur: la taille n''''est pas une puissance de 2'')')
            stop
         end if
         read(1,'(A70)') entete
         read(1,'(A70)') entete
         read(1,*) cd1,cd2
      else
         deconv = 0
      end if
      close(unit=1)

c     OUVERTURE DE L'IMAGE
c     --------------------

      do i=1,tailleg*tailleg
         psf(i) = 0.
         psfsig(i) = 0.
      end do

      call openima(nom,nax1,nax2,tab)

c     EXTRACTION DES IMAGES PSF ET PSFSIG
c     -----------------------------------

      do k=1,m
         max = 0.
         debx = c(1,k) - int(taille/2) - 1
         deby = c(2,k) - int(taille/2) - 1
c         write(*,*) c(1,k),c(2,k),debx,deby
         if (k .eq. 1) then
            dx = 0
            dy = 0
         else if (k .eq. 2) then
            dx = taille
            dy = 0
         else if (k .eq. 3) then
            dx = 0
            dy = taille
         else if (k .eq. 4) then
            dx = taille
            dy = taille
         end if
         do j=1,taille
            ind2 = (dy+j-1)*tailleg
            do i=1,taille
               indice = ind2 + dx+i 
               indice2 = (j+deby-1)*nax1 + i+debx
               psf(indice) = tab(indice2)
               psfsig(indice) =1./sqrt((psf(indice)/gain)+(ecart*ecart))
               if (psf(indice) .gt. max) max = psf(indice)
            end do
         end do       
      end do

      nom2 = 'g001.fits'
      nom3 = 'sig001.fits'
c      write(*,*) tailleg
      call makeima(nom2,tailleg,psf)
      call makeima(nom3,tailleg,psfsig)

c     ICI : CREER UNE IMAGE 128 SUR 128 CONTENANT LES IMAGES DES ETOILES DE PSF (4 MAX)
c     ON COMMENCE EN BAS A GAUCHE PUIS BAS DROITE PUIS HAUT GAUCHE PUis HAUT DROIT
c     IDEM 1/SIGMA
c     ON MET LES PARTIES DE L'IMAGE NON REMPLIES A ZERO (EN TOUT CAS POUR LES 1 SUR SIGMA.

      
      if (deconv .eq. 1) then
         debx = cd1 - int(taille2/2) - 1
         deby = cd2 - int(taille2/2) - 1
         do j=1,taille2
            do i=1,taille2
               indice2 = (j+deby-1)*nax1 + i+debx
               indice = (j-1)*taille2+i
               g(indice) = tab(indice2)
               if (((g(indice)/gain)+(ecart*ecart)).lt.0.) then
                 write(*,*) j,i,'pixel avec nan'
               end if 
               sig(indice) = 1/sqrt((g(indice)/gain)+(ecart*ecart))
            end do
         end do
         nom2 = 'g.fits'
         call makeima(nom2,taille2,g)
         nom3 = 'sig.fits'
         call makeima(nom3,taille2,sig)
      end if
      
      end


c     ---------------------
c     SUBROUTINE: openima
c     ---------------------

      subroutine openima(name,xpix,ypix,data)

      implicit none

      integer xpix,ypix
      integer status,unit,readwrite,blocksize,group
      integer nfound_in,naxes(2),npix,fpix

      real*4 data(xpix*ypix)
      real*4 null

      logical anynull

      character name*20

      status=0     
      call ftgiou(unit,status)
      readwrite=0
      blocksize=2880
      call ftopen(unit,name,readwrite,blocksize,status)
      call ftgknj(unit,'NAXIS',1,2,naxes,nfound_in,status)
      npix=naxes(1)*naxes(2)
      xpix=naxes(1)
      ypix=naxes(2)
      group=1
      fpix=1
      null=0.
      call ftgpve(unit,group,fpix,npix,null,data,anynull,status)
      call ftclos(unit,status)
      call ftfiou(unit,status)   
      
      if (status.gt.0) call printerror(status)

      return
      end

c     ---------------------
c     SUBROUTINE: makeima
c     ---------------------

      subroutine makeima(name,xpix,data)
 
      implicit none

      integer status,unit,blocksize
      integer xpix,fpixel,nelement
      integer bitpix
      integer naxes(2)
      integer group
      real*4 data(xpix*xpix)
      logical extend,simple
      character name*20

      status=0
      call delfil(name,status)
      call ftgiou(unit,status)
      blocksize=2880
      call ftinit(unit,name,blocksize,status)
      simple=.true.
      extend=.true.
      bitpix=-32
      naxes(1)=xpix
      naxes(2)=xpix
      call ftphpr(unit,simple,bitpix,2,naxes,0,1,extend,status)
      if (status.gt.0) then
         call printerror(status)
         stop
      end if
      group = 1
      fpixel = 1
      nelement = xpix*xpix
      call ftppre(unit,group,fpixel,nelement,data,status)
      call ftclos(unit,status)
      call ftfiou(unit,status)
      if (status.gt.0) then
         call printerror(status)
         stop
      end if

      return
      end

c     ------------------------
c     SUBROUTINE: printerror
c     ------------------------

      subroutine printerror(status)


      integer status
      character errtext*30,errmessage*80

      if (status .le. 0) return

      call ftgerr(status,errtext)
      print *,'FITSIO Error Status =',status,': ',errtext

 1    call ftgmsg(errmessage)
      do while (errmessage .ne. ' ')
          print *,errmessage
 2        call ftgmsg(errmessage)
      end do

      return
      end

c     --------------------
c     SUBROUTINE: delfil
c     --------------------

      subroutine delfil(filename,status)


      integer status,unit,blocksize
      character*(*) filename
 
      if (status .gt. 0)return

 1    call ftgiou(unit,status)

 2    call ftopen(unit,filename,1,blocksize,status)

      if (status .eq. 0)then
 3        call ftdelt(unit,status)
      else if (status .eq. 103)then
          status=0
 4        call ftcmsg
      else
          status=0
 5        call ftcmsg
          call ftdelt(unit,status)
      end if

 6    call ftfiou(unit, status)
      
      return
      end
