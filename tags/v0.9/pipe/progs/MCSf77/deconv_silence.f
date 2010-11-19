c     PROGRAM OF DECONVOLUTION
c     ------------------------

c     VARIABLE DECLARATION
c     --------------------

      implicit none

      include 'param_dec.f'


      real*4 g(nbr1,nbg),sig2(nbr1,nbg),lambda(nbr1)
      real*4 s(nbr2,nbg),trs(nbr2,nbg),sig3(nbr1,nbg)

      real*4 a(npic,nbg),b,c(2,npic),z(2,nbg)
      real*4 p(nbr2),delta(2,nbg),manaly(6),alpha

      real*4 ss(2*xy2,nbg),lamb(nbr2),tab(nbr2)
      real*4 rr(nbr2),frf(nbr2),tmp(nbr2),tmp2(nbr2),stmp(2*xy2)
      real*4 srr(2*xy2),strs(2*xy2,nbg),stmp2(2*xy2)
      real*4 t(nbr2,nbg),st(2*xy2,nbg)
      real*4 tmp3(nbr1),tmp4(nbr1),poids(nbr2)
      real*4 idlc,idfc,somme
      real*4 nda(npic),ndc,ndf,ndz(2),ndd,k1,kk
      real*4 ndmanaly(6),cxmask,cymask,mask(nbr2)
      real*4 dz(2,nbg),dd(2,nbg),dmanaly(6),fwhm2
      real*4 da(npic,nbg),dc(2,npic),df(nbr2)
      real*4 fret,som,multi(3),expo,t1,t2,qimin
      real*4 ndamin(npic),ndcmin,ndfmin,ndzmin(2)
      real*4 nddmin,ndmamin(6),k3,kk3,v,fwhm(nbg),bg(nbg),d

      integer n1,n2,m,nxy1,nxy2,cent,half,i2,j2,m2,nbch,i3
      integer np,k,iter,idl,idf,vari_int,maskmodel,raymask
      integer nax1,nax2,itmax,module,ind,amodel,rayon_coupure
      integer pas,i,ii,j,k2,l,ind1,ind2,indice,testh,posi
      integer ndels,dels(npic),numdels(npic)
      
      character*20 name
      character*20 lambda_name,fond_name,idln,idfn
      character*20 entree,sortie,sortie2,results
      character*70 entete
      character*1 lettre1,question,lettre2,lettre3,lettre4
      character*9 fin
      character*42 ligne
        
      common /source_delete/ dels,ndels
      common /param/ nxy1,nxy2,pas
      common /parametre_alpha/ b,alpha
      common /gr1/ g,s,sig2,ss
      common /lambd/ idl,idlc,idln
      common /trans/ trs,strs
      common /delta2/ da,dc,df,dz,dd
      common /deltacons/ nda,ndc,ndf,ndz,ndd
      common /deltacons2/ ndamin,ndcmin,ndfmin,ndzmin
      common /deltacons3/ nddmin
      common /model/ manaly
      common /model3/ dmanaly,ndmanaly,ndmamin
      common /sig/ sig3
      common /entropie/ rr,frf,srr
      common /psft/ t,st
      common /variables/ p,z,a,c,delta
      common /tailles/ n1,n2,np,m,m2
      common /positif/ posi
      common /gaussienne/ fwhm,bg
      common /variation_intensite/ vari_int
      common /masque/ cxmask,cymask,raymask
      common /masque2/ mask
      common /digit/ nbch

c     START OF THE PROGRAM
c     --------------------


c     READING OF FILE:  DECONV2.DAT:
c     - - - - - - - - - - - - - - -

      open(unit=4,file='deconv.txt')

      read(4,'(A70)') entete
      read(4,'(A42,I4)') ligne,nbch
      read(4,'(A70)') entete
      read(4,'(A42,I4)') ligne,m
      read(4,'(A70)') entete
      read(4,'(A42,I4)') ligne,np
      read(4,'(A70)') entete
      read(4,'(A42,F16.10)') ligne,fwhm2
      if (fwhm2 .ge. 2.) then
         b = 4.*log(2.)/(fwhm2*fwhm2)
      else
         write(*,*) 'FWHM < 2 --> erreur d''échantillonnage'
         stop
      end if


c     CHANGEMENT: Largeurs à mi-hauteur variable.
c     on ne lit plus ces deux lignes dans le fichier deconv.txt:
c     ----------------------------------------------------------
c      read(4,'(A70)') entete
c      read(4,'(A42,F16.10)') ligne,fwhm

c     On va lire les largeurs à mi-hauteur dans un fichier que je vais
c     appeller fwhm-des-G.txt
c     les largeurs à mi-hauteur y sont en colonnes.
c     ----------------------------------------------------------
      open(unit=1,file='fwhm-des-G.txt')
      do i=1,m
         read(1,*) fwhm(i)
         if (fwhm(i) .ge. 2.) then
            bg(i) = 4.*log(2.)/(fwhm(i)*fwhm(i))
         else
            write(*,*) 'FWHM < 2 --> erreur d''échantillonnage'
            stop
         end if
      end do


      read(4,'(A70)') entete
      read(4,'(A42,A1)') ligne,question
      if (question .eq. 'y') then
         amodel = 1
      else
         amodel = 0
      end if
      if (amodel .eq. 1) then
         read(4,'(A70)') entete
         read(4,'(A42,F16.10)') ligne,alpha
         if ((alpha .ne. 0.5) .and. (alpha.ne.0.125)) then
            write(*,*) 'Alpha doit valoir 0.5 ou 0.125'
            stop
         end if
         write(*,*) 'alpha: ',alpha
         read(4,'(A70)') entete
         read(4,'(A70)') entete
         read(4,'(A42,A1)') ligne,question
         if (question .eq. 'y') then
            maskmodel = 1
         else
            maskmodel = 0
         end if
         write(*,*) maskmodel
         if (maskmodel .eq. 1) then
            read(4,'(A70)') entete
            read(4,'(A42,F16.10)') ligne,cxmask
            read(4,'(A70)') entete
            read(4,'(A42,F16.10)') ligne,cymask
            read(4,'(A70)') entete
            read(4,'(A42,I4)') ligne,raymask
            read(4,'(A70)') entete
         else
            do i=1,7
               read(4,'(A70)') entete
            end do
         end if
      else
         do i=1,12
            read(4,'(A70)') entete
         end do
      end if
      read(4,'(A42,A1)') ligne,question
      if (question .eq. 'y') then
         rayon_coupure = 1
      else
         rayon_coupure = 0
      end if
      if (rayon_coupure .eq. 1) then
         read(4,'(A70)') entete
         read(4,'(A42,F16.10)') ligne,v
         read(4,'(A70)') entete
      else
         do i=1,3
            read(4,'(A70)') entete
         end do
      end if
      read(4,'(A42,A1)') ligne,question
      if (question .eq. 'y') then
         vari_int = 1
         m2 = m
      else
         vari_int = 0
         m2 = 1
      end if
      read(4,'(A70)') entete
      read(4,'(A42,A20)') ligne,entree
      read(4,'(A70)') entete
      read(4,'(A42,A20)') ligne,sortie
      read(4,'(A70)') entete
      read(4,'(A42,A20)') ligne,sortie2
      read(4,'(A70)') entete
      read(4,'(A42,I4)') ligne,itmax
      read(4,'(A70)') entete
      read(4,'(A42,F16.10)') ligne,qimin
      read(4,'(A70)') entete
      read(4,'(A42,I4)') ligne,module
      read(4,'(A70)') entete
      read(4,'(A42,A1)') ligne,question
      if (question .eq. 'y') then
         posi = 1
      else
         posi = 0
      end if
      read(4,'(A70)') entete
      read(4,'(A42,A1)') ligne,question
      if (question.eq.'y') then
         idl = 1
         read(4,'(A42,A20)') ligne,idln
      else
         idl = 2
         read(4,'(A42,F16.10)') ligne,idlc
      endif
      read(4,'(A70)') entete
      read(4,'(A42,A1)') ligne,question
      if (question.eq.'y') then
         idf = 1
         read(4,'(A42,A20)') ligne,idfn
      else
         idf = 2
         read(4,'(A42,F16.10)') ligne,idfc
      endif
      do i=1,3
         read(4,'(A70)') entete
      end do
      read(4,'(A42,I4)') ligne,ndels
      do i=1,3
         read(4,'(A70)') entete
      end do
      read(4,*) (numdels(i),i=1,ndels)
      do i=1,np
         dels(i) = 0
      end do
      do i=1,ndels
         dels(numdels(i)) = 1
      end do
      close(unit=4)


c     READING OF DATA FROM INPUT FILE 
c     - - - - - - - - - - - - - - - -

      open(unit=4,file=entree)
      do ii=1,3
         read(4,'(A70)') entete
      end do

      read(4,'(A42,F16.10)') ligne,k1
      read(4,'(A42,F16.10)') ligne,k3
      read(4,'(A70)') entete
      read(4,'(A42,F16.10)') ligne,ndc
      read(4,'(A42,F16.10)') ligne,ndcmin
      read(4,'(A70)') entete
      read(4,'(A42,F16.10)') ligne,ndf
      read(4,'(A42,F16.10)') ligne,ndfmin
      read(4,'(A70)') entete
      read(4,'(A42,F16.10)') ligne,ndz(1)
      read(4,'(A42,F16.10)') ligne,ndzmin(1)
      read(4,'(A42,F16.10)') ligne,ndz(2)
      read(4,'(A42,F16.10)') ligne,ndzmin(2)
      read(4,'(A70)') entete
      read(4,'(A42,F16.10)') ligne,ndd
      read(4,'(A42,F16.10)') ligne,nddmin
      if (amodel .eq. 1) then
         read(4,'(A70)') entete
         read(4,'(A42,F16.10)') ligne,kk
         read(4,'(A42,F16.10)') ligne,kk3
         read(4,'(A70)') entete
         read(4,'(A42,F16.10)') ligne,ndmanaly(1)
         read(4,'(A42,F16.10)') ligne,ndmamin(1)
         ndmanaly(2) = ndmanaly(1)
         ndmamin(2) = ndmamin(1)
         read(4,'(A70)') entete
         read(4,'(A42,F16.10)') ligne,ndmanaly(3)
         read(4,'(A42,F16.10)') ligne,ndmamin(3)
         read(4,'(A70)') entete
         read(4,'(A42,F16.10)') ligne,ndmanaly(4)
         read(4,'(A42,F16.10)') ligne,ndmamin(4)
         ndmanaly(5) = ndmanaly(4)
         ndmamin(5) = ndmamin(4)
         do i=1,4
             read(4,'(A70)') entete
         end do
      else
         do i=1,16
             read(4,'(A70)') entete
         end do
      end if
      do k=1,np
         read(4,*) (a(k,j),j=1,m2)
         read(4,*) c(1,k),c(2,k)
      end do
      do i=1,4
         read(4,'(A70)') entete
      end do
      do i=1,m
         read(4,*) z(1,i),z(2,i),delta(1,i),delta(2,i)
      end do
      if (amodel .eq. 1) then
         do i=1,4
            read(4,'(A70)') entete
         end do
         read(4,*) manaly(6),manaly(1),manaly(2),manaly(3),
     &             manaly(4),manaly(5)
      end if
      close(unit=4)

c     LOADING OF IMAGES
c     - - - - - - - - -
      do ii=1,m
         if (nbch .eq. 1) then
            do i=1,m
               lettre1 = char(48+ii)
               fin = lettre1 // '.fits'
            end do
         else if (nbch .eq. 2) then
            do i=1,m
               i2 = int(ii/10)
               lettre1 = char(48+i2)
               i2 = ii - i2*10
               lettre2 = char(48+i2)
               fin = lettre1 // lettre2 // '.fits'
            end do
         else if (nbch .eq. 3) then
            do i=1,m
               i2 = int(ii/100)
               lettre1 = char(48+i2)
               i2 = ii-i2*100
               i3 = int(i2/10)
               lettre2 = char(48+i3)
               i2 = i2-i3*10
               lettre3 = char(48+i2)
               fin = lettre1 // lettre2 // lettre3 // '.fits'
            end do
         else if (nbch .eq. 4) then
            do i=1,m
               i2 = int(ii/1000)
               lettre1 = char(48+i2)
               i2 = ii-i2*1000
               i3 = int(i2/100)
               lettre2 = char(48+i3)
               i2 = i2-i3*100
               i3 = int(i2/10)
               lettre3 = char(48+i3)
               i2 = i2-i3*10
               lettre4 = char(48+i2)
               fin = lettre1 // lettre2 // lettre3 // lettre4 // '.fits'
            end do
         else 
            write(*,*) 'nombre d''images > 9999 => pas prévu!'
            stop
         end if

         name = 'g' // fin
         call openima(name,nax1,nax2,tmp3)
         expo = log(real(nax1))/log(2.)
         if (nax1 .ne. nax2) then
            write(*,*) 'Erreur: image g.fits non carrée'
            stop
         else if (int(expo) .ne. expo) then
            write(*,*) 'Erreur: taille de g.fits pas une puissance de 2'
            stop
         end if
         n1 = nax1*nax1
         nxy1 = nax1

         name = 's' // fin
         call openima(name,nax1,nax2,tmp)
         expo = log(real(nax1))/log(2.)
         if (nax1 .ne. nax2) then
            write(*,*) 'Erreur: image s.fits non carrée'
            stop
         else if (nax1 .ne. xy2) then
            write(*,*) 'Erreur: XY2 pas le meme dans images et param.f'
            write(*,*) 'utilise ini_dec.f'
         else if (int(expo) .ne. expo) then
            write(*,*) 'Erreur: taille de s.fits pas une puissance de 2'
            stop
         end if
         n2 = nax1*nax1
         nxy2 = nax1
         pas = int(xy2/xy1)

         name = 'sig' // fin
         call openima(name,nax1,nax2,tmp4)
         expo = log(real(nax1))/log(2.)
         if (nax1 .ne. nax2) then
            write(*,*) 'Erreur: image sig.fits non carrée'
            stop
         else if (nax1 .ne. xy1) then
            write(*,*) 'Images g.fits et sig.fits pas de meme taille or'
            write(*,*) 'Erreur: XY1 pas le meme dans images et param.f'
            write(*,*) 'utilise ini_dec.f'
            stop
         else if (int(expo) .ne. expo) then
            write(*,*) 'Erreur: taille sig.fits pas une puissance de 2'
            stop
         end if

         do i=1,n1
            g(i,ii) = tmp3(i)
            sig2(i,ii) = tmp4(i)*tmp4(i)
         end do

c       FONCTION POIDS POUR TRONQUER LA PSF TRANSPOSEE (A NE FAIRE QU'UNE FOIS)
c        - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
         if ((ii .eq. 1) .and. (rayon_coupure .eq. 1)) then
            half = int((nxy2/2)+1)
            do j=1,nxy2
               t2 = (0.94*(j-half))/v
               do i=1,nxy2
                  ind = (j-1)*nxy2+i
                  t1 = (0.94*(i-half))/v
                  tmp2(ind) = exp(-((t1*t1+t2*t2)**3))
               end do
            end do         
            name = 'poids.fits'
            call makeima(name,nxy2,tmp2)

            half = int(nxy2/2)
            do j=1,nxy2
               j2 = j+half
               if (j2 .gt. nxy2) j2 = j2-nxy2
               ind = (j-1)*nxy2
               ind2 = (j2-1)*nxy2
               do i=1,nxy2
                  i2 = i+half
                  if (i2 .gt. nxy2) i2 = i2-nxy2
                  poids(ind+i) = tmp2(ind2+i2)
              end do
            end do
            name = 'poids2.fits'
            call makeima(name,nxy2,poids)
         end if


         do j=1,nxy2
            do i=1,nxy2
               ind1 = i + (j-1)*nxy2
               ind2 = j + (i-1)*nxy2
               tmp2(ind2) = tmp(ind1) 
            end do
         end do

         if (rayon_coupure .eq. 1) then
             somme = 0.
             do i=1,n2
               tmp2(i) = tmp2(i)*poids(i)
               somme = somme + tmp2(i)
             end do
             do i=1,n2
                tmp2(i) = tmp2(i)/somme
             end do
         end if

         call rlft2(tmp,stmp,nxy2,1)
         call rlft2(tmp2,stmp2,nxy2,1)

         do i=1,2*nxy2
            ss(i,ii) = stmp(i)
            strs(i,ii) = stmp2(i)
         end do
         do i=1,n2
            s(i,ii) = tmp(i)
            trs(i,ii) = tmp2(i)
         end do            
      end do

c     ===========================================
c     CREATION DU MASQUE POUR LE MODEL ANALYTIQUE
c     ===========================================
c      write(*,*) maskmodel,nxy2,cxmask,cymask,raymask
      if (maskmodel .eq. 1) then
         do j=1,nxy2
            ind2 = (j-1)*nxy2
            t2 = (j-cymask)*(j-cymask)
            do i=1,nxy2
               ind = ind2+i
               mask(ind) = 1.
               t1 = (i-cxmask)*(i-cxmask)
               d = sqrt(t1+t2)
               if (d .ge. real(raymask)) then
                  mask(ind) = 0.
               else if (d .lt. real(raymask)) then
                  mask(ind) = 1.
               end if
            end do
         end do
      else
         do i=1,n2
            mask(i) = 1.
         end do
      end if
         results = 'mask.fits'
         call makeima(results,nxy2,mask)

c     CREATION DE LA TABLE R:
c     - - - - - - - - - - - - 
      som = 0.
      cent = (nxy2/2+1)
      do j=1,nxy2
         t2 = j-cent
         ind = (j-1)*nxy2
         do i=1,nxy2
            t1 = i-cent
            ind = ind+1
            tmp(ind) = exp(-b*(t1*t1+t2*t2))
            som = som + tmp(ind)
         end do
      end do
      half = int(nxy2/2)
      do j=1,nxy2
         j2 = j+half
         if (j2 .gt. nxy2) j2 = j2-nxy2
         ind = (j-1)*nxy2
         ind2 = (j2-1)*nxy2
         do i=1,nxy2
            i2 = i+half
            if (i2 .gt. nxy2) i2 = i2-nxy2
            rr(ind+i) = tmp(ind2+i2)/som
         end do
      end do
      call rlft2(rr,srr,nxy2,1)

      half = int(nxy2/2)
      do ii=1,m
         do i=1,2*nxy2
            stmp(i) = ss(i,ii)
         end do
         do i=1,n2
            tmp(i) = s(i,ii) 
         end do            
         call produit(tmp,rr,stmp,srr,nxy2)
         call rlft2(tmp,stmp,nxy2,-1)
c         results = 't.fits'
c         call makeima(results,nxy2,tmp)
c         stop
         call rlft2(tmp,stmp,nxy2,1)
         do i=1,2*nxy2
            st(i,ii) = stmp(i)
         end do
         do i=1,n2
            t(i,ii) = tmp(i)
         end do            
      end do


c     INITIALISATION DES DONNEES
c     - - - - - - - - - - - - - -

c      write(*,*) 
      if (amodel .eq. 1) then
c         write(*,*) 'DECONVOLUTION AVEC MODELE ANALYTIQUE'
      else
c         write(*,*) 'DECONVOLUTION SANS MODELE ANALYTIQUE'        
      end if
c      write(*,*)
c      write(*,*) '============ Valeurs initiales ================'
      do k=1,np
         nda(k) = a(k,1)*k1/(100.)
         ndamin(k) = a(k,1)*k3/(100.)
c         write(*,'(A10,$)') ' Sources : '
         do j=1,m2
            da(k,j) = a(k,j)*k1/(100.)
c            write(*,'(E12.6,A1,$)') a(k,j),' '
         end do
         dc(1,k) = ndc
         dc(2,k) = ndc
c         write(*,*) c(1,k),c(2,k)       
      end do
      do j=1,m
         if (j .eq. 1) then
            dz(1,j) = 0.
            dz(2,j) = 0.
            dd(1,j) = 0.
            dd(2,j) = 0.
         else
            dz(1,j) = ndz(1)
            dz(2,j) = ndz(2)
            dd(1,j) = ndd
            dd(2,j) = ndd
         end if
c         write(*,*) 'z1 z2 : ',z(1,j),z(2,j)
c         write(*,*) 'delta : ',delta(1,j),delta(2,j)
      end do
      if (amodel .eq. 1) then
         ndmanaly(6) = manaly(6)*kk/100.
         ndmamin(6) = manaly(6)*kk3/100.
         do j=1,6
            dmanaly(j) = ndmanaly(j)
         end do
c         write(*,*) 'Modèle Io    : ',manaly(6)
c         write(*,*) 'Modèle A B C : ',manaly(1),manaly(2),manaly(3)
c         write(*,*) 'Modèle Cx Cy : ',manaly(4),manaly(5)
      end if
c      write(*,*) '------------------------------------------------'
c      write(*,*)

c     INITIALISATION DE LA TABLE LAMBDA
c     - - - - - - - - - - - - - - - - - -

      if (idl .eq. 1) then
         lambda_name = idln
         call openima(lambda_name,nax1,nax2,lamb)
         if (nax1 .eq. nxy1) then
            do ii=1,m 
               do j=1,n1
                  lambda(j) = lamb(j)
               end do
            end do
         else
            do j=1,nxy1
               do ii=1,nxy1
                  ind1 = nxy2*pas*(j-1)+pas*(ii-1)
                  indice = (j-1)*nxy1+ii
                  lambda(indice) = 0.
                  do l=1,pas
                     ind2 = (l-1)*nxy2
                     do k2=1,pas
                        lambda(indice) = lambda(indice) + 
     &                                   lamb(ind1+k2+ind2)  
                     end do
                  end do
                  lambda(indice) = lambda(indice)/real(pas*pas)
               end do
            end do
         end if
      else
         do j=1,n1
            lambda(j) = idlc
         end do
      end if

c     CALCUL DE 1/(SIGMA AU CARRE) ET LAMBDA/(SIGMA AU CARRE):
c     - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

      do ii=1,m
         do j=1,n1
            sig3(j,ii) = sig2(j,ii)
            sig2(j,ii) = lambda(j)*sig2(j,ii)
         end do
      end do
         
c     LECTURE DE L IMAGE DU FOND INITIAL :
c     - - - - - - - - - - - - - - - - - - -
      if (idf .eq. 1) then
         fond_name = idfn
         call openima(fond_name,nax1,nax2,p)
         if (posi .eq. 1) then
            do j=1,n2
               if (p(j) .lt. 0.) p(j) = 0.
            end do
         end if
      else
         do j=1,n2
            p(j) = idfc
         end do
      end if
      do j=1,n2
         df(j) = ndf
      end do



      open(unit=1,file=entree)
      open(unit=3,file=sortie2)
      do i=1,35
         read(1,'(A70)') entete
         write(3,'(A70)') entete
      end do
      close(unit=1)

      open(unit=2,file=sortie)
      write(2,'(A12)') ' Résultats : '
      write(2,'(A12)') '============ '
      write(2,*)

c     DEBUT DE LA MINIMISATION :
c     - - - - - - - - - - - - - -

      if (amodel .eq. 1) then
c        MINIMISATION AVEC LE MODELE ANALYTIQUE
c        ---------------------------------------
         call minimi_model(iter,itmax,module,qimin)
         write(2,'(A34,I4)') 
     &       'Nombre d''itérations dans minimi_model  : ',iter 
         call decompos_model(1)
      else
c        MINIMISATION SANS LE MODELE ANALYTIQUE
c        ---------------------------------------
         call minimi(iter,itmax,module,qimin)
         write(2,'(A34,I4)') 'Nombre d''itérations dans minimi  : ',iter 
         call decompos(1)
      end if
c      write(*,*)
c      write(*,*) 'FIN DE LA DECONVOLUTION'

      close(unit=2)
      close(unit=3)

      end 

C     ==============================================================================================
C     ==============================================================================================
c         A     V       V EEEEEEEEE  CCCCCCCC      M       M  OOOOOOO  DDDDDDDD  EEEEEEEEE L
c        A A     V     V  E         C              MM     MM O       O D       D E         L
c       A   A     V   V   EEEEE     C              M M   M M O       O D       D EEEEE     L 
c      AAAAAAA     V V    E         C              M  M M  M O       O D       D E         L 
c     A       A     V     EEEEEEEEE  CCCCCCCC      M   M   M  OOOOOOO  DDDDDDDD  EEEEEEEEE LLLLLLLLL
C     ==============================================================================================
C     ==============================================================================================

c     ------------------------
c     SUBROUTINE: minimi_model
C     ------------------------
c     MINIMISATION BY DECREASING STEPS.
c     ---------------------------------

      subroutine minimi_model(iter,itmax,modu,qimin)

      implicit none

      include 'param_dec.f'

      real*4 eps
      integer iter,itmax,modu
      parameter (eps=1.E-10)

      real*4 z(2,nbg),p(nbr2),delta(2,nbg),a(npic,nbg),c(2,npic)
      real*4 da(npic,nbg),dc(2,npic),df(nbr2),dz(2,nbg),dd(2,nbg)
      real*4 nda(npic),ndc,ndf,ndz(2),ndd
      real*4 manaly(6),dmanaly(6),ndmanaly(6)
      real*4 dfN(nbr2),pN(nbr2)
      real*4 daN(npic,nbg),dcN(2,npic),aN(npic,nbg),cN(2,npic)
      real*4 zN(2,nbg),deltaN(2,nbg),dzN(2,nbg),ddN(2,nbg)
      real*4 manalyN(6),dmanalyN(6)
      real*4 fp,qi,fpA,qimin,qiA
      real*4 ndamin(npic),ndcmin,ndfmin,ndzmin(2)
      real*4 nddmin,ndmamin(6),vecteurqi(10)
      real*4 xif(nbr2),xia(npic,nbg),xic(2,npic),xiz(2,nbg)
      real*4 xid(2,nbg),xima(6)
      real*4 xifA(nbr2),xiaA(npic,nbg),xicA(2,npic),xizA(2,nbg)
      real*4 xidA(2,nbg),ximaA(6),model(nbr2)
      integer testh,posi,n1,n2,m,np,indi,condi,its,i,ind,j,m2
      integer arret,arret2,ii,jj,aug

      common /delta2/ da,dc,df,dz,dd
      common /deltacons/ nda,ndc,ndf,ndz,ndd
      common /deltacons2/ ndamin,ndcmin,ndfmin,ndzmin
      common /deltacons3/ nddmin
      common /variables/ p,z,a,c,delta
      common /model/ manaly
      common /model3/ dmanaly,ndmanaly,ndmamin
      common /model2/ xima
      common /tailles/ n1,n2,np,m,m2
      common /derivees/ xif,xia,xic,xiz,xid
      common /minimum/ fp,qi
      common /positif/ posi
      common /modelpourminimi/ model

      aug = 0
      arret = 0
      arret2 = 1

c     CALCUL DU MINIMUM ET DES DERIVEES :
c     - - - - - - - - - - - - - - - - - -
      call inifunc_dfunc_model(p,z,a,c,delta,manaly)

      vecteurqi(1) = qi
      do i=2,10
         vecteurqi(i) = 100000.
      end do

      indi = m+2
      condi = indi*np


c     Sauvegarde des anciens pas, car si on dépasse 
c     le minimum, il faut revenir avec les anciens pas 
c     et les diviser par 2
c     - - - - - - - - - - - - - - - - - - - - - - - 
      do i=1,n2
         dfN(i) = df(i)
      end do
      do i=1,np
         do j=1,m2
            daN(i,j) = da(i,j)
         end do
         dcN(1,i) = dc(1,i)
         dcN(2,i) = dc(2,i)
      end do
      do j=1,m
         do i=1,2
            dzN(i,j) = dz(i,j)
            ddN(i,j) = dd(i,j)
         end do
      end do
      do i=1,6
         dmanalyN(i) = dmanaly(i)
      end do
      do i=1,2
         zN(i,1) = z(i,1)
         deltaN(i,1) = delta(i,1) 
      end do
      
      do its=1,itmax

c         write(*,*) its,' (M avec modèle)   min qi: ',fp,qi
         if (aug .eq. 0) then
c           write(*,*) '================================================'
         else
c           write(*,*) '************************************************'
c           write(*,*) 
           aug = 0
         end if
         iter = its

c        MODIFICATION DE F
c        - - - - - - - - -
         do i=1,n2
            if (xif(i) .lt. 0.) then
                pN(i) = p(i) + dfN(i)
            else
               if (posi .eq. 0) then
                  pN(i) = p(i) - dfN(i)
               else
                  if (p(i)-dfN(i) .ge. -(model(i))) then
                      pN(i) = p(i) - dfN(i)
                  else
                      pN(i) = -(model(i))
                  end if
              end if
            end if
         end do

c        MODIFICATION DE A, C1 ET C2
c        - - - - - - - - - - - - - - -
         do i=1,np
c            write(*,'(''   a...a c1 c2   : '',$)')
            do j=1,m2
               if (xia(i,j) .lt. 0.) then
                  aN(i,j) = a(i,j) + daN(i,j)
               else
                  aN(i,j) = a(i,j) - daN(i,j)
               end if
c               write(*,'(E12.6,A1,$)') aN(i,j),' '
            end do
            do j=1,2
               if(xic(j,i) .lt. 0.) then
                  cN(j,i) = c(j,i) + dcN(j,i)
               else
                  cN(j,i) = c(j,i) - dcN(j,i)
               end if
            end do
c            write(*,'(2(E12.6,A1))') cN(1,i),' ',cN(2,i),' '
         end do

c        MODIFICATION DE Z ET DELTA 
c           NOTE: LES PARAMETRES DE L IMAGE 1 NE SONT PAS MODIFIES
c        - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
c         write(*,*) '  z1  z2        : ',zN(1,1),zN(2,1)
c         write(*,*) '  delta1 delta2 : ',deltaN(1,1),deltaN(2,1)
         do i=2,m
            do j=1,2
               if (xiz(j,i) .lt. 0.) then
                  zN(j,i) = z(j,i) + dzN(j,i)
               else
                  zN(j,i) = z(j,i) - dzN(j,i)
               end if
               if (xid(j,i) .lt. 0.) then
                  deltaN(j,i) = delta(j,i) + ddN(j,i)
               else
                  deltaN(j,i) = delta(j,i) - ddN(j,i)
               end if
            end do
c            write(*,*) '  z1  z2        : ',zN(1,i),zN(2,i)
c            write(*,*) '  delta1 delta2 : ',deltaN(1,i),deltaN(2,i)
         end do

c        MODIFICATION DE Io A B C Cx Cy 
c        - - - - - - - - - - - - - - - 
         do i=1,6
            if (xima(i) .lt. 0.) then
               manalyN(i) = manaly(i) + dmanalyN(i)
            else
               manalyN(i) = manaly(i) - dmanalyN(i)
            end if
         end do
c         write(*,*) '  Modèle analytique: '
c         write(*,'(A13,E12.6)')'     Io    : ',manalyN(6)
c         write(*,'(A13,3(E12.6,A1))')'     A B C : ',manalyN(1),' ',
c     &                               manalyN(2),' ',manalyN(3),' '
c         write(*,'(A13,2(E12.6,A1))')'     Cx Cy : ',manalyN(4),' ',
c     &                                   manalyN(5),' '
c         write(*,*) '  f : ',pN(1),pN(512),pN(1024)

c        Sauvegarde des anciennes dérivées avant un nouveau 
c        calcul avec les nouvelles valeurs.
c        - - - - - - - - - - - - - - - - - - - - - - - - - -
         fpA = fp
         qiA = qi
         do i=1,n2
            xifA(i) = xif(i)
         end do
         do i=1,np
            do j=1,m2
               xiaA(i,j) = xia(i,j)
            end do
            xicA(1,i) = xic(1,i)
            xicA(2,i) = xic(2,i)
         end do
         do i=1,m
            xizA(1,i) = xiz(1,i)
            xizA(2,i) = xiz(2,i)
            xidA(1,i) = xid(1,i)
            xidA(2,i) = xid(2,i)
         end do
         do i=1,6
            ximaA(i) = xima(i)
         end do

c         write(*,*) '---------------------------------------'

c        BACKUP AUTOMATIQUE APRES X ITERATIONS:
c        - - - - - - - - - - - - - - - - - - - - 
         call inifunc_dfunc_model(pN,zN,aN,cN,deltaN,manalyN)

         ii = mod(its+1,10)
         jj = ii+1
         if (ii.eq.0) ii = 10
         vecteurqi(ii) = qi
         if (abs(abs(vecteurqi(ii)) - 
     &        abs(vecteurqi(jj))) .le. qimin) then
            write(*,*)
            write(*,*) '===================================='
            write(*,*) '  LA DIFFERENCE DE KHI CARRE ENTRE  '
            write(*,*) '  10 ITERATIONS EST INSIGNIFIANTE'
            write(*,*) '===================================='
            return
         end if

         if (mod(its,modu) .eq. 0) then
            write(2,*) 'Nombre d''itérations dans minimi  : ',iter 
            write(2,*) 'Nombre d''itérations dans gradient: 0'
            write(2,*) 
            call decompos_model(0)
            do j=1,(m+2)*np+m+13
               backspace(unit=2)
            end do
            do j=1,2*np+m+9
               backspace(unit=3)
            end do
         end if

c        Test la valeur du minimum:
c        Si elle diminue c'est que les valeurs étaient bonnes
c           et on en recalcule de nouvelles
c        Sinon on revient aux anciens pas et on les divise par 2
c        - - - - - - - - - - - - - - - - - - - - - - - - - - - -

         if (fpA .gt. fp) then

            if (arret .ne. 0) arret = 0

c           CHECK OF THE SIGN OF THE DERIVATIVES OF F 
c           AND MODIFICATION OF STEP.
c           - - - - - - - - - - - - - - - - - - - - - 
            do i=1,n2
               df(i) = dfN(i)
               if (xifA(i)*xif(i) .lt. 0.)  then
                  dfN(i) = df(i)/2.
               else
                  if (df(i)*1.1 .le. ndf) then
                     dfN(i)= df(i)*1.1
                  else
                     dfN(i)= df(i)
                  end if
               end if
               if (arret2.eq.1 .and. dfN(i) .gt. ndfmin) arret2 = 0 
               p(i) = pN(i)
            end do

c           CHECK OF THE SIGN OF THE DERIVATIVES OF A, C1 AND C2
c           AND MODIFICATION OF STEP.
c           - - - - - - - - - - - - - - - - - - - - - - - - - - 
            do i=1,np
               do j=1,m2
                  da(i,j) = daN(i,j)
                  if (xiaA(i,j)*xia(i,j) .lt. 0.) then
                     daN(i,j) = da(i,j)/2.
                  else
                     if (da(i,j)*1.1 .le. nda(i)) then
                        daN(i,j) = da(i,j)*1.1
                     else
                        daN(i,j) = da(i,j)
                     end if
                  end if
                  a(i,j) = aN(i,j)
                  if (arret2.eq.1 .and. daN(i,j).gt.ndamin(i)) arret2=0 
               end do
               do j=1,2
                  dc(j,i) = dcN(j,i)
                  if (xicA(j,i)*xic(j,i) .lt. 0.) then
                     dcN(j,i) = dc(j,i)/2.
                  else
                     if (dc(j,i)*1.1 .le. ndc) then
                       dcN(j,i) = dc(j,i)*1.1
                     else
                        dcN(j,i) = dc(j,i)
                     end if
                  end if
                  c(j,i) = cN(j,i) 
                  if (arret2.eq.1 .and. dcN(j,i).gt.ndcmin) arret2=0 
               end do
            end do

c           CHECK OF THE SIGN OF THE DERIVATIVES OF Z AND DELTA 
c           AND MODIFICATION OF STEP.
c           - - - - - - - - - - - - - - - - - - - - - - - - - - 
            do j=2,m
               do i=1,2
                  dz(i,j) = dzN(i,j)
                  if (xizA(i,j)*xiz(i,j) .lt. 0.) then
                     dzN(i,j) = dz(i,j)/2.
                  else 
                    if (dz(i,j)*1.1 .le. ndz(i)) then
                       dzN(i,j) = dz(i,j)*1.1
                    else
                       dzN(i,j) = dz(i,j)
                    end if
                  end if
                  z(i,j) = zN(i,j)
                  if (arret2.eq.1 .and. dzN(i,j).gt.ndzmin(i)) arret2=0 

                  dd(i,j) = ddN(i,j)
                  if (xidA(i,j)*xid(i,j) .lt. 0.) then
                     ddN(i,j) = dd(i,j)/2.
                  else
                    if (dd(i,j)*1.4 .le. ndd) then
                       ddN(i,j) = dd(i,j)*1.4
                    else
                       ddN(i,j) = dd(i,j)
                    end if
                  end if
                  delta(i,j) = deltaN(i,j)
                  if (arret2.eq.1 .and. ddN(i,j).gt.nddmin) arret2=0 
               end do
            end do

c           CHECK OF THE SIGN OF THE DERIVATIVES OF Io A B C Cx Cy 
c           AND MODIFICATION OF STEP.
c           - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            do j=1,6
               dmanaly(j) = dmanalyN(j)
               if (ximaA(j)*xima(j) .lt. 0.) then
                  dmanalyN(j) = dmanaly(j)/2.
               else 
                 if (dmanaly(j)*1.1 .le. ndmanaly(j)) then
                    dmanalyN(j) = dmanaly(j)*1.1
                 else
                    dmanalyN(j) = dmanaly(j)
                 end if
               end if
               manaly(j) = manalyN(j)
               if (arret2.eq.1 .and. dmanalyN(j).gt.ndmamin(j)) arret2=0
            end do

            if (arret2 .eq. 1) then
                write(*,*)
                write(*,*) '================================='
                write(*,*) '  TOUS LES PAS SONT TROP PETITS'
                write(*,*) '================================='
                return
            end if
            arret2 = 1

         else

            aug = 1
            arret = arret + 1
            write(*,*) 'Iteration ', its+1,', min qi : ',fp,qi

c            write(*,*)
c            write(*,*) ' ON DEPASSE LE MIN. (dépassement n° ',arret,' )'
c            write(*,*) '==============================================='
c            write(*,*) '****** ON REPART DES VALEURS SUIVANTES : ******'

            do i=1,np
c               write(*,'(''   a...a c1 c2   : '',$)')
               do j=1,m2
c                  write(*,'(E12.6,A1,$)') a(i,j),' '
               end do
c               write(*,'(2(E12.6,A1))') c(1,i),' ',c(2,i),' '
            end do

            do i=1,m
c               write(*,*) '  z1  z2        : ',z(1,i),z(2,i)
c               write(*,*) '  delta1 delta2 : ',delta(1,i),delta(2,i)
            end do

c            write(*,*) '  Modèle analytique: '
c            write(*,'(A13,E12.6)')'     Io    : ',manaly(6)
c            write(*,'(A13,3(E12.6,A1))')'     A B C : ',manaly(1),' ',
c     &                                  manaly(2),' ',manaly(3),' '
c            write(*,'(A13,2(E12.6,A1))')'     Cx Cy : ',manaly(4),' ',
c     &                                      manaly(5),' '
c            write(*,*) '  f : ',p(1),p(512),p(1024)

            if (arret .eq. 10) then
               write(*,*)
               write(*,*) '=================================='
               write(*,*) '  LE MINIMUM A ETE DEPASSE 10 fois'
               write(*,*) '=================================='
               return
            end if
   
c           FOND
c           - - -   
            do i=1,n2
               if (xifA(i)*xif(i) .lt. 0.)  then
                  df(i) = df(i)/2.
               end if
               dfN(i) = df(i)
               xif(i) = xifA(i)
            end do

c           SOURCES PONCTUELLES
c           - - - - - - - - - - 
            do i=1,np
               do j=1,m2
                  if (xiaA(i,j)*xia(i,j) .lt. 0.) then
                     da(i,j) = da(i,j)/2.
                  end if
                  daN(i,j) = da(i,j)
                  xia(i,j) = xiaA(i,j)
               end do
               do j=1,2
                  if (xicA(j,i)*xic(j,i) .lt. 0.) then
                     dc(j,i) = dc(j,i)/2.
                  end if
                  dcN(j,i) = dc(j,i)
                  xic(j,i) = xicA(j,i)
               end do
            end do

c           Z ET DECALAGES.
c           - - - - - - - - 
            do j=2,m
               do i=1,2
                  if (xizA(i,j)*xiz(i,j) .lt. 0.) then
                     dz(i,j) = dz(i,j)/2.
                  end if
                  dzN(i,j) = dz(i,j)
                  xiz(i,j) = xizA(i,j)

                  if (xidA(i,j)*xid(i,j) .lt. 0.) then
                     dd(i,j) = dd(i,j)/2.
                  end if
                  ddN(i,j) = dd(i,j)
                  xid(i,j) = xidA(i,j)
               end do
            end do

c           MODELE ANALYTIQUE.
c           - - - - - - - - - -
            do j=1,6
               if (ximaA(j)*xima(j) .lt. 0.) then
                  dmanaly(j) = dmanaly(j)/2.
               end if
               dmanalyN(j) = dmanaly(j)
               xima(j) = ximaA(j)
            end do

            fp = fpA
            qi = qiA
         end if
      end do

      write(*,*)
      write(*,*) '========================================='
      write(*,*) ' NOMBRE D''ITERATIONS EXCEDE DANS MINIMI'
      write(*,*) '========================================='

      return
      end

c     -------------------------------
c     SUBROUTINE: inifunc_dfunc_model
c     -------------------------------

      subroutine inifunc_dfunc_model(p,z,a,c,delta,manaly)

      implicit none

      include 'param_dec.f'

      integer nb4
      parameter(nb4=nbr2+4*(xy2+1))

      real*4 a(npic,nbg),c(2,npic),b,p(nbr2),z(2,nbg),delta(2,nbg)
      real*4 manaly(6)
      real*4 g(nbr1,nbg),sig2(nbr1,nbg),sig3(nbr1,nbg),s(nbr2,nbg)
      real*4 ss(2*xy2,nbg),trs(nbr2,nbg),strs(2*xy2,nbg)
      real*4 far(nbr2,nbg),far2(nbr2,nbg)
      real*4 sf(nbr2),ssf(2*xy2),sfbis(nbr1,nbg),sf2(nbr2),ssf2(2*xy2)
      real*4 sfbis2(nbr1),sfbis3,t(nbr2,nbg),st(2*xy2,nbg),tmpt(nbr2)
      real*4 far3(nbr2,nbg),sf3(nbr2),ssf3(2*xy2),stmpt(2*xy2)
      real*4 rc(nbr2,6),srcbis,src2bis,src3bis,src4bis,src5bis,src6bis
      real*4 delx,dely,w(9),shfz(nb4,nbg),inter(nb4) 
      real*4 tmp9(nbr2),stmp9(2*xy2),src7bis(nbr1),model(nbr2)
      real*4 tm,tm2,tm3,tamp,tamp1,tamp2,tamp3,t1,t2,t3,t4,t5,som1,som2
      real*4 tmp(nbr2),stmp(2*xy2),tmp2(nbr2),stmp2(2*xy2),tmp3(nbr2)
      real*4 stmp3(2*xy2),tmp4(nbr2),stmp4(2*xy2),tmp5(nbr2)
      real*4 stmp5(2*xy2),tmp6(nbr2),stmp6(2*xy2),tabl(nbr2,6)
      real*4 tmp7(nbr2),tmp8(nbr2),stmp7(2*xy2),stmp8(2*xy2)
      real*4 rr(nbr2),frf(nbr2),srr(2*xy2)
      real*4 xif(nbr2),xia(npic,nbg),xic(2,npic),xiz(2,nbg)
      real*4 xid(2,nbg),xima(6),ttt(nbr1),mask(nbr2)
      real*4 ebc,alpha,fp,qi,fwhm(nbg),bg(nbg),cx,cy
      integer n1,n2,np,m,indice,indice2,ind,ind1,ind2,ind3,ind4,indi
      integer i,ii,iii,j,jj,j2,k,k2,l,pas,deb,nxy1,nxy2,m2,ii2
      integer debutx,debuty,finx,finy,dif,vari_int
      character*20 resultat

      common /gr1/ g,s,sig2,ss
      common /param/ nxy1,nxy2,pas
      common /parametre_alpha/ b,alpha
      common /gr5/ sfbis
      common /entropie/ rr,frf,srr
      common /sig/ sig3
      common /tailles/ n1,n2,np,m,m2
      common /minimum/ fp,qi
      common /trans/ trs,strs
      common /derivees/ xif,xia,xic,xiz,xid
      common /model2/ xima
      common /gaussienne/ fwhm,bg
      common /psft/ t,st
      common /variation_intensite/ vari_int
      common /masque2/ mask
      common /modelpourminimi/ model

c     CALCULATION OF : FAR(j,i) = z(1,i)*F(j) + z(2,i)
c                      FAR2(j,i) = SOMMEsurK (A(k,i)*R(C(k)-delta(i)))
c                                + Io*z(1,i)*r(A,B,C,Cx,Cy)
c                      WHERE i = IMAGE NUMBER
c                            j = INDEX OF THE COMPUTED PARAMETER
c                            k = NUMBER OF POINT SOURCES
c     - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


      do i=1,n2
         tmp2(i) = p(i)
         xif(i) = 0.
      end do
      do ii=1,m
         t1 = z(1,ii)
         t2 = z(2,ii)
         do i=1,n2
            far(i,ii) = t1*p(i)+t2
            far2(i,ii) = 0.
         end do
      end do

c     CALCULATION OF R CONVOLVED WITH F, USED IN THE SMOOTHING TERM
c     AND CALCULATION OF THIS TERM:
c     - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
      call rlft2(tmp2,stmp2,nxy2,1)
      call produit(tmp2,rr,stmp2,srr,xy2)
      call rlft2(tmp2,stmp2,nxy2,-1)

      fp = 0.
      do i=1,n2
         frf(i) = p(i)-tmp2(i)
         fp = fp + frf(i)**2
      end do

      do k=1,np
         xic(1,k) = 0.
         xic(2,k) = 0.
         do ii=1,m
            if (vari_int .eq. 1) then
               t2 = a(k,ii)
            else
               t2 = a(k,1)*z(1,ii)
            end if
            t3 = c(1,k)-delta(1,ii)
            t4 = c(2,k)-delta(2,ii)
            xia(k,ii) = 0.
            do j=1,nxy2
               tamp2 = j-t4
               ind2 = (j-1)*nxy2
               do i=1,nxy2
                  ind = i+ind2
                  tamp1 = i-t3
                  tm = exp(-b*(tamp1*tamp1+tamp2*tamp2))
                  far2(ind,ii) = far2(ind,ii) + t2*tm
               end do
            end do
         end do
      end do

      do ii=1,m
         xiz(1,ii) = 0.
         xiz(2,ii) = 0.
         xid(1,ii) = 0.
         xid(2,ii) = 0.
         t1 = manaly(4)-delta(1,ii)
         t2 = manaly(5)-delta(2,ii)
         do j=1,nxy2
            tamp2 = j-t2
            ind2 = (j-1)*nxy2
            do i=1,nxy2
               ind = i+ind2
               tamp1 = i-t1
               tm = exp(-((manaly(1)*tamp1*tamp1+manaly(2)*tamp2*tamp2+
     &                     manaly(3)*tamp1*tamp2)**alpha))
               far3(ind,ii) = manaly(6)*z(1,ii)*tm
            end do
         end do
      end do
      do i=1,n2
         model(i) = far3(i,1)
      end do

      do i=1,6
         xima(i) = 0.
      end do

c     CALCULATION OF W (WEIGHT OF PIXELS) FOR THE SHIFT BETWEEN IMAGES
c     - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
      qi = 0.
      do ii=1,m
         if (delta(1,ii) .lt. 0.) then
            delx = 1+delta(1,ii)
         else
            delx = delta(1,ii)
         end if
         if (delta(2,ii) .lt. 0.) then
            dely = 1+delta(2,ii)
         else
            dely = delta(2,ii)
         end if
         if (pas .eq. 1) then
c           WHEN ONE STAYS IN BIG PIXELS
c           - - - - - - - - - - - - - - 
            w(1) = (1-delx)*(1-dely)
            w(2) = delx*(1-dely)
            w(3) = dely*(1-delx)
            w(4) = delx*dely
         else
c           WHEN ONE CHANGES TO SMALL PIXELS
c           - - - - - - - - - - - - - - -
            w(1) = (1-delx)*(1-dely)/4
            w(2) = (1-dely)/4
            w(3) = delx*(1-dely)/4
            w(4) = (1-delx)/4
            w(5) = 0.25
            w(6) = delx/4
            w(7) = dely*(1-delx)/4
            w(8) = dely/4
            w(9) = delx*dely/4
         end if

         if (delta(1,ii) .ge. 0. .and. delta(2,ii) .ge. 0.) then
            deb = nxy2+3
         else if (delta(1,ii) .ge. 0. .and. delta(2,ii) .lt. 0.) then
            deb = 1
         else if (delta(1,ii) .lt. 0. .and. delta(2,ii) .ge. 0.) then
            deb = nxy2+2
         else
            deb = 0
         end if 

c        CALCULATION OF S CONVOLVED WITH FAR AND S CONVOLVED WITH FAR2,
c        AND CALCULATION OF THE MINIMUM
c        - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

         do i=1,n2
            sf(i) = far(i,ii)
            sf2(i) = far2(i,ii)
            sf3(i) = far3(i,ii)
            tmp(i) = s(i,ii)
            tmpt(i) = t(i,ii)
            tmp2(i) = 0.
            tmp3(i) = 0.
            tmp9(i) = 0.
         end do   
         do i=1,xy2*2
            stmp(i) = ss(i,ii)
            stmpt(i) = st(i,ii)
         end do

         call rlft2(sf,ssf,nxy2,1)
         call rlft2(sf2,ssf2,nxy2,1)
         call rlft2(sf3,ssf3,nxy2,1)
         call produit(sf,tmp,ssf,stmp,nxy2)
         call produit(sf2,tmp,ssf2,stmp,nxy2)
         call produit(sf3,tmpt,ssf3,stmpt,nxy2)
         call rlft2(sf,ssf,nxy2,-1)
         call rlft2(sf2,ssf2,nxy2,-1)
         call rlft2(sf3,ssf3,nxy2,-1)

c        SF = (S)*(Z1*F+Z2) AND 
c        SF2 = (S)*[SOMME(A*R(C-DELTE))]
c        SF3 = (T)*[(I0*Z1*R(A,B,C,Cx,Cy)]

c        SF MUST BE SHIFTED
c        THE TABLE IS MODIFIED AND THE STARTING POINT IS COMPUTED
c        YOU CHANGE FROM BIG PIXELS TO SMALL PIXELS TO TAKE INTO
c        ACCOUNT THE WEIGHTS OF PIXELS.
c        - - - - - - - - - - - - - - - - - - - - - - - - - - -

         do j=1,nxy2
            inter(j*(nxy2+2)+1) = sf(j*nxy2)
            do i=1,nxy2
               indice = (j-1)*nxy2+i
               indice2 = j*(nxy2+2)+1+i
               inter(indice2) = sf(indice)
            end do
            inter((j+1)*(nxy2+2)) = sf((j-1)*nxy2+1)
         end do
         do i=1,nxy2+2
            inter(i) = inter((nxy2+2)*nxy2+i)
            inter((nxy2+2)*(nxy2+1)+i) = inter(nxy2+2+i)
         end do

         do i=1,n2+4*(nxy2+1)
            shfz(i,ii) = inter(i)
         end do

         do j=1,nxy1
            do i=1,nxy1
               ind1 = deb+(nxy2+2)*pas*(j-1)+pas*(i-1)
               indice = (j-1)*nxy1+i
               sfbis2(indice) = 0.
               do l=1,pas+1
                  ind2 = (l-1)*(nxy2+2)
                  ind3 = (pas+1)*(l-1)
                  do k=1,pas+1
                    sfbis2(indice) = sfbis2(indice) + 
     &                              w(ind3+k)*inter(ind1+k+ind2) 
                 end do
               end do
            end do
         end do

c        SFBIS2 = SF SHIFTED AND PUT IN BIG PIXELS.


c        SF2 IS ALREADY SHIFTED, ON ONLY CHANGE FROM SMALL TO BIG PIXELS
c        - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
         do j=1,nxy1
            do i=1,nxy1
               ind1 = nxy2*pas*(j-1)+pas*(i-1)
               indice = (j-1)*nxy1+i
               sfbis(indice,ii) = 0.
               sfbis3 = 0.
               do l=1,pas
                  ind2 = (l-1)*nxy2
                  do k=1,pas
                    sfbis(indice,ii) = sfbis(indice,ii) + 
     &                              sf2(ind1+k+ind2) 
                    sfbis3 = sfbis3 + sf3(ind1+k+ind2)
                  end do
               end do
               sfbis3 = sfbis3/real(pas**2)
               sfbis(indice,ii) = sfbis(indice,ii)/real(pas**2) +
     &                            sfbis2(indice) + sfbis3
               tamp = (sfbis(indice,ii)-g(indice,ii))**2 
               qi = qi + tamp*sig3(indice,ii)
               fp = fp + tamp*sig2(indice,ii)
            end do
         end do
 
c        SFBIS = SFBIS2 + SF2 PUT IN BIG PIXELS
c        - - - - - - - - - - - - - - - - - - - 

c        CALCULATION OF DERIVATIVES OF A, C1 ET C2
c        - - - - - - - - - - - - - - - - - - - - - 

         do k=1,np
            cx = c(1,k)-delta(1,ii)
            cy = c(2,k)-delta(2,ii)

            if (vari_int .eq. 1) then
               t3 = a(k,ii)
               ii2 = ii
               t4 = 1.
               do j=1,nxy2
                  tamp2 = j-cy
                  ind2 = (j-1)*nxy2
                  do i=1,nxy2
                     ind = i+ind2
                     tamp1 = i-cx
                     ebc= exp(-b*((tamp1*tamp1)+(tamp2*tamp2)))
                     tmp2(ind) = tmp2(ind) + ebc*tamp1*t3
                     tmp3(ind) = tmp3(ind) + ebc*tamp2*t3
                  end do
               end do
            else
               t3 = a(k,1)*z(1,ii)
               ii2 = 1
               t4 = z(1,ii)
               do j=1,nxy2
                  tamp2 = j-cy
                  ind2 = (j-1)*nxy2
                  do i=1,nxy2
                     ind = i+ind2
                     tamp1 = i-cx
                     ebc= exp(-b*((tamp1*tamp1)+(tamp2*tamp2)))
                     tmp2(ind) = tmp2(ind) + ebc*tamp1*t3
                     tmp3(ind) = tmp3(ind) + ebc*tamp2*t3
                     tmp9(ind) = tmp9(ind) + ebc*a(k,1)
                  end do
               end do
            end if

            cx = cx/2.
            cy = cy/2.
            debutx = anint(cx)-fwhm(ii)
            debuty = anint(cy)-fwhm(ii)
            finx = anint(cx)+fwhm(ii)
            finy = anint(cy)+fwhm(ii)
            if (debutx .le. 0) then
               dif = 1-debutx
               debutx = 1
               finx = finx-dif
            end if
            if (debuty .le. 0) then
               dif = 1-debuty
               debuty=1
               finy = finy-dif
            end if
            if (finx .gt. nxy1) then
               dif = finx-nxy1
               debutx = debutx+dif
               finx=nxy1
            end if
            if (finy .gt. nxy1) then
               dif = finy-nxy1
               debuty = debuty+dif
               finy = nxy1
            end if
            do j=debuty,finy
               tamp2 = j-cy
               do i=debutx,finx
                  tamp1 = i-cx
                  indice = (j-1)*nxy1+i
                  ebc = exp(-bg(ii)*((tamp1*tamp1)+(tamp2*tamp2)))
                  tamp3 = (sfbis(indice,ii)-g(indice,ii))
     &                     *sig2(indice,ii)
                  xia(k,ii2) = xia(k,ii2) + ebc*tamp3*t4
                  xic(1,k) = xic(1,k) + t3*ebc*tamp3*tamp1
                  xic(2,k) = xic(2,k) + t3*ebc*tamp3*tamp2
               end do
            end do
         end do
c        ---------------------------------------------
c        FIN DE LA BOUCLE SUR LE NOMBRE DE SOURCES (K)
c        ---------------------------------------------

c        CALCULATION OF DERIVATIVES OF Io A B C Cx Cy
c        - - - - - - - - - - - - - - - - - - - - - - -

         t1 = manaly(4)-delta(1,ii)
         t2 = manaly(5)-delta(2,ii)
         t3 = manaly(6)*z(1,ii)
         do j=1,nxy2
            tamp2 = j-t2
            ind2 = (j-1)*nxy2
            do i=1,nxy2
               ind = i+ind2
               tamp1 = i-t1
               tm = manaly(1)*tamp1*tamp1+manaly(2)*tamp2*tamp2+
     &                      manaly(3)*tamp1*tamp2
               tm2 = exp(-((tm)**alpha))
               if ((tamp1.eq.0.).and.(tamp2.eq.0.)) then
                  tm3 = 0.
               else
                  tm3 = tm**(alpha-1)
               end if
               tmp7(ind) = t3*tm2*(-alpha)*tm3*
     &                     ((2*manaly(1)*tamp1)+(manaly(3)*tamp2))
               tmp8(ind) = t3*tm2*(-alpha)*tm3*
     &                     ((2*manaly(2)*tamp2)+(manaly(3)*tamp1))
               tmp6(ind) = tm2*manaly(6)
               rc(ind,1) = tm2*z(1,ii)
               rc(ind,2) = t3*tm2*(-alpha)*tm3*tamp1*tamp1
               rc(ind,3) = t3*tm2*(-alpha)*tm3*tamp2*tamp2
               rc(ind,4) = t3*tm2*(-alpha)*tm3*tamp1*tamp2
               rc(ind,5) = t3*tm2*(alpha)*tm3*
     &                       ((2*manaly(1)*tamp1)+(manaly(3)*tamp2))
               rc(ind,6) = t3*tm2*(alpha)*tm3*
     &                       ((2*manaly(2)*tamp2)+(manaly(3)*tamp1))
            end do
         end do

         call rlft2(tmp7,stmp7,nxy2,1)
         call rlft2(tmp8,stmp8,nxy2,1)
         call produit(tmp7,rr,stmp7,srr,nxy2)
         call produit(tmp8,rr,stmp8,srr,nxy2)
         call rlft2(tmp7,stmp7,nxy2,-1)
         call rlft2(tmp8,stmp8,nxy2,-1)

         do i=1,n2
            tmp2(i) = tmp2(i) + tmp7(i)
            tmp3(i) = tmp3(i) + tmp8(i)
         end do

         do j2=1,6
            do i=1,n2
               tmp4(i) = rc(i,j2)
            end do
            call rlft2(tmp4,stmp4,nxy2,1)
            call produit(tmp4,tmpt,stmp4,stmpt,nxy2)
            call rlft2(tmp4,stmp4,nxy2,-1)
            do i=1,n2
               tabl(i,j2) = tmp4(i)
            end do
         end do

         do j=1,nxy1
            do i=1,nxy1
               ind1 = nxy2*pas*(j-1)+pas*(i-1)
               indice = (j-1)*nxy1+i
               srcbis = 0.
               src2bis = 0.
               src3bis = 0.
               src4bis = 0.
               src5bis = 0.
               src6bis = 0.
               do l=1,pas
                  ind2 = (l-1)*nxy2
                  do k2=1,pas
                     srcbis  = srcbis  + tabl((ind1+k2+ind2),1)
     &                          * mask(ind1+k2+ind2)
                     src2bis = src2bis + tabl((ind1+k2+ind2),2)  
     &                          * mask(ind1+k2+ind2)
                     src3bis = src3bis + tabl((ind1+k2+ind2),3)  
     &                          * mask(ind1+k2+ind2)
                     src4bis = src4bis + tabl((ind1+k2+ind2),4)  
     &                          * mask(ind1+k2+ind2)
                     src5bis = src5bis + tabl((ind1+k2+ind2),5)  
     &                          * mask(ind1+k2+ind2)
                     src6bis = src6bis + tabl((ind1+k2+ind2),6)  
     &                          * mask(ind1+k2+ind2)
                  end do
               end do
               srcbis  = srcbis/real(pas**2)
               src2bis = src2bis/real(pas**2)
               src3bis = src3bis/real(pas**2)
               src4bis = src4bis/real(pas**2)
               src5bis = src5bis/real(pas**2)
               src6bis = src6bis/real(pas**2)
               tamp2 = (sfbis(indice,ii)-g(indice,ii))
     &                  *sig2(indice,ii)
               xima(6) = xima(6) + 2*tamp2*srcbis
               xima(1) = xima(1) + 2*tamp2*src2bis
               xima(2) = xima(2) + 2*tamp2*src3bis
               xima(3) = xima(3) + 2*tamp2*src4bis
               xima(4) = xima(4) + 2*tamp2*src5bis
               xima(5) = xima(5) + 2*tamp2*src6bis
            end do
         end do

c        CALCULATION OF DERIVATIVES OF Z AND DELTA
c        - - - - - - - - - - - - - - - - - - - - - 
         if (ii .ne. 1) then

            if (vari_int .eq. 0) then
               call rlft2(tmp9,stmp9,nxy2,1)
               call produit(tmp9,tmp,stmp9,stmp,nxy2)
               call rlft2(tmp9,stmp9,nxy2,-1)

               do j=1,nxy1
                  do i=1,nxy1
                     ind1 = deb+(nxy2+2)*pas*(j-1)+pas*(i-1)
                     ind4 = nxy2*pas*(j-1)+pas*(i-1)
                     indice = (j-1)*nxy1+i
                     src7bis(indice) = 0.
                     do l=1,pas
                        ind2 = (l-1)*nxy2
                        do k2=1,pas
                           src7bis(indice) = src7bis(indice) + 
     &                                       tmp9(ind4+k2+ind2)  
                        end do
                     end do
                     src7bis(indice) = src7bis(indice)/real(pas**2)
                  end do
               end do
            else 
               do i=1,n1
                  src7bis(i) = 0.
               end do  
            end if

            do i=1,n2
               tmp4(i) = p(i)
            end do
            call rlft2(tmp4,stmp4,nxy2,1)
            call rlft2(tmp6,stmp6,nxy2,1)
            call rlft2(tmp2,stmp2,nxy2,1)
            call rlft2(tmp3,stmp3,nxy2,1)
            call produit(tmp4,tmp,stmp4,stmp,nxy2)
            call produit(tmp6,tmpt,stmp6,stmpt,nxy2)
            call produit(tmp2,tmp,stmp2,stmp,nxy2)
            call produit(tmp3,tmp,stmp3,stmp,nxy2)
            call rlft2(tmp4,stmp4,nxy2,-1)
            call rlft2(tmp6,stmp6,nxy2,-1)
            call rlft2(tmp2,stmp2,nxy2,-1)
            call rlft2(tmp3,stmp3,nxy2,-1)

            do j=1,nxy2
               inter(j*(nxy2+2)+1) = tmp4(j*nxy2)
               do i=1,nxy2
                  indice = (j-1)*nxy2+i
                  indice2 = j*(nxy2+2)+1+i
                  inter(indice2) = tmp4(indice)
               end do
               inter((j+1)*(nxy2+2)) = tmp4((j-1)*nxy2+1)
            end do
            do i=1,nxy2+2
               inter(i) = inter((nxy2+2)*nxy2+i)
               inter((nxy2+2)*(nxy2+1)+i) = inter(nxy2+2+i)
            end do

            do j=1,nxy1
               do i=1,nxy1
                  ind1 = deb+(nxy2+2)*pas*(j-1)+pas*(i-1)
                  ind4 = nxy2*pas*(j-1)+pas*(i-1)
                  indice = (j-1)*nxy1+i
                  srcbis = 0.
                  src2bis = 0.
                  src3bis = 0.
                  src4bis = 0.
                  tamp2 = (sfbis(indice,ii)-g(indice,ii))
     &                    *sig2(indice,ii)
                  do l=1,pas+1
                     ind2 = (l-1)*(nxy2+2)
                     ind3 = (pas+1)*(l-1)
                     do k2=1,pas+1
                        srcbis = srcbis + 
     &                           w(ind3+k2)*inter(ind1+k2+ind2)  
                     end do
                  end do
                  do l=1,pas
                     ind2 = (l-1)*nxy2
                     do k2=1,pas
                        src2bis = src2bis + tmp2(ind4+k2+ind2)  
                        src3bis = src3bis + tmp3(ind4+k2+ind2)  
                        src4bis = src4bis + tmp6(ind4+k2+ind2)
                        tmp5(ind4+k2+ind2) = tamp2
                     end do
                  end do
                  src2bis = src2bis/real(pas**2)
                  src3bis = src3bis/real(pas**2)
                  src4bis = src4bis/real(pas**2)
                  if (pas .eq. 1) then
                     som1 = shfz(ind1+1,ii)*(dely-1) +
     &                      shfz(ind1+2,ii)*(1-dely) -
     &                      shfz(ind1+(nxy2+2)+1,ii)*dely +
     &                      shfz(ind1+(nxy2+2)+2,ii)*dely
                     som2 = shfz(ind1+1,ii)*(delx-1) -
     &                      shfz(ind1+2,ii)*delx +
     &                      shfz(ind1+(nxy2+2)+1,ii)*(1-delx) +
     &                      shfz(ind1+(nxy2+2)+2,ii)*delx
                  else
                    som1 = (shfz(ind1+1,ii)*(dely-1) +
     &                     shfz(ind1+3,ii)*(1-dely) -     
     &                     shfz(ind1+(nxy2+2)+1,ii) +
     &                     shfz(ind1+(nxy2+2)+3,ii) -
     &                     shfz(ind1+2*(nxy2+2)+1,ii)*dely +
     &                     shfz(ind1+2*(nxy2+2)+3,ii)*dely)*0.25 
                    som2 = (shfz(ind1+1,ii)*(delx-1) -
     &                     shfz(ind1+2,ii) -
     &                     shfz(ind1+3,ii)*delx +
     &                     shfz(ind1+2*(nxy2+2)+1,ii)*(1-delx)+
     &                     shfz(ind1+2*(nxy2+2)+2,ii) +
     &                     shfz(ind1+2*(nxy2+2)+3,ii)*delx)*0.25
                  end if
                  xiz(1,ii) = xiz(1,ii) + 
     &                        2*tamp2*(srcbis+src4bis+src7bis(indice))
                  xiz(2,ii) = xiz(2,ii) + 2.*tamp2
                  xid(1,ii) = xid(1,ii)-4.*b*tamp2*src2bis 
     &                       + 2.*som1*tamp2
                  xid(2,ii) = xid(2,ii)-4.*b*tamp2*src3bis 
     &                       + 2.*som2*tamp2
               end do
            end do
         else 
            do j=1,nxy1
               do i=1,nxy1
                  ind1 = nxy2*pas*(j-1)+pas*(i-1)
                  indice = (j-1)*nxy1+i
                  tamp2 = (sfbis(indice,ii)-g(indice,ii))*
     &                    sig2(indice,ii)
                  do l=1,pas
                     ind2 = (l-1)*nxy2
                     do k=1,pas
                        tmp5(ind1+k+ind2) = tamp2
                     end do
                  end do
               end do
            end do
         end if  

c        CALCULTATION OF DERIVATIVES OF F
c        - - - - - - - - - - - - - - - - -

         call rlft2(tmp5,stmp5,nxy2,1)
        
         do i=1,n2
            tmp3(i) = trs(i,ii)
         end do
         do i=1,2*nxy2
            stmp3(i) = strs(i,ii)
         end do
 
         call produit(tmp3,tmp5,stmp3,stmp5,nxy2)
         call rlft2(tmp3,stmp3,nxy2,-1)
 
         t1 = z(1,ii)*2.
         do i=1,n2
            xif(i) =  xif(i) + t1*tmp3(i) 
         end do
      end do
c     ---------------------------------------------
c     FIN DE LA BOUCLE SUR LE NOMBRE D'IMAGE (II)
c     ---------------------------------------------

c     CALCULTATION OF THE SMOOTHING TERM FOR THE DERIVATIVES OF F
c     - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

      do i=1,n2
         tmp2(i) = frf(i)
      end do

      call rlft2(tmp2,stmp2,nxy2,1)
      call produit(tmp2,rr,stmp2,srr,nxy2)
      call rlft2(tmp2,stmp2,nxy2,-1)

      do i=1,n2
         xif(i) = xif(i) + 2.*(frf(i)-tmp2(i))
      end do

      return
      end

c     --------------------------
c     SUBROUTINE: decompos_model
c     --------------------------
c     THIS ROUTINE IS USED FOR THE OUTPUT OF THE RESULTS.
c     ----------------------

      subroutine decompos_model(residu_fin)

      implicit none

      include 'param_dec.f'

      integer nb
      parameter(nb=nbr2+4*(xy2+1))

      real*4 p(nbr2),a(npic,nbg),c(2,npic),manaly(6)
      real*4 z(2,nbg),delta(2,nbg)
      real*4 g(nbr1,nbg),sig2(nbr1,nbg),sig3(nbr1,nbg)
      real*4 s(nbr2,nbg),ss(2*xy2,nbg),ssourdel(2*xy2)
      real*4 source(nbr2),fond(nbr2),model(nbr2),fondmodel(nbr2)
      real*4 sfondmodel(2*xy2),fg(nbr1),sourdel(nbr2),sg(nbr1)
      real*4 tmp(nbr2),tmp2(nbr2),tmp3(nbr2),stmp3(2*xy2),stmp2(2*xy2)
      real*4 w(4),w2(4),fp,qi,b,gsm(nbr1)
      real*4 inter(nb),inter2(nb),inter3(nb)
      real*4 resim(nbr2),resismm(nbr2),sfbis(nbr1,nbg),resireduit(nbr2)
      real*4 alpha,delx,dely,delx2,dely2,t1,t2,t3,t4,t5,t6,t7,t8
      integer n1,n2,np,m,nxy1,nxy2,pas,deb,deb2
      integer i,i2,ii,j,k,l,indice,indice2,ind1,ind2,ind3,ii2
      integer residu_fin,vari_int,m2,nbch,i3
      integer dels(npic),ndels
      character*20 results
      character*1 lettre1,lettre3,lettre2,lettre4,question
      character*9 fin


      common /param/ nxy1,nxy2,pas
      common /parametre_alpha/ b,alpha
      common /gr1/ g,s,sig2,ss
      common/sig/ sig3
      common /variables/ p,z,a,c,delta
      common /tailles/ n1,n2,np,m,m2
      common /minimum/ fp,qi
      common /model/ manaly
      common /gr5/ sfbis
      common /variation_intensite/ vari_int
      common /source_delete/ dels,ndels
      common /digit/ nbch

      if (residu_fin .eq. 1) then
         do i=1,n2
            resim(i) = 0.
            resismm(i) = 0.
            resireduit(i) = 0.
         end do

c        demande de mise à zero des valeurs négatives
c        - - - - - - - - - - - - - - - - - - - - - - -
         question = 'n'
c         do while (question.ne.'y' .and. question .ne.'n')
c            write(*,'('' Mettre à 0 les valeurs négatives'',$)')
c            write(*,'('' du fond dans les images lissées (y/n) : '',$)')
c            read(5,*) question
c         end do
      end if

c     inter 3 = image de f avec un bord de 1 pixel supplémentaire
c     - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
      do j=1,nxy2
         inter3(j*(nxy2+2)+1) = p(j*nxy2)
         do i=1,nxy2
            indice = (j-1)*nxy2+i
            indice2 = j*(nxy2+2)+1+i
            inter3(indice2) = p(indice)
         end do
         inter3((j+1)*(nxy2+2)) = p((j-1)*nxy2+1)
      end do
      do i=1,nxy2+2
         inter3(i) = inter3((nxy2+2)*nxy2+i)
         inter3((nxy2+2)*(nxy2+1)+i) = inter3(nxy2+2+i)
      end do

c     Boucle sur le nombre d'images
c     - - - - - - - - - - - - - - - 
      do ii=1,m
         if (nbch .eq. 1 .and. m .lt. 10) then
            do i=1,m
               lettre1 = char(48+ii)
               fin = lettre1 // '.fits'
            end do
         else if (nbch .eq. 2 .and. m .lt. 100) then
            do i=1,m
               i2 = int(ii/10)
               lettre1 = char(48+i2)
               i2 = ii - i2*10
               lettre2 = char(48+i2)
               fin = lettre1 // lettre2 // '.fits'
            end do
         else if (nbch .eq. 3 .and. m .lt. 1000) then
            do i=1,m
               i2 = int(ii/100)
               lettre1 = char(48+i2)
               i2 = ii-i2*100
               i3 = int(i2/10)
               lettre2 = char(48+i3)
               i2 = i2-i3*10
               lettre3 = char(48+i2)
               fin = lettre1 // lettre2 // lettre3 // '.fits'
            end do
         else if (nbch .eq. 4 .and. m .lt. 10000) then
            do i=1,m
               i2 = int(ii/1000)
               lettre1 = char(48+i2)
               i2 = ii-i2*1000
               i3 = int(i2/100)
               lettre2 = char(48+i3)
               i2 = i2-i3*100
               i3 = int(i2/10)
               lettre3 = char(48+i3)
               i2 = i2-i3*10
               lettre4 = char(48+i2)
               fin = lettre1 // lettre2 // lettre3 // lettre4 // '.fits'
            end do
         end if

c        Calcul des variables delx dely deb (delx2 dely2 deb2 si residu_fin = 1)
c        - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
         if (delta(1,ii) .lt. 0.) then
            delx = 1+delta(1,ii)
            delx2 = -delta(1,ii)
         else
            delx = delta(1,ii)
            delx2 = 1-delta(1,ii)
         end if
         if (delta(2,ii) .lt. 0.) then
            dely = 1+delta(2,ii)
            dely2 = -delta(2,ii)
         else
            dely = delta(2,ii)
            dely2 = 1-delta(2,ii)
         end if

         if (delta(1,ii) .ge. 0. .and. delta(2,ii) .ge. 0.) then
            deb = nxy2+3
            deb2 = 0
         else if (delta(1,ii) .ge. 0. .and. delta(2,ii) .lt. 0.) then
            deb = 1
            deb2 = nxy2+2
         else if (delta(1,ii) .lt. 0. .and. delta(2,ii) .ge. 0.) then
            deb = nxy2+2
            deb2 = 1
         else
            deb = 0
            deb2 = nxy2+3
         end if 

         w(1) = (1-delx)*(1-dely)
         w(2) = delx*(1-dely)
         w(3) = dely*(1-delx)
         w(4) = delx*dely
         w2(1) = (1-delx2)*(1-dely2)
         w2(2) = delx2*(1-dely2)
         w2(3) = dely2*(1-delx2)
         w2(4) = delx2*dely2

         t5 = manaly(4)-delta(1,ii)
         t6 = manaly(5)-delta(2,ii)
         do j=1,nxy2
            t4 = j-t6
            do i=1,nxy2
               t3 = i-t5
               indice = (j-1)*nxy2+i
               ind1 = deb+(nxy2+2)*(j-1)+(i-1)
               source(indice) = 0.
               sourdel(indice) = 0.
c              -------
c              SOURCES
c              -------
               if (vari_int .eq. 1) then
                  t7 = 1.
                  ii2 = ii
               else
                  t7 = z(1,ii)
                  ii2 = 1
               end if
               do k=1,np
                  t1 = i-(c(1,k)-delta(1,ii))
                  t2 = j-(c(2,k)-delta(2,ii))
                  t8 = a(k,ii2)*t7*exp(-b*((t1**2)+(t2**2)))
                  source(indice) = source(indice) + t8
                  if (ndels.ne.0 .and. dels(k).eq.1) then
                     sourdel(indice) = sourdel(indice) + t8
                  end if
               end do
c              ----
c              FOND
c              ----
               fond(indice) = 0.
               do l=1,2
                  ind2 = (l-1)*(nxy2+2)
                  ind3 = 2*(l-1)
                  do k=1,2
                    fond(indice) = fond(indice) + 
     &                  w(ind3+k)*inter3(ind1+k+ind2) 
                  end do
               end do
               fond(indice) = z(1,ii)*fond(indice) + z(2,ii)
c              ----------------
c              MODELE ANALYTIQUE
c              ----------------
               model(indice) = manaly(6)*z(1,ii)*exp(-(manaly(1)*t3*t3+
     &                         manaly(2)*t4*t4+
     &                         manaly(3)*t3*t4)**alpha)
c              -----------------------
c              FOND + MODELE ANALYTIQUE
c              -----------------------
               fondmodel(indice) = fond(indice) + model(indice)
c              ------------
c              SOMME TOTALE
c              ------------
               tmp2(indice) = fondmodel(indice) + source(indice)
c              ----------------
c              affectation de S
c              ----------------
               tmp3(indice) = s(indice,ii)
            end do
         end do
         do i=1,2*nxy2
            stmp3(i) = ss(i,ii)
         end do


c        IMAGES DE SORTIE:
c        dec---.fits = image déconvoluée
c        model---.fits = modele analytique décalé.
c        back---.fitsn = fond multiplié par z1 additionné à z2 et décalé
c        backmodel---.fits = back + model
c        - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
         results = 'dec' // fin 
         call makeima(results,nxy2,tmp2)
         results = 'model' // fin 
         call makeima(results,nxy2,model)
         results = 'back' // fin 
         call makeima(results,nxy2,fond)
         results = 'backmodel' // fin 
         call makeima(results,nxy2,fondmodel)

c        Lissage de dec par s
c        - - - - - - - - - - - 
         call rlft2(tmp2,stmp2,nxy2,1)
         call produit(tmp2,tmp3,stmp2,stmp3,nxy2)
         call rlft2(tmp2,stmp2,nxy2,-1)

c        Lissage du fond par s
c        - - - - - - - - - - - 
         call rlft2(fondmodel,sfondmodel,nxy2,1)
         call produit(fondmodel,tmp3,sfondmodel,stmp3,nxy2)
         call rlft2(fondmodel,sfondmodel,nxy2,-1)

         if (residu_fin.eq.1 .and. question.eq.'y') then
            do i=1,n2
               if (fondmodel(i) .lt. 0.) fondmodel(i) = 0.
            end do
         end if

c        --------------------------------------------------------
c        ATTENTION: dans cette boucle tmp2 est utilisé pour dec*s 
c        et puis il est directement utilisé pour autre chose
c        --------------------------------------------------------
         if (ndels .eq. 0) then
            do j=1,nxy1
               do i=1,nxy1
                  ind1 = nxy2*pas*(j-1)+pas*(i-1)
                  indice = (j-1)*nxy1+i
                  t1 = (sfbis(indice,ii)-g(indice,ii))*
     &                    sqrt(sig3(indice,ii))
                  fg(indice) = 0.
                  gsm(indice) = 0.
                  do l=1,pas
                     ind2 = (l-1)*nxy2
                     do k=1,pas
                       gsm(indice) = gsm(indice) + tmp2(ind1+k+ind2)
                       tmp(ind1+k+ind2) = t1
                       tmp2(ind1+k+ind2) = t1*t1
                       fg(indice) = fg(indice) + fondmodel(ind1+k+ind2)
                     end do
                  end do
                  fg(indice) = fg(indice)/real(pas*pas)
                  gsm(indice) = gsm(indice)/real(pas*pas)
               end do
            end do
         else
c           Lissage du sourdel par s
c           - - - - - - - - - - - - - 
            call rlft2(sourdel,ssourdel,nxy2,1)
            call produit(sourdel,tmp3,ssourdel,stmp3,nxy2)
            call rlft2(sourdel,ssourdel,nxy2,-1)
            do j=1,nxy1
               do i=1,nxy1
                  ind1 = nxy2*pas*(j-1)+pas*(i-1)
                  indice = (j-1)*nxy1+i
                  t1 = (sfbis(indice,ii)-g(indice,ii))*
     &                    sqrt(sig3(indice,ii))
                  fg(indice) = 0.
                  sg(indice) = 0.
                  gsm(indice) = 0.
                  do l=1,pas
                     ind2 = (l-1)*nxy2
                     do k=1,pas
                       gsm(indice) = gsm(indice) + tmp2(ind1+k+ind2)
                       tmp(ind1+k+ind2) = t1
                       tmp2(ind1+k+ind2) = t1*t1
                       fg(indice) = fg(indice) + fondmodel(ind1+k+ind2)
                       sg(indice) = sg(indice) + sourdel(ind1+k+ind2)
                     end do
                  end do
                  fg(indice) = fg(indice)/real(pas*pas)
                  sg(indice) = sg(indice)/real(pas*pas)
                  gsm(indice) = gsm(indice)/real(pas*pas)
               end do
            end do
c           IMAGE 
c           source_sm---.fits : (source à supprimer)*s
c           - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            results = 'source_sm' // fin
            call makeima(results,nxy1,sg)
         end if

c        IMAGE 
c        g_sm---.fits : (dec*s)
c        - - - - - - - - - - - - - - - - - - - - - - - - - - - -
         results = 'g_sm' // fin
         call makeima(results,nxy1,gsm)

c        IMAGE 
c        fondmodel_sm---.fits : (fond decalé z1 et z2 + model)*s
c        - - - - - - - - - - - - - - - - - - - - - - - - - - - -
         results = 'backmodel_sm' // fin
         call makeima(results,nxy1,fg)

         call rlft2(tmp2,stmp2,nxy2,1)
         call produit(tmp2,tmp3,stmp2,stmp3,nxy2)
         call rlft2(tmp2,stmp2,nxy2,-1)

c        IMAGES DE SORTIE:
c        resi---.fits = image des résidus
c        resi_sm---.fits = image des résidus au carré, lissés
c        - - - - - - - - - - - - - - - - - - - - - - - - - - -
         results = 'resi' // fin
         call makeima(results,nxy2,tmp)
         results = 'resi_sm' // fin
         call makeima(results,nxy2,tmp2)


         if (residu_fin .eq. 1) then
            do j=1,nxy2
               inter(j*(nxy2+2)+1) = tmp(j*nxy2)
               inter2(j*(nxy2+2)+1) = tmp2(j*nxy2)
               do i=1,nxy2
                  indice = (j-1)*nxy2+i
                  indice2 = j*(nxy2+2)+1+i
                  inter(indice2) = tmp(indice)
                  inter2(indice2) = tmp2(indice)
               end do
               inter((j+1)*(nxy2+2)) = tmp((j-1)*nxy2+1)
               inter2((j+1)*(nxy2+2)) = tmp2((j-1)*nxy2+1)
            end do
            do i=1,nxy2+2
               inter(i) = inter((nxy2+2)*nxy2+i)
               inter2(i) = inter2((nxy2+2)*nxy2+i)
               inter((nxy2+2)*(nxy2+1)+i) = inter(nxy2+2+i)
               inter2((nxy2+2)*(nxy2+1)+i) = inter2(nxy2+2+i)
            end do

            do j=1,nxy2
               do i=1,nxy2
                  ind1 = deb2+(nxy2+2)*(j-1)+(i-1)
                  indice = (j-1)*nxy2+i
                  t1 = 0.
                  t2 = 0.
                  t3 = 0.
                  do l=1,2
                     ind2 = (l-1)*(nxy2+2)
                     ind3 = 2*(l-1)
                     do k=1,2
                       t1 = t1 + w2(ind3+k)*inter(ind1+k+ind2) 
                       t2 = t2 + w2(ind3+k)*inter2(ind1+k+ind2) 
                     end do
                  end do
                  resim(indice) = resim(indice) + t1
                  resismm(indice) = resismm(indice) + t2
                  resireduit(indice) = resireduit(indice) +t1*t1
               end do
            end do
         end if
      end do

c     FIN DE LA BOUCLE SUR LE NOMBRE D'IMAGES
c     - - - - - - - - - - - - - - - - - - - -

      if (residu_fin .eq. 1) then
         do i=1,n2
            resim(i) = resim(i)/real(m)
            resismm(i) = resismm(i)/real(m)
            resireduit(i) = resireduit(i)/real(m)
         end do
         results = 'resi_moyenne' // '.fits'
         call makeima(results,nxy2,resim)
         results = 'resi_sm_moyenne' // '.fits'
         call makeima(results,nxy2,resismm)
         results = 'resi_reduit' // '.fits'
         call makeima(results,nxy2,resireduit)
      end if

c     BACKUP OF RESULTS IN 2 OUTPUT FILES
c     - - - - - - - - - - - - - - - - - - 

      write(2,'(A12,E20.13)') 'Minimum   : ',fp
      write(2,'(A12,E20.13)') 'Chi carré : ',qi
      write(2,*)
      write(2,'(A35)') '* Intensité et coordonnées (x,y) :'
      write(2,*)
      do k=1,np
         write(2,'(A25,I4)') '  - Numéro de la source: ',k 
         do i=1,m2
            write(2,'(A10,3(F16.6,A1))') '          ',a(k,i),
     &                ' ',
     &               c(1,k)-delta(1,i),' ',
     &               c(2,k)-delta(2,i),' '
            write(3,'(F16.6,A1,$)') a(k,i),' '
        end do
        write(3,*)  
        write(3,'(2F12.6)') c(1,k),c(2,k)
        write(2,*)
      end do
      write(3,'(A55)') '------------------------------------------------
     &-------'
      write(3,'(A55)') '|Valeurs initiales de z1, z2, delta1 et delta2  
     &      |'
      write(3,'(A55)') '|nb * (4 valeurs) où nb = nombre d''images      
     &      |'
      write(3,'(A55)') '------------------------------------------------
     &-------'
      write(2,'(A47)') '* Valeurs finales de z1, z2, delta1 et delta2 :'
      do i=1,m
         write(2,'(A10,4(F12.6,A1))') '          ',z(1,i),' ',
     &   z(2,i),' ',delta(1,i),' ',delta(2,i),' '
         write(3,'(4F12.6)') z(1,i),z(2,i),delta(1,i),
     &                       delta(2,i)
      end do
      write(2,*) 

      write(3,'(A55)') '------------------------------------------------
     &-------'
      write(3,'(A55)') '|Modèle analytique: valeurs de Io A B C Cx et Cy       
     &      |'
      write(3,'(A55)') '|     (6 valeurs Io A B C Cx Cy)                   
     &      |'
      write(3,'(A55)') '------------------------------------------------
     &-------'

      write(2,'(A46)') '* Modèle analytique: valeurs de Io A B C Cx Cy'
      write(3,'(E20.13,A1,$)') manaly(6),' '
      write(2,'(E20.13,A1,$)') manaly(6),' '
      do i=1,5
         write(3,'(F13.6,A1,$)') manaly(i),' '
         write(2,'(F13.6,A1,$)') manaly(i),' '
      end do
      write(3,*) 
      write(2,*) 
      write(2,*) 

      return
      end

C     ==============================================================================================
C     ==============================================================================================
c     SSSSSSSSS     A     NN      N SSSSSSSSS      M       M  OOOOOOO  DDDDDDDD  EEEEEEEEE L
c     S            A A    N N     N S              MM     MM O       O D       D E         L
c     SSSSSSSSS   A   A   N   N   N SSSSSSSSS      M M   M M O       O D       D EEEEE     L 
c             S  AAAAAAA  N     N N         S      M  M M  M O       O D       D E         L 
c     SSSSSSSSS A       A N      NN SSSSSSSSS      M   M   M  OOOOOOO  DDDDDDDD  EEEEEEEEE LLLLLLLLL
C     ==============================================================================================
C     ==============================================================================================


c     ------------------
c     SUBROUTINE: minimi
C     ------------------
c     MINIMISATION BY DECREASING STEPS.
c     --------------------

      subroutine minimi(iter,itmax,modu,qimin)

      implicit none

      include 'param_dec.f'

      real*4 eps
      integer iter,itmax,modu
      parameter (eps=1.E-10)

      real*4 z(2,nbg),p(nbr2),delta(2,nbg),a(npic,nbg),c(2,npic)
      real*4 da(npic,nbg),dc(2,npic),df(nbr2),dz(2,nbg),dd(2,nbg)
      real*4 nda(npic),ndc,ndf,ndz(2),ndd
      real*4 dfN(nbr2),pN(nbr2)
      real*4 daN(npic,nbg),dcN(2,npic),aN(npic,nbg),cN(2,npic)
      real*4 zN(2,nbg),deltaN(2,nbg),dzN(2,nbg),ddN(2,nbg)
      real*4 fp,qi,fpA,qimin,qiA
      real*4 ndamin(npic),ndcmin,ndfmin,ndzmin(2)
      real*4 nddmin,vecteurqi(10)
      real*4 xif(nbr2),xia(npic,nbg),xic(2,npic),xiz(2,nbg)
      real*4 xid(2,nbg)
      real*4 xifA(nbr2),xiaA(npic,nbg),xicA(2,npic),xizA(2,nbg)
      real*4 xidA(2,nbg)
      integer testh,posi,n1,n2,m,np,indi,condi,its,i,ind,j
      integer arret,arret2,ii,jj,aug,m2

      common /delta2/ da,dc,df,dz,dd
      common /deltacons/ nda,ndc,ndf,ndz,ndd
      common /deltacons2/ ndamin,ndcmin,ndfmin,ndzmin
      common /deltacons3/ nddmin
      common /variables/ p,z,a,c,delta
      common /tailles/ n1,n2,np,m,m2
      common /derivees/ xif,xia,xic,xiz,xid
      common /minimum/ fp,qi
      common /positif/ posi

      aug = 0
      arret = 0
      arret2 = 1

c     COMPUTATION OF MINIMUM AND DERIVTIVES:
c     - - - - - - - - - - - - - - - - - - -
      call inifunc_dfunc(p,z,a,c,delta)

      vecteurqi(1) = qi
      do i=2,10
         vecteurqi(i) = 100000.
      end do

      indi = m+2
      condi = indi*np


c     Sauvegarde des anciens pas, car si le minimum
c     augmente, il faut revenir avec les ancien pas 
c     et les diviser par 2
c     - - - - - - - - - - - - - - - - - - - - - - - 
      do i=1,n2
         dfN(i) = df(i)
      end do
      do i=1,np
         do j=1,m2
            daN(i,j) = da(i,j)
         end do
         dcN(1,i) = dc(1,i)
         dcN(2,i) = dc(2,i)
      end do
      do j=1,m
         do i=1,2
            dzN(i,j) = dz(i,j)
            ddN(i,j) = dd(i,j)
         end do
      end do
      do i=1,2
         zN(i,1) = z(i,1)
         deltaN(i,1) = delta(i,1) 
      end do
      
      do its=1,itmax

         write(*,*) 'Iteration ', its,', min qi: ',fp,qi
         if (aug .eq. 0) then
c           write(*,*) '================================================'
         else
c           write(*,*) '************************************************'
c           write(*,*) 
           aug = 0
         end if
         iter = its

c        MODIFICATION OF F
c        - - - - - - - - -
         do i=1,n2
            if (xif(i) .lt. 0.) then
                pN(i) = p(i) + dfN(i)
            else
               if (posi .eq. 0) then
                  pN(i) = p(i) - dfN(i)
               else
                  if (p(i)-dfN(i) .ge. 0) then
                      pN(i) = p(i) - dfN(i)
                  else
                      pN(i) = 0.
                  end if
              end if
            end if
         end do

c        MODIFICATION OF A, C1 AND C2
c        - - - - - - - - - - - - - - -
         do i=1,np
c            write(*,'(''   a...a c1 c2   : '',$)')
            do j=1,m2
               if (xia(i,j) .lt. 0.) then
                  aN(i,j) = a(i,j) + daN(i,j)
               else
                  aN(i,j) = a(i,j) - daN(i,j)
               end if
c               write(*,'(E12.6,A1,$)') aN(i,j),' '
            end do
            do j=1,2
               if(xic(j,i) .lt. 0.) then
                  cN(j,i) = c(j,i) + dcN(j,i)
               else
                  cN(j,i) = c(j,i) - dcN(j,i)
               end if
            end do
c            write(*,'(2(E12.6,A1))') cN(1,i),' ',cN(2,i),' '
         end do

c        MODIFICATION OF Z AND DELTA 
c           NOTE: THE PARAMETER OF IMAGE 1 ARE NOT MODIFIED
c        - - - - - - - - - - - - - - - - - - - - - - - - - -
c         write(*,*) '  z1  z2        : ',zN(1,1),zN(2,1)
c         write(*,*) '  delta1 delta2 : ',deltaN(1,1),deltaN(2,1)
         do i=2,m
            do j=1,2
               if (xiz(j,i) .lt. 0.) then
                  zN(j,i) = z(j,i) + dzN(j,i)
               else
                  zN(j,i) = z(j,i) - dzN(j,i)
               end if
               if (xid(j,i) .lt. 0.) then
                  deltaN(j,i) = delta(j,i) + ddN(j,i)
               else
                  deltaN(j,i) = delta(j,i) - ddN(j,i)
               end if
            end do
c           write(*,*) '  z1  z2        : ',zN(1,i),zN(2,i)
c           write(*,*) '  delta1 delta2 : ',deltaN(1,i),deltaN(2,i)
         end do

c         write(*,*) '  f : ',pN(1),pN(512),pN(1024)

c        Sauvegarde des anciennes dérivées avant un nouveau 
c        calcul avec les nouvelles valeurs.
c        - - - - - - - - - - - - - - - - - - - - - - - - - -
         fpA = fp
         qiA = qi
         do i=1,n2
            xifA(i) = xif(i)
         end do
         do i=1,np
            do j=1,m2
               xiaA(i,j) = xia(i,j)
            end do
            xicA(1,i) = xic(1,i)
            xicA(2,i) = xic(2,i)
         end do
         do i=1,m
            xizA(1,i) = xiz(1,i)
            xizA(2,i) = xiz(2,i)
            xidA(1,i) = xid(1,i)
            xidA(2,i) = xid(2,i)
         end do

c         write(*,*) '---------------------------------------'

c        AUTOMATIC BACKUP AFTER X ITERATIONS:
c        - - - - - - - - - - - - - - - - - - 
         call inifunc_dfunc(pN,zN,aN,cN,deltaN)

         ii = mod(its+1,10)
         jj = ii+1
         if (ii.eq.0) ii = 10
         vecteurqi(ii) = qi
         if (abs(abs(vecteurqi(ii)) - 
     &        abs(vecteurqi(jj))) .le. qimin) then
            write(*,*)
            write(*,*) '===================================='
            write(*,*) '  LA DIFFERENCE DE KHI CARRE ENTRE '
            write(*,*) '  10 ITERATIONS EST INSIGNIFIANTE'
            write(*,*) '===================================='
            return
         end if

         if (mod(its,modu) .eq. 0) then
            write(2,*) 'Nombre d''itérations dans minimi  : ',iter 
            write(2,*) 'Nombre d''itérations dans gradient: 0'
            write(2,*) 
            call decompos(0)
            do j=1,(m+2)*np+m+13
               backspace(unit=2)
            end do
            do j=1,2*np+m+9
               backspace(unit=3)
            end do
         end if

c        Test la valeur du minimum:
c        Si elle diminue c'est que les valeurs étaient bonnes
c           et on en recalcul de nouvelles
c        Sinon on revient au ancien pas et on les divise par 2
c        - - - - - - - - - - - - - - - - - - - - - - - - - - - 

         if (fpA .gt. fp) then

            if (arret .ne. 0) arret = 0

c           CHECK OF THE SIGN OF THE DERIVATIVES OF F 
c           AND MODIFICATION OF STEP.
c           - - - - - - - - - - - - - - - - - - - - - 
            do i=1,n2
               df(i) = dfN(i)
               if (xifA(i)*xif(i) .lt. 0.)  then
                  dfN(i) = df(i)/2.
               else
                  if (df(i)*1.1 .le. ndf) then
                     dfN(i)= df(i)*1.1
                  else
                     dfN(i)= df(i)
                  end if
               end if
               if (arret2.eq.1 .and. dfN(i) .gt. ndfmin) arret2 = 0 
               p(i) = pN(i)
            end do

c           CHECK OF THE SIGN OF THE DERIVATIVES OF A, C1 AND C2
c           AND MODIFICATION OF STEP.
c           - - - - - - - - - - - - - - - - - - - - - - - - - - 
            do i=1,np
               do j=1,m2
                  da(i,j) = daN(i,j)
                  if (xiaA(i,j)*xia(i,j) .lt. 0.) then
                     daN(i,j) = da(i,j)/2.
                  else
                     if (da(i,j)*1.1 .le. nda(i)) then
                        daN(i,j) = da(i,j)*1.1
                     else
                        daN(i,j) = da(i,j)
                     end if
                  end if
                  a(i,j) = aN(i,j)
                  if (arret2.eq.1 .and. daN(i,j).gt.ndamin(i)) arret2=0 
               end do
               do j=1,2
                  dc(j,i) = dcN(j,i)
                  if (xicA(j,i)*xic(j,i) .lt. 0.) then
                     dcN(j,i) = dc(j,i)/2.
                  else
                     if (dc(j,i)*1.1 .le. ndc) then
                       dcN(j,i) = dc(j,i)*1.1
                     else
                        dcN(j,i) = dc(j,i)
                     end if
                  end if
                  c(j,i) = cN(j,i) 
                  if (arret2.eq.1 .and. dcN(j,i).gt.ndcmin) arret2=0 
               end do
            end do

c           CHECK OF THE SIGN OF THE DERIVATIVES OF Z AND DELTA 
c           AND MODIFICATION OF STEP.
c           - - - - - - - - - - - - - - - - - - - - - - - - - - 
            do j=2,m
               do i=1,2
                  dz(i,j) = dzN(i,j)
                  if (xizA(i,j)*xiz(i,j) .lt. 0.) then
                     dzN(i,j) = dz(i,j)/2.
                  else 
                    if (dz(i,j)*1.1 .le. ndz(i)) then
                       dzN(i,j) = dz(i,j)*1.1
                    else
                       dzN(i,j) = dz(i,j)
                    end if
                  end if
                  z(i,j) = zN(i,j)
                  if (arret2.eq.1 .and. dzN(i,j).gt.ndzmin(i)) arret2=0 

                  dd(i,j) = ddN(i,j)
                  if (xidA(i,j)*xid(i,j) .lt. 0.) then
                     ddN(i,j) = dd(i,j)/2.
                  else
                    if (dd(i,j)*1.4 .le. ndd) then
                       ddN(i,j) = dd(i,j)*1.4
                    else
                       ddN(i,j) = dd(i,j)
                    end if
                  end if
                  delta(i,j) = deltaN(i,j)
                  if (arret2.eq.1 .and. ddN(i,j).gt.nddmin) arret2=0 
               end do
            end do

            if (arret2 .eq. 1) then
                write(*,*)
                write(*,*) '================================='
                write(*,*) '  TOUS LES PAS SONT TROP PETITS'
                write(*,*) '================================='
                return
            end if
            arret2 = 1

         else

            aug = 1
            arret = arret + 1
c            write(*,*) its+1,' (M sans modèle)   min qi: ',fp,qi

c            write(*,*)
            write(*,*) 'Chi-square increase number ',arret
c            write(*,*) '==============================================='
c            write(*,*) '****** ON REPART DES VALEURS SUIVANTES : ******'

            do i=1,np
c               write(*,'(''   a...a c1 c2   : '',$)')
               do j=1,m2
c                  write(*,'(E12.6,A1,$)') a(i,j),' '
               end do
c               write(*,'(2(E12.6,A1))') c(1,i),' ',c(2,i),' '
            end do

            do i=1,m
c               write(*,*) '  z1  z2        : ',z(1,i),z(2,i)
c               write(*,*) '  delta1 delta2 : ',delta(1,i),delta(2,i)
            end do

c            write(*,*) '  f : ',p(1),p(512),p(1024)

            if (arret .eq. 10) then
               write(*,*)
               write(*,*) '=================================='
               write(*,*) '  LE MINIMUM A ETE DEPASSE 10 fois'
               write(*,*) '=================================='
               return
            end if
   
c           FOND
c           - - -   
            do i=1,n2
               if (xifA(i)*xif(i) .lt. 0.)  then
                  df(i) = df(i)/2.
               end if
               dfN(i) = df(i)
               xif(i) = xifA(i)
            end do

c           SOURCES PONCTUELLES
c           - - - - - - - - - - 
            do i=1,np
               do j=1,m2
                  if (xiaA(i,j)*xia(i,j) .lt. 0.) then
                     da(i,j) = da(i,j)/2.
                  end if
                  daN(i,j) = da(i,j)
                  xia(i,j) = xiaA(i,j)
               end do
               do j=1,2
                  if (xicA(j,i)*xic(j,i) .lt. 0.) then
                     dc(j,i) = dc(j,i)/2.
                  end if
                  dcN(j,i) = dc(j,i)
                  xic(j,i) = xicA(j,i)
               end do
            end do

c           Z ET DECALAGES.
c           - - - - - - - - 
            do j=2,m
               do i=1,2
                  if (xizA(i,j)*xiz(i,j) .lt. 0.) then
                     dz(i,j) = dz(i,j)/2.
                  end if
                  dzN(i,j) = dz(i,j)
                  xiz(i,j) = xizA(i,j)

                  if (xidA(i,j)*xid(i,j) .lt. 0.) then
                     dd(i,j) = dd(i,j)/2.
                  end if
                  ddN(i,j) = dd(i,j)
                  xid(i,j) = xidA(i,j)
               end do
            end do

            fp = fpA
            qi = qiA
         end if
      end do

      write(*,*)
      write(*,*) '=========================================='
      write(*,*) '  NOMBRE D''ITERATIONS EXCEDE DANS MINIMI'
      write(*,*) '=========================================='

      return
      end

c     -------------------------
c     SUBROUTINE: inifunc_dfunc
c     -------------------------

      subroutine inifunc_dfunc(p,z,a,c,delta)

      implicit none

      include 'param_dec.f'

      integer nb4
      parameter(nb4=nbr2+4*(xy2+1))

      real*4 a(npic,nbg),c(2,npic),b,p(nbr2),z(2,nbg),delta(2,nbg)
      real*4 g(nbr1,nbg),sig2(nbr1,nbg),sig3(nbr1,nbg),s(nbr2,nbg)
      real*4 ss(2*xy2,nbg),trs(nbr2,nbg),strs(2*xy2,nbg)
      real*4 far(nbr2,nbg),far2(nbr2,nbg)
      real*4 sf(nbr2),ssf(2*xy2),sfbis(nbr1,nbg),sf2(nbr2),ssf2(2*xy2)
      real*4 sfbis2(nbr1),sfbis3,src7bis(nbr1)
      real*4 rc(nbr2,6),srcbis,src2bis,src3bis,src4bis,src5bis,src6bis
      real*4 delx,dely,w(9),shfz(nb4,nbg),inter(nb4)
      real*4 tm,tm2,tm3,tamp,tamp1,tamp2,tamp3,t1,t2,t3,t4,t5,som1,som2
      real*4 tmp(nbr2),stmp(2*xy2),tmp2(nbr2),stmp2(2*xy2),tmp3(nbr2)
      real*4 stmp3(2*xy2),tmp4(nbr2),stmp4(2*xy2),tmp5(nbr2)
      real*4 stmp5(2*xy2),tmp6(nbr2),stmp6(2*xy2),tabl(nbr2,6)
      real*4 tmp9(nbr2),stmp9(2*xy2)
      real*4 rr(nbr2),frf(nbr2),srr(2*xy2)
      real*4 xif(nbr2),xia(npic,nbg),xic(2,npic),xiz(2,nbg)
      real*4 xid(2,nbg),xima(6)
      real*4 ebc,alpha,fp,qi,fwhm(nbg),bg(nbg),cx,cy
      integer n1,n2,np,m,indice,indice2,ind,ind1,ind2,ind3,ind4,indi
      integer i,ii,iii,j,jj,j2,k,k2,l,pas,deb,nxy1,nxy2,vari_int
      integer debutx,debuty,finx,finy,dif,m2,ii2
      character*20 resultat

      common /gr1/ g,s,sig2,ss
      common /param/ nxy1,nxy2,pas
      common /parametre_alpha/ b,alpha
      common /gr5/ sfbis
      common /entropie/ rr,frf,srr
      common /sig/ sig3
      common /tailles/ n1,n2,np,m,m2
      common /minimum/ fp,qi
      common /trans/ trs,strs
      common /derivees/ xif,xia,xic,xiz,xid
      common /gaussienne/ fwhm,bg
      common /variation_intensite/ vari_int

c     CALCULATION OF : FAR(j,i) = z(1,i)*F(j) + z(2,i)
c                      FAR2(j,i) = SOMMEsurK (A(k,i)*R(C(k)-delta(i)))
c                      WHERE i = IMAGE NUMBER
c                            j = INDEX OF THE COMPUTED PARAMETER
c                            k = NUMBER OF POINT SOURCES
c     - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


      do i=1,n2
         tmp2(i) = p(i)
         xif(i) = 0.
      end do
      do ii=1,m
         t1 = z(1,ii)
         t2 = z(2,ii)
         do i=1,n2
            far(i,ii) = t1*p(i)+t2
            far2(i,ii) = 0.
         end do
      end do

c     CALCULATION OF R CONVOLVED WITH F, USED IN THE SMOOTHING TERM
c     AND CALCULATION OF THIS TERM:
c     - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
      call rlft2(tmp2,stmp2,nxy2,1)
      call produit(tmp2,rr,stmp2,srr,xy2)
      call rlft2(tmp2,stmp2,nxy2,-1)

      fp = 0.
      do i=1,n2
         frf(i) = p(i)-tmp2(i)
         fp = fp + frf(i)**2
      end do

      do k=1,np
         xic(1,k) = 0.
         xic(2,k) = 0.
         do ii=1,m
            if (vari_int .eq. 1) then
               t2 = a(k,ii)
            else
               t2 = a(k,1)*z(1,ii)
            end if
            t3 = c(1,k)-delta(1,ii)
            t4 = c(2,k)-delta(2,ii)
            xia(k,ii) = 0.
            do j=1,nxy2
               tamp2 = j-t4
               ind2 = (j-1)*nxy2
               do i=1,nxy2
                  ind = i+ind2
                  tamp1 = i-t3
                  tm = exp(-b*(tamp1*tamp1+tamp2*tamp2))
                  far2(ind,ii) = far2(ind,ii) + t2*tm
               end do
            end do
         end do
      end do

      do ii=1,m
         xiz(1,ii) = 0.
         xiz(2,ii) = 0.
         xid(1,ii) = 0.
         xid(2,ii) = 0.
      end do

c     CALCULATION OF W (WEIGHT OF PIXELS) FOR THE SHIFT BETWEEN IMAGES
c     - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
      qi = 0.
      do ii=1,m
         if (delta(1,ii) .lt. 0.) then
            delx = 1+delta(1,ii)
         else
            delx = delta(1,ii)
         end if
         if (delta(2,ii) .lt. 0.) then
            dely = 1+delta(2,ii)
         else
            dely = delta(2,ii)
         end if
         if (pas .eq. 1) then
c           WHEN ONE STAYS IN BIG PIXELS
c           - - - - - - - - - - - - - - 
            w(1) = (1-delx)*(1-dely)
            w(2) = delx*(1-dely)
            w(3) = dely*(1-delx)
            w(4) = delx*dely
         else
c           WHEN ONE CHANGES TO SMALL PIXELS
c           - - - - - - - - - - - - - - -
            w(1) = (1-delx)*(1-dely)/4
            w(2) = (1-dely)/4
            w(3) = delx*(1-dely)/4
            w(4) = (1-delx)/4
            w(5) = 0.25
            w(6) = delx/4
            w(7) = dely*(1-delx)/4
            w(8) = dely/4
            w(9) = delx*dely/4
         end if

         if (delta(1,ii) .ge. 0. .and. delta(2,ii) .ge. 0.) then
            deb = nxy2+3
         else if (delta(1,ii) .ge. 0. .and. delta(2,ii) .lt. 0.) then
            deb = 1
         else if (delta(1,ii) .lt. 0. .and. delta(2,ii) .ge. 0.) then
            deb = nxy2+2
         else
            deb = 0
         end if 

c        CALCULATION OF S CONVOLVED WITH FAR AND S CONVOLVED WITH FAR2,
c        AND CALCULATION OF THE MINIMUM
c        - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

         do i=1,n2
            sf(i) = far(i,ii)
            sf2(i) = far2(i,ii)
            tmp(i) = s(i,ii)
            tmp2(i) = 0.
            tmp3(i) = 0.
            tmp9(i) = 0.
         end do   
         do i=1,xy2*2
            stmp(i) = ss(i,ii)
         end do

         call rlft2(sf,ssf,nxy2,1)
         call rlft2(sf2,ssf2,nxy2,1)
         call produit(sf,tmp,ssf,stmp,nxy2)
         call produit(sf2,tmp,ssf2,stmp,nxy2)
         call rlft2(sf,ssf,nxy2,-1)
         call rlft2(sf2,ssf2,nxy2,-1)

c        SF = (S)*(Z1*F+Z2) AND SF2 = (S)*(SOMME(A*R(C-DELTE))

c        SF MUST BE SHIFTED
c        THE TABLE IS MODIFIED AND THE STARTING POINT IS COMPUTED
c        YOU CHANGE FROM BIG PIXELS TO SMALL PIXELS TO TAKE INTO
c        ACCOUNT THE WEIGHTS OF PIXELS.
c        - - - - - - - - - - - - - - - - - - - - - - - - - - -

         do j=1,nxy2
            inter(j*(nxy2+2)+1) = sf(j*nxy2)
            do i=1,nxy2
               indice = (j-1)*nxy2+i
               indice2 = j*(nxy2+2)+1+i
               inter(indice2) = sf(indice)
            end do
            inter((j+1)*(nxy2+2)) = sf((j-1)*nxy2+1)
         end do
         do i=1,nxy2+2
            inter(i) = inter((nxy2+2)*nxy2+i)
            inter((nxy2+2)*(nxy2+1)+i) = inter(nxy2+2+i)
         end do

         do i=1,n2+4*(nxy2+1)
            shfz(i,ii) = inter(i)
         end do

         do j=1,nxy1
            do i=1,nxy1
               ind1 = deb+(nxy2+2)*pas*(j-1)+pas*(i-1)
               indice = (j-1)*nxy1+i
               sfbis2(indice) = 0.
               do l=1,pas+1
                  ind2 = (l-1)*(nxy2+2)
                  ind3 = (pas+1)*(l-1)
                  do k=1,pas+1
                    sfbis2(indice) = sfbis2(indice) + 
     &                              w(ind3+k)*inter(ind1+k+ind2) 
                 end do
               end do
            end do
         end do

c        SFBIS2 = SF SHIFTED AND PUT IN BIG PIXELS.


c        SF2 IS ALREADY SHIFTED, ON ONLY CHANGE FROM SMALL TO BIG PIXELS
c        - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
         do j=1,nxy1
            do i=1,nxy1
               ind1 = nxy2*pas*(j-1)+pas*(i-1)
               indice = (j-1)*nxy1+i
               sfbis(indice,ii) = 0.
               do l=1,pas
                  ind2 = (l-1)*nxy2
                  do k=1,pas
                    sfbis(indice,ii) = sfbis(indice,ii) + 
     &                              sf2(ind1+k+ind2) 
                  end do
               end do
               sfbis(indice,ii) = sfbis(indice,ii)/real(pas**2) +
     &                            sfbis2(indice)
               tamp = (sfbis(indice,ii)-g(indice,ii))**2 
               qi = qi + tamp*sig3(indice,ii)
               fp = fp + tamp*sig2(indice,ii)
            end do
         end do
 
c        SFBIS = SFBIS2 + SF2 PUT IN BIG PIXELS
c        - - - - - - - - - - - - - - - - - - - 

c        CALCULATION OF DERIVATIVES OF A, C1 ET C2
c        - - - - - - - - - - - - - - - - - - - - - 

         do k=1,np
            cx = c(1,k)-delta(1,ii)
            cy = c(2,k)-delta(2,ii)
            if (vari_int .eq. 1) then
               t3 = a(k,ii)
               ii2 = ii
               t4 = 1.
               do j=1,nxy2
                  tamp2 = j-cy
                  ind2 = (j-1)*nxy2
                  do i=1,nxy2
                     ind = i+ind2
                     tamp1 = i-cx
                     ebc= exp(-b*((tamp1*tamp1)+(tamp2*tamp2)))
                     tmp2(ind) = tmp2(ind) + ebc*tamp1*t3
                     tmp3(ind) = tmp3(ind) + ebc*tamp2*t3
                  end do
               end do
            else
               t3 = a(k,1)*z(1,ii)
               ii2 = 1
               t4 = z(1,ii)
               do j=1,nxy2
                  tamp2 = j-cy
                  ind2 = (j-1)*nxy2
                  do i=1,nxy2
                     ind = i+ind2
                     tamp1 = i-cx
                     ebc= exp(-b*((tamp1*tamp1)+(tamp2*tamp2)))
                     tmp2(ind) = tmp2(ind) + ebc*tamp1*t3
                     tmp3(ind) = tmp3(ind) + ebc*tamp2*t3
                     tmp9(ind) = tmp9(ind) + ebc*a(k,1)
                  end do
               end do
            end if

            cx = cx/2.
            cy = cy/2.
            debutx = anint(cx)-fwhm(ii)
            debuty = anint(cy)-fwhm(ii)
            finx = anint(cx)+fwhm(ii)
            finy = anint(cy)+fwhm(ii)
            if (debutx .le. 0) then
               dif = 1-debutx
               debutx = 1
               finx = finx-dif
            end if
            if (debuty .le. 0) then
               dif = 1-debuty
               debuty=1
               finy = finy-dif
            end if
            if (finx .gt. nxy1) then
               dif = finx-nxy1
               debutx = debutx+dif
               finx=nxy1
            end if
            if (finy .gt. nxy1) then
               dif = finy-nxy1
               debuty = debuty+dif
               finy = nxy1
            end if
            do j=debuty,finy
               tamp2 = j-cy
               do i=debutx,finx
                  tamp1 = i-cx
                  indice = (j-1)*nxy1+i
                  ebc = exp(-bg(ii)*((tamp1*tamp1)+(tamp2*tamp2)))
                  tamp3 = (sfbis(indice,ii)-g(indice,ii))
     &                     *sig2(indice,ii)
                  xia(k,ii2) = xia(k,ii2) + ebc*tamp3*t4
                  xic(1,k) = xic(1,k) + t3*ebc*tamp3*tamp1
                  xic(2,k) = xic(2,k) + t3*ebc*tamp3*tamp2
               end do
            end do
         end do
c        ---------------------------------------------
c        FIN DE LA BOUCLE SUR LE NOMBRE DE SOURCES (K)
c        ---------------------------------------------

c        CALCULATION OF DERIVATIVES OF Z AND DELTA
c        - - - - - - - - - - - - - - - - - - - - - 
         if (ii .ne. 1) then

            if (vari_int .eq. 0) then
               call rlft2(tmp9,stmp9,nxy2,1)
               call produit(tmp9,tmp,stmp9,stmp,nxy2)
               call rlft2(tmp9,stmp9,nxy2,-1)
               do j=1,nxy1
                  do i=1,nxy1
                     ind4 = nxy2*pas*(j-1)+pas*(i-1)
                     indice = (j-1)*nxy1+i
                     src7bis(indice) = 0.
                     do l=1,pas
                        ind2 = (l-1)*nxy2
                        do k2=1,pas
                           src7bis(indice) = src7bis(indice) 
     &                                       + tmp9(ind4+k2+ind2)  
                        end do
                     end do
                     src7bis(indice) = src7bis(indice)/real(pas**2)
                  end do
               end do
            else
               do i=1,n1
                  src7bis(i) = 0.
               end do
            end if


            do i=1,n2
               tmp4(i) = p(i)
            end do
            call rlft2(tmp4,stmp4,nxy2,1)
            call rlft2(tmp6,stmp6,nxy2,1)
            call rlft2(tmp2,stmp2,nxy2,1)
            call rlft2(tmp3,stmp3,nxy2,1)
            call produit(tmp4,tmp,stmp4,stmp,nxy2)
            call produit(tmp6,tmp,stmp6,stmp,nxy2)
            call produit(tmp2,tmp,stmp2,stmp,nxy2)
            call produit(tmp3,tmp,stmp3,stmp,nxy2)
            call rlft2(tmp4,stmp4,nxy2,-1)
            call rlft2(tmp6,stmp6,nxy2,-1)
            call rlft2(tmp2,stmp2,nxy2,-1)
            call rlft2(tmp3,stmp3,nxy2,-1)

            do j=1,nxy2
               inter(j*(nxy2+2)+1) = tmp4(j*nxy2)
               do i=1,nxy2
                  indice = (j-1)*nxy2+i
                  indice2 = j*(nxy2+2)+1+i
                  inter(indice2) = tmp4(indice)
               end do
               inter((j+1)*(nxy2+2)) = tmp4((j-1)*nxy2+1)
            end do
            do i=1,nxy2+2
               inter(i) = inter((nxy2+2)*nxy2+i)
               inter((nxy2+2)*(nxy2+1)+i) = inter(nxy2+2+i)
            end do

            do j=1,nxy1
               do i=1,nxy1
                  ind1 = deb+(nxy2+2)*pas*(j-1)+pas*(i-1)
                  ind4 = nxy2*pas*(j-1)+pas*(i-1)
                  indice = (j-1)*nxy1+i
                  srcbis = 0.
                  src2bis = 0.
                  src3bis = 0.
                  src4bis = 0.
                  tamp2 = (sfbis(indice,ii)-g(indice,ii))
     &                    *sig2(indice,ii)
                  do l=1,pas+1
                     ind2 = (l-1)*(nxy2+2)
                     ind3 = (pas+1)*(l-1)
                     do k2=1,pas+1
                        srcbis = srcbis + 
     &                           w(ind3+k2)*inter(ind1+k2+ind2)  
                     end do
                  end do
                  do l=1,pas
                     ind2 = (l-1)*nxy2
                     do k2=1,pas
                        src2bis = src2bis + tmp2(ind4+k2+ind2)  
                        src3bis = src3bis + tmp3(ind4+k2+ind2)  
                        src4bis = src4bis + tmp6(ind4+k2+ind2)
                        tmp5(ind4+k2+ind2) = tamp2
                     end do
                  end do
                  src2bis = src2bis/real(pas**2)
                  src3bis = src3bis/real(pas**2)
                  src4bis = src4bis/real(pas**2)
                  if (pas .eq. 1) then
                     som1 = shfz(ind1+1,ii)*(dely-1) +
     &                      shfz(ind1+2,ii)*(1-dely) -
     &                      shfz(ind1+(nxy2+2)+1,ii)*dely +
     &                      shfz(ind1+(nxy2+2)+2,ii)*dely
                     som2 = shfz(ind1+1,ii)*(delx-1) -
     &                      shfz(ind1+2,ii)*delx +
     &                      shfz(ind1+(nxy2+2)+1,ii)*(1-delx) +
     &                      shfz(ind1+(nxy2+2)+2,ii)*delx
                  else
                    som1 = (shfz(ind1+1,ii)*(dely-1) +
     &                     shfz(ind1+3,ii)*(1-dely) -     
     &                     shfz(ind1+(nxy2+2)+1,ii) +
     &                     shfz(ind1+(nxy2+2)+3,ii) -
     &                     shfz(ind1+2*(nxy2+2)+1,ii)*dely +
     &                     shfz(ind1+2*(nxy2+2)+3,ii)*dely)*0.25 
                    som2 = (shfz(ind1+1,ii)*(delx-1) -
     &                     shfz(ind1+2,ii) -
     &                     shfz(ind1+3,ii)*delx +
     &                     shfz(ind1+2*(nxy2+2)+1,ii)*(1-delx)+
     &                     shfz(ind1+2*(nxy2+2)+2,ii) +
     &                     shfz(ind1+2*(nxy2+2)+3,ii)*delx)*0.25
                  end if
                  xiz(1,ii) = xiz(1,ii) 
     &                       + 2*tamp2*(srcbis+src4bis+src7bis(indice))
                  xiz(2,ii) = xiz(2,ii) + 2.*tamp2
                  xid(1,ii) = xid(1,ii)-4.*b*tamp2*src2bis 
     &                       + 2.*som1*tamp2
                  xid(2,ii) = xid(2,ii)-4.*b*tamp2*src3bis 
     &                       + 2.*som2*tamp2
               end do
            end do
         else 
            do j=1,nxy1
               do i=1,nxy1
                  ind1 = nxy2*pas*(j-1)+pas*(i-1)
                  indice = (j-1)*nxy1+i
                  tamp2 = (sfbis(indice,ii)-g(indice,ii))*
     &                    sig2(indice,ii)
                  do l=1,pas
                     ind2 = (l-1)*nxy2
                     do k=1,pas
                        tmp5(ind1+k+ind2) = tamp2
                     end do
                  end do
               end do
            end do
         end if  

c        CALCULATION OF DERIVATIVES OF F
c        - - - - - - - - - - - - - - - - -

         call rlft2(tmp5,stmp5,nxy2,1)
        
         do i=1,n2
            tmp3(i) = trs(i,ii)
         end do
         do i=1,2*nxy2
            stmp3(i) = strs(i,ii)
         end do
 
         call produit(tmp3,tmp5,stmp3,stmp5,nxy2)
         call rlft2(tmp3,stmp3,nxy2,-1)
 
         t1 = z(1,ii)*2.
         do i=1,n2
            xif(i) =  xif(i) + t1*tmp3(i) 
         end do
      end do
c     ---------------------------------------------
c     FIN DE LA BOUCLE SUR LE NOMBRE D'IMAGES (II)
c     ---------------------------------------------

c     CALCULATION OF THE SMOOTHING TERM FOR THE DERIVATIVES OF F
c     - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

      do i=1,n2
         tmp2(i) = frf(i)
      end do

      call rlft2(tmp2,stmp2,nxy2,1)
      call produit(tmp2,rr,stmp2,srr,nxy2)
      call rlft2(tmp2,stmp2,nxy2,-1)

      do i=1,n2
         xif(i) = xif(i) + 2.*(frf(i)-tmp2(i))
      end do

      return
      end

c     --------------------------
c     SUBROUTINE: decompos
c     --------------------------
c     THIS ROUTINE IS USED FOR THE OUTPUT OF THE RESULTS.
c     ----------------------

      subroutine decompos(residu_fin)

      implicit none

      include 'param_dec.f'

      integer nb
      parameter(nb=nbr2+4*(xy2+1))

      real*4 p(nbr2),a(npic,nbg),c(2,npic)
      real*4 z(2,nbg),delta(2,nbg)
      real*4 g(nbr1,nbg),sig2(nbr1,nbg),sig3(nbr1,nbg)
      real*4 s(nbr2,nbg),ss(2*xy2,nbg),ssourdel(2*xy2)
      real*4 source(nbr2),fond(nbr2),sourdel(nbr2)
      real*4 sfond(2*xy2),fg(nbr1),sg(nbr2),gsm(nbr1)
      real*4 tmp(nbr2),tmp2(nbr2),tmp3(nbr2),stmp3(2*xy2),stmp2(2*xy2)
      real*4 w(4),w2(4),b,fp,qi
      real*4 inter(nb),inter2(nb),inter3(nb),resireduit(nbr2)
      real*4 resim(nbr2),resismm(nbr2),sfbis(nbr1,nbg)
      real*4 alpha,delx,dely,delx2,dely2,t1,t2,t3,t4,t5,t6,t7,t8
      integer n1,n2,np,m,nxy1,nxy2,pas,deb,deb2
      integer i,i2,ii,j,k,l,indice,indice2,ind1,ind2,ind3,i3
      integer residu_fin,m2,vari_int,ii2,nbch
      integer ndels,dels(npic)
      character*20 results
      character*1 lettre1,lettre3,lettre2,lettre4,question
      character*9 fin


      common /param/ nxy1,nxy2,pas
      common /parametre_alpha/ b,alpha
      common /gr1/ g,s,sig2,ss
      common/sig/ sig3
      common /variables/ p,z,a,c,delta
      common /tailles/ n1,n2,np,m,m2
      common /minimum/ fp,qi
      common /gr5/ sfbis
      common /variation_intensite/ vari_int
      common /source_delete/ dels,ndels
      common /digit/ nbch

      if (residu_fin .eq. 1) then
         do i=1,n2
            resim(i) = 0.
            resismm(i) = 0.
            resireduit(i) = 0.
         end do

c        demande de mise à zero des valeurs négatives
c        - - - - - - - - - - - - - - - - - - - - - - -
         question = 'n'
c         do while (question.ne.'y' .and. question .ne.'n')
c            write(*,'('' Mettre à 0 les valeurs négatives'',$)')
c            write(*,'('' du fond dans les images lissées (y/n) : '',$)')
c            read(5,*) question
c         end do
      end if

c     inter 3 = image de f avec un bord de 1 pixel supplémentaire
c     - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
      do j=1,nxy2
         inter3(j*(nxy2+2)+1) = p(j*nxy2)
         do i=1,nxy2
            indice = (j-1)*nxy2+i
            indice2 = j*(nxy2+2)+1+i
            inter3(indice2) = p(indice)
         end do
         inter3((j+1)*(nxy2+2)) = p((j-1)*nxy2+1)
      end do
      do i=1,nxy2+2
         inter3(i) = inter3((nxy2+2)*nxy2+i)
         inter3((nxy2+2)*(nxy2+1)+i) = inter3(nxy2+2+i)
      end do

c     Boucle sur le nombre d'images
c     - - - - - - - - - - - - - - - 
      do ii=1,m
         if (nbch .eq. 1 .and. m .lt. 10) then
            do i=1,m
               lettre1 = char(48+ii)
               fin = lettre1 // '.fits'
            end do
         else if (nbch .eq. 2 .and. m .lt. 100) then
            do i=1,m
               i2 = int(ii/10)
               lettre1 = char(48+i2)
               i2 = ii - i2*10
               lettre2 = char(48+i2)
               fin = lettre1 // lettre2 // '.fits'
            end do
         else if (nbch .eq. 3 .and. m .lt. 1000) then
            do i=1,m
               i2 = int(ii/100)
               lettre1 = char(48+i2)
               i2 = ii-i2*100
               i3 = int(i2/10)
               lettre2 = char(48+i3)
               i2 = i2-i3*10
               lettre3 = char(48+i2)
               fin = lettre1 // lettre2 // lettre3 // '.fits'
            end do
         else if (nbch .eq. 4 .and. m .lt. 10000) then
            do i=1,m
               i2 = int(ii/1000)
               lettre1 = char(48+i2)
               i2 = ii-i2*1000
               i3 = int(i2/100)
               lettre2 = char(48+i3)
               i2 = i2-i3*100
               i3 = int(i2/10)
               lettre3 = char(48+i3)
               i2 = i2-i3*10
               lettre4 = char(48+i2)
               fin = lettre1 // lettre2 // lettre3 // lettre4 // '.fits'
            end do
         end if

c        Calcul des variables delx dely deb (delx2 dely2 deb2 si residu_fin = 1)
c        - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
         if (delta(1,ii) .lt. 0.) then
            delx = 1+delta(1,ii)
            delx2 = -delta(1,ii)
         else
            delx = delta(1,ii)
            delx2 = 1-delta(1,ii)
         end if
         if (delta(2,ii) .lt. 0.) then
            dely = 1+delta(2,ii)
            dely2 = -delta(2,ii)
         else
            dely = delta(2,ii)
            dely2 = 1-delta(2,ii)
         end if

         if (delta(1,ii) .ge. 0. .and. delta(2,ii) .ge. 0.) then
            deb = nxy2+3
            deb2 = 0
         else if (delta(1,ii) .ge. 0. .and. delta(2,ii) .lt. 0.) then
            deb = 1
            deb2 = nxy2+2
         else if (delta(1,ii) .lt. 0. .and. delta(2,ii) .ge. 0.) then
            deb = nxy2+2
            deb2 = 1
         else
            deb = 0
            deb2 = nxy2+3
         end if 

         w(1) = (1-delx)*(1-dely)
         w(2) = delx*(1-dely)
         w(3) = dely*(1-delx)
         w(4) = delx*dely
         w2(1) = (1-delx2)*(1-dely2)
         w2(2) = delx2*(1-dely2)
         w2(3) = dely2*(1-delx2)
         w2(4) = delx2*dely2

         do j=1,nxy2
            do i=1,nxy2
               indice = (j-1)*nxy2+i
               ind1 = deb+(nxy2+2)*(j-1)+(i-1)
               source(indice) = 0.
               sourdel(indice) = 0.
c              -------
c              SOURCES
c              -------
               if (vari_int .eq. 1) then
                  t7 = 1.
                  ii2 = ii
               else
                  t7 = z(1,ii)
                  ii2 = 1
               end if
               do k=1,np
                  t1 = i-(c(1,k)-delta(1,ii))
                  t2 = j-(c(2,k)-delta(2,ii))
                  t8 = a(k,ii2)*t7*exp(-b*((t1**2)+(t2**2)))
                  source(indice) = source(indice) + t8
                  if (ndels.ne.0 .and. dels(k).eq.1) then
                     sourdel(indice) = sourdel(indice) + t8
                  end if
               end do
c              ----
c              FOND
c              ----
               fond(indice) = 0.
               do l=1,2
                  ind2 = (l-1)*(nxy2+2)
                  ind3 = 2*(l-1)
                  do k=1,2
                    fond(indice) = fond(indice) + 
     &                  w(ind3+k)*inter3(ind1+k+ind2) 
                  end do
               end do
               fond(indice) = z(1,ii)*fond(indice) + z(2,ii)
c              ------------
c              SOMME TOTALE
c              ------------
               tmp2(indice) = fond(indice) + source(indice)
c              ----------------
c              affectation de S
c              ----------------
               tmp3(indice) = s(indice,ii)
            end do
         end do
         do i=1,2*nxy2
            stmp3(i) = ss(i,ii)
         end do


c        IMAGES DE SORTIE:
c        dec---.fits = image déconvoluée
c        model---.fits = modèle analytique décalé.
c        back---.fitsn = fond multiplié par z1 additionné à z2 et décalé
c        - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
         results = 'dec' // fin 
         call makeima(results,nxy2,tmp2)
         results = 'back' // fin 
         call makeima(results,nxy2,fond)

c        Lissage de dec par s
c        - - - - - - - - - - - 
         call rlft2(tmp2,stmp2,nxy2,1)
         call produit(tmp2,tmp3,stmp2,stmp3,nxy2)
         call rlft2(tmp2,stmp2,nxy2,-1)

c        Lissage du fond par s
c        - - - - - - - - - - - 
         call rlft2(fond,sfond,nxy2,1)
         call produit(fond,tmp3,sfond,stmp3,nxy2)
         call rlft2(fond,sfond,nxy2,-1)

         if (residu_fin.eq.1 .and. question.eq.'y') then
            do i=1,n2
               if (fond(i) .lt. 0.) fond(i) = 0.
            end do
         end if

c        --------------------------------------------------------
c        ATTENTION: dans cette boucle tmp2 est utilisé pour dec*s 
c        et puis il est directement utilisé pour autre chose
c        --------------------------------------------------------
         if (ndels .eq. 0) then
            do j=1,nxy1
               do i=1,nxy1
                  ind1 = nxy2*pas*(j-1)+pas*(i-1)
                  indice = (j-1)*nxy1+i
                  t1 = (sfbis(indice,ii)-g(indice,ii))*
     &                    sqrt(sig3(indice,ii))
                  fg(indice) = 0.
                  gsm(indice) = 0.
                  do l=1,pas
                     ind2 = (l-1)*nxy2
                     do k=1,pas
                       gsm(indice) = gsm(indice) + tmp2(ind1+k+ind2) 
                       tmp(ind1+k+ind2) = t1
                       tmp2(ind1+k+ind2) = t1*t1
                       fg(indice) = fg(indice) + fond(ind1+k+ind2) 
                     end do
                  end do
                  fg(indice) = fg(indice)/real(pas*pas)
                  gsm(indice) = gsm(indice)/real(pas*pas)
               end do
            end do
         else
c           Lissage du sourdel par s
c           - - - - - - - - - - - - - 
            call rlft2(sourdel,ssourdel,nxy2,1)
            call produit(sourdel,tmp3,ssourdel,stmp3,nxy2)
            call rlft2(sourdel,ssourdel,nxy2,-1)
            do j=1,nxy1
               do i=1,nxy1
                  ind1 = nxy2*pas*(j-1)+pas*(i-1)
                  indice = (j-1)*nxy1+i
                  t1 = (sfbis(indice,ii)-g(indice,ii))*
     &                    sqrt(sig3(indice,ii))
                  fg(indice) = 0.
                  sg(indice) = 0.
                  gsm(indice) = 0.
                  do l=1,pas
                     ind2 = (l-1)*nxy2
                     do k=1,pas
                       gsm(indice) = gsm(indice) + tmp2(ind1+k+ind2) 
                       tmp(ind1+k+ind2) = t1
                       tmp2(ind1+k+ind2) = t1*t1
                       fg(indice) = fg(indice) + fond(ind1+k+ind2)
                       sg(indice) = sg(indice) + sourdel(ind1+k+ind2)
                     end do
                  end do
                  fg(indice) = fg(indice)/real(pas*pas)
                  sg(indice) = sg(indice)/real(pas*pas)
                  gsm(indice) = gsm(indice)/real(pas*pas)
               end do
            end do
c           IMAGE 
c           source_sm---.fits : (source à supprimer)*s
c           - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            results = 'source_sm' // fin
            call makeima(results,nxy1,sg)
         end if

c        IMAGE 
c        g_sm---.fits : (dec*s)
c        - - - - - - - - - - - - - - - - - - - - - - - - - - - -
         results = 'g_sm' // fin
         call makeima(results,nxy1,gsm)

c        IMAGE 
c        fondmodel_sm---.fits : (fond decalé z1 et z2 + model)*s
c        - - - - - - - - - - - - - - - - - - - - - - - - - - - -
         results = 'back_sm' // fin
         call makeima(results,nxy1,fg)

         call rlft2(tmp2,stmp2,nxy2,1)
         call produit(tmp2,tmp3,stmp2,stmp3,nxy2)
         call rlft2(tmp2,stmp2,nxy2,-1)

c        IMAGES DE SORTIE:
c        resi---.fits = image des résidus
c        resi_sm---.fits = image des résidus au carré, lissés
c        - - - - - - - - - - - - - - - - - - - - - - - - - - -
         results = 'resi' // fin
         call makeima(results,nxy2,tmp)
         results = 'resi_sm' // fin
         call makeima(results,nxy2,tmp2)


         if (residu_fin .eq. 1) then
            do j=1,nxy2
               inter(j*(nxy2+2)+1) = tmp(j*nxy2)
               inter2(j*(nxy2+2)+1) = tmp2(j*nxy2)
               do i=1,nxy2
                  indice = (j-1)*nxy2+i
                  indice2 = j*(nxy2+2)+1+i
                  inter(indice2) = tmp(indice)
                  inter2(indice2) = tmp2(indice)
               end do
               inter((j+1)*(nxy2+2)) = tmp((j-1)*nxy2+1)
               inter2((j+1)*(nxy2+2)) = tmp2((j-1)*nxy2+1)
            end do
            do i=1,nxy2+2
               inter(i) = inter((nxy2+2)*nxy2+i)
               inter2(i) = inter2((nxy2+2)*nxy2+i)
               inter((nxy2+2)*(nxy2+1)+i) = inter(nxy2+2+i)
               inter2((nxy2+2)*(nxy2+1)+i) = inter2(nxy2+2+i)
            end do

            do j=1,nxy2
               do i=1,nxy2
                  ind1 = deb2+(nxy2+2)*(j-1)+(i-1)
                  indice = (j-1)*nxy2+i
                  t1 = 0.
                  t2 = 0.
                  do l=1,2
                     ind2 = (l-1)*(nxy2+2)
                     ind3 = 2*(l-1)
                     do k=1,2
                       t1 = t1 + w2(ind3+k)*inter(ind1+k+ind2) 
                       t2 = t2 + w2(ind3+k)*inter2(ind1+k+ind2) 
                     end do
                  end do
                  resim(indice) = resim(indice) + t1
                  resismm(indice) = resismm(indice) + t2 
                  resireduit(indice) = resireduit(indice) + t1*t1
               end do
            end do
         end if
      end do

c     FIN DE LA BOUCLE SUR LE NOMBRE D'IMAGES
c     - - - - - - - - - - - - - - - - - - - - -

      if (residu_fin .eq. 1) then
         do i=1,n2
            resim(i) = resim(i)/real(m)
            resismm(i) = resismm(i)/real(m)
            resireduit(i) = resireduit(i)/real(m)
         end do
         results = 'resi_moyenne' // '.fits'
         call makeima(results,nxy2,resim)
         results = 'resi_sm_moyenne' // '.fits'
         call makeima(results,nxy2,resismm)
         results = 'resi_reduit' // '.fits'
         call makeima(results,nxy2,resireduit)
      end if

c     BACKUP OF RESULTS IN 2 OUTPUT FILES
c     - - - - - - - - - - - - - - - - - - 

      write(2,'(A12,E20.13)') 'Minimum   : ',fp
      write(2,'(A12,E20.13)') 'Chi carré : ',qi
      write(2,*)
      write(2,'(A34)') '* Intensité et coordonnées (x,y):'
      write(2,*)
      do k=1,np
         write(2,'(A25,I4)') '  - Numéro de la source: ',k 
         do i=1,m2
            write(2,'(A10,3(F16.6,A1))') '          ',a(k,i),
     &                ' ',
     &               c(1,k)-delta(1,i),' ',
     &               c(2,k)-delta(2,i),' '
            write(3,'(F16.6,A1,$)') a(k,i),' '
        end do
        write(3,*)  
        write(3,'(2F12.6)') c(1,k),c(2,k)
        write(2,*)
      end do
      write(3,'(A55)') '------------------------------------------------
     &-------'
      write(3,'(A55)') '|Valeurs intiales de z1, z2, delta1 et delta2    
     &      |'
      write(3,'(A55)') '|nb * (4 valeurs) où nb = nombre d''images       
     &      |'
      write(3,'(A55)') '------------------------------------------------
     &-------'
      write(2,'(A47)') '* Valeurs finales de z1, z2, delta1 et delta2 :'
      do i=1,m
         write(2,'(A10,4(F12.6,A1))') '          ',z(1,i),' ',
     &   z(2,i),' ',delta(1,i),' ',delta(2,i),' '
         write(3,'(4F12.6)') z(1,i),z(2,i),delta(1,i),
     &                       delta(2,i)
      end do
      write(2,*) 

      write(3,'(A55)') '------------------------------------------------
     &-------'
      write(3,'(A55)') '|Modèle analytique: valeurs de Io A B C Cx et Cy
     &      |'
      write(3,'(A55)') '|    (6 valeurs : Io A B C Cx Cy)                  
     &      |'
      write(3,'(A55)') '------------------------------------------------
     &-------'

      write(2,'(A46)') '* Modèle analytique: valeurs de Io A B C Cx Cy'
      write(3,'(E20.13,A1,$)') 0.,' '
      write(2,'(E20.13,A1,$)') 0.,' '
      do i=1,5
         write(3,'(F13.6,A1,$)') 0.,' '
         write(2,'(F13.6,A1,$)') 0.,' '
      end do
      write(3,*) 
      write(2,*) 
      write(2,*) 

      return
      end

C     ============================================================
C     ============================================================
c         A     U       U TTTTTTTTT RRRRRRRR  EEEEEEEEE SSSSSSSSS 
c        A A    U       U     T     R       R E         S
c       A   A   U       U     T     RRRRRRRR  EEEEE     SSSSSSSSS
c      AAAAAAA  U       U     T     R     R   E                 S
c     A       A  UUUUUUU      t     R      R  EEEEEEEEE SSSSSSSSS
C     =============================================================
C     =============================================================

c     ----------------------------
c     SUBROUTINE: nouvelle fourier
c     ----------------------------

      subroutine rlft2(data,speq,nn1,isign)
 
      integer isign,nn1
      reaL*4 data(nn1*nn1)
      integer i1,i2,j1,j2,nn(2),i,ind1,ind2,nb
      double precision theta,wi,wpi,wpr,wr,wtemp
      real*4 c1,c2,h1r,h1i,h2r,h2i
      real*4 speq(nn1*2)

      c1 = 0.5
      c2 = -0.5*isign
      theta = 6.28318530717959d0/dble(isign*nn1)
      wpr = -2.0d0*sin(0.5d0*theta)**2
      wpi = sin(theta)
      nn(1) = nn1/2
      nn(2) = nn1
      nb = nn(1)*nn(2)
      if (isign .eq. 1) then
         call fourn(data,nn,nb,2,isign)
        do i=1,nn1
            speq(i*2-1) = data((i-1)*nn1+1)
            speq(i*2) = data((i-1)*nn1+2)
        end do
      end if
      wr = 1.0d0
      wi = 0.0d0
      do i2=1,nn1/2+1,2
         j2 = nn1-i2+2
         do i1=1,nn1
            j1 = 1
            if (i1 .ne. 1) j1 = nn1-i1+2
            if (i2 .eq. 1) then
               h1r = c1*(data((i1-1)*nn1+1)+speq(j1*2-1))
               h1i = c1*(data((i1-1)*nn1+2)-speq(j1*2))
               h2i = c2*(data((i1-1)*nn1+1)-speq(j1*2-1))
               h2r = -c2*(data((i1-1)*nn1+2)+speq(j1*2))
               data((i1-1)*nn1+1) = h1r+h2r
               data((i1-1)*nn1+2) = h1i+h2i
               speq(j1*2-1) = h1r-h2r
               speq(j1*2) = -h1i+h2i
            else
               ind1 = (i1-1)*nn1+i2
               ind2 = (j1-1)*nn1+j2
               h1r = c1*(data(ind1)+data(ind2))
               h1i = c1*(data(ind1+1)-data(ind2+1))
               h2i = c2*(data(ind1)-data(ind2))
               h2r = -c2*(data(ind1+1)+data(ind2+1))
               data(ind1) = h1r+wr*h2r-wi*h2i
               data(ind1+1) = h1i+wr*h2i+wi*h2r
               data(ind2) = h1r-wr*h2r+wi*h2i
               data(ind2+1) = -h1i+wr*h2i+wi*h2r
           end if
         end do
         wtemp = wr
         wr = wr*wpr-wi*wpi+wr
         wi = wi*wpr+wtemp*wpi+wi
      end do
      if (isign .eq. -1) then
         call fourn(data,nn,nb,2,isign)
      end if

      return
      end 

c     ---------------------
c     SUBROUTINE: fourier
c     ---------------------
c     ROUTINE WHICH CALCULATES THE FOURIER TRANSFORM OR INVERSE FOURIER
c     TRANSFORM
c     ---------------------

      subroutine fourn(data,nn,nb,ndim,isign)

c      real*8 wr,wi,wpr,wpi,wtemp,theta
c      real*4 data(nb*2)
c      integer nn(ndim)
      integer nn(ndim),isign,ndim,nb
      double precision wr,wi,wpr,wpi,wtemp,theta
      real*4 data(nb*2),tempi,tempr
      integer i1,i2,i2rev,i3,i3rev,ibit,idim,ifp1,ifp2,ip1,ip2,ip3
      integer k1,k2,n,nprev,nrem,ntot


      ntot = 1
      do idim=1,ndim
         ntot = ntot*nn(idim)
      end do    
      nprev = 1
      do idim=1,ndim
         n = nn(idim)
         nrem = ntot/(n*nprev)
         ip1 = 2*nprev
         ip2 = ip1*n
         ip3 = ip2*nrem
         i2rev = 1
         do i2=1,ip2,ip1
            if (i2 .lt. i2rev) then
               do i1=i2,i2+ip1-2,2
                  do i3=i1,ip3,ip2
                     i3rev = i2rev+i3-i2
                     tempr = data(i3)
                     tempi = data(i3+1)
                     data(i3) = data(i3rev)
                     data(i3+1) = data(i3rev+1)
                     data(i3rev) = tempr
                     data(i3rev+1) = tempi
                 end do
               end do
            end if
            ibit = ip2/2
30          if ((ibit .ge. ip1) .and. (i2rev .gt. ibit)) then
               i2rev = i2rev-ibit
               ibit = ibit/2
               go to 30
            end if
            i2rev = i2rev+ibit 
        end do
        ifp1 = ip1
31      if (ifp1 .lt. ip2) then
           ifp2 = 2*ifp1
           theta = isign*6.28318530717959D0/(ifp2/ip1)
           wpr = -2.D0*sin(0.5D0*theta)**2
           wpi = sin(theta)
           wr = 1.D0
           wi = 0.D0
           do i3=1,ifp1,ip1
              do i1=i3,i3+ip1-2,2
                do i2=i1,ip3,ifp2
                   k1 = i2
                   k2 = k1+ifp1
                   tempr = sngl(wr)*data(k2)-sngl(wi)*data(k2+1)
                   tempi = sngl(wr)*data(k2+1)+sngl(wi)*data(k2)
                   data(k2) = data(k1)-tempr
                   data(k2+1) = data(k1+1)-tempi
                   data(k1) = data(k1)+tempr
                   data(k1+1) = data(k1+1)+tempi
                end do
              end do
              wtemp = wr
              wr = wr*wpr-wi*wpi+wr
              wi = wi*wpr+wtemp*wpi+wi
           end do
           ifp1 = ifp2
           go to 31
        end if
        nprev = n*nprev
      end do
      
      return
      end

c     ---------------------
c     SUBROUTINE: produit
c     ---------------------
c     ROUTINE WHICH COMPUTES THE PRODUCT OF 2 COMPLEX TABLES
c     ---------------------

      subroutine produit(f1,f2,s1,s2,n)

      integer n,j
      real*4 f1(n*n),f2(n*n),s1(2*n),s2(2*n),sc,r,i
  

      sc = 2./(n*n)
      do j=1,n*n,2
         r = f1(j)*f2(j) - f1(j+1)*f2(j+1)
         i = f1(j)*f2(j+1) + f1(j+1)*f2(j)
         f1(j) = r*sc
         f1(j+1) = i*sc
      end do
      do j=1,2*n,2
         r = s1(j)*s2(j) - s1(j+1)*s2(j+1)
         i = s1(j)*s2(j+1) + s1(j+1)*s2(j)
         s1(j) = r*sc
         s1(j+1) = i*sc
      end do

      return
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
