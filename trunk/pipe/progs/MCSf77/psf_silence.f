c     PROGRAMME DE MINIMISATION
c     -------------------------

c     DECLARATION DES VARIABLES
c     -------------------------

      implicit none

      include 'param2.f'

      integer i,j,iter,n1,j2,ind2,ind,i2,pas,k,r1,Rmin,Rmax,ni
      integer nax1,nax2,nxy1,ns,centre,n2,nxy2,l,itergauss
      integer rayon,xy_carre,nb_carre,deb,fin,ray,its_final     
      integer marche,nb_iter,nb_iter_mini,jj,modu,nbitermax_mof
      integer qicible

      real*4 a(nbi,nbs),c(nbs,2),bb,br,f(nbr2,nbi),constf
      real*4 delta(nbi,2),ddelta(nbi,2),somme
      real*4 b(nbi,3),beta(nbi),fret,fond,lambda(nbi),fwhm2,cc
      real*4 g(nbr1,nbi),sig2(nbr1,nbi),fwhm,phi,nddelta(2)
      real*4 da(nbi,nbs),dc(nbs,2),db(nbi,3),dbeta(nbi),df(nbr2,nbi)
      real*4 nda(nbi,nbs),ndc,ndb(3),ndbeta,k1,ndf,fwhmgauss,fwhmgaussf
      real*4 tmp(nbr2),rr(nbr2),srr(2*xy2),t1,t2,cent,som,half
      real*4 moffatfixe(nbr2,nbi),plan(nbi,3),dplan(nbi,3),ndplan,fwhm3
      real*4 filtre(nbr2),tmp3(nbr1),qimin,fpA,qiA,resi_min,stepgauss

      character*80 name
      character*70 entete
      character*42 ligne
      character*20 results,name_moffat(nbi)
      character*1 question,minimum_moffat,lettre,lettre2,lettre3
      character*1 recompose
      character*8 mot
 
      logical execute

      common /gr1/ g,sig2
      common /var_fond/ f
      common /var_moffat/ b,beta
      common /var_source/ a,bb,c,delta
      common /var_plan/ plan
      common /tailles/ n1,n2,ns,nxy1,nxy2,pas,ni
      common /delta_fond/ df
      common /delta_moffat/ db,dbeta
      common /delta_source/ da,dc,ddelta
      common /delta_plan/ dplan
      common /deltacons_fond/ ndf
      common /deltacons_moffat/ ndb,ndbeta
      common /deltacons_source/ nda,ndc,nddelta
      common /deltacons_plan/ ndplan
      common /lissage/ rr,srr
      common /lissage3/ lambda
      common /moffat_fixe/ moffatfixe
      common /carre/ rayon,xy_carre,nb_carre,deb,fin
      common /fichier_sortie/ minimum_moffat,name_moffat
      common /minimum2/ fpA,qiA
      common /gauss_lissage/ stepgauss,fwhmgauss,resi_min,itergauss
      common /image_recomposee/ recompose
      common /qi_cible/ qicible

c     DEBUT DE PROGRAMME
c     ------------------

      n1=nbr1
      nxy1=xy1
      n2=nbr2
      nxy2=xy2
      pas = nxy2/nxy1
c      write(*,*) n1,n2,ns,nxy1,nxy2,pas
      if (n1 .eq. n2) then
         write(*,*) 'On reste en gros pixels'
      else if (n1*pas*pas .eq. n2) then
c         write(*,*) 'On passe en petits pixels'
      else
         write(*,*) ' n1 pas egal à n2 ou n1*pas*pas pas egal à n2'
         stop
      end if

c     LECTURE DU FICHIER 'psfmofsour8.txt'
c     - - - - - - - - - - - - - - - - - -
      open(unit=1,file='psfmofsour8.txt')
      do i=1,4
         read(1,'(A70)') entete
      end do 
      read(1,'(A42,I4)') ligne,ni
      if (ni .gt. nbi) then
         write(*,*) 'Nbr images supérieur à la valeur de param2.f'
         stop
      end if
      read(1,'(A70)') entete
      read(1,'(A42,I4)') ligne,ns
      if (ns .gt. nbs) then
         write(*,*) 'Nbr sources supérieur à la valeur de param2.f'
         stop
      end if
      read(1,'(A70)') entete
      read(1,'(A42,A1)') ligne,recompose
      read(1,'(A70)') entete
      read(1,'(A42,F16.10)') ligne,fwhm
      if (fwhm .ge. 2.) then
         bb = 4*log(2.)/(fwhm*fwhm)
      else
         write(*,*) 'FWHM < 2 --> erreur échantillonnage'
         stop
      end if
      read(1,'(A70)') entete
      read(1,'(A42,F16.10)') ligne,fwhm2
      read(1,'(A70)') entete
      read(1,'(A70)') entete
      read(1,'(A42,F16.10)') ligne,fwhm3
      if (fwhm3 .ge. 2.) then
         br = 4*log(2.)/(fwhm3*fwhm3)
      else
         write(*,*) 'FWHM < 2 --> erreur échantillonnage'
         stop
      end if
      read(1,'(A70)') entete
      read(1,'(A42,I4)') ligne,modu
      read(1,'(A70)') entete
      read(1,'(A42,I4)') ligne,nbitermax_mof
      read(1,'(A70)') entete
      read(1,'(A42,I4)') ligne,nb_iter_mini
      read(1,'(A70)') entete
      read(1,'(A42,F16.10)') ligne,qimin
      do i=1,3
         read(1,'(A70)') entete
      end do 
      read(1,'(A42,I4)') ligne,ray
      read(1,'(A42,I4)') ligne,marche
      read(1,'(A42,I4)') ligne,Rmin
      read(1,'(A42,I4)') ligne,Rmax
      if ((ray*2+1) .gt. nxy2) then
          write(*,*) 'rayon trop grand'
          stop
      end if
      do i=1,3
         read(1,'(A70)') entete
      end do 
      read(1,'(A42,F16.10)') ligne,ndb(1)
      read(1,'(A42,F16.10)') ligne,ndb(2)
      read(1,'(A42,F16.10)') ligne,ndb(3)
      read(1,'(A42,F16.10)') ligne,ndbeta
      read(1,'(A70)') entete
      read(1,'(A42,F16.10)') ligne,ndplan
      read(1,'(A70)') entete
      read(1,'(A42,F16.10)') ligne,nddelta(1)
      read(1,'(A42,F16.10)') ligne,nddelta(2)
      read(1,'(A70)') entete
      read(1,'(A42,F16.10)') ligne,k1
      read(1,'(A42,F16.10)') ligne,ndc
      do i=1,3
         read(1,'(A70)') entete
      end do 
      read(1,'(A42,F16.10)') ligne,ndf
      read(1,'(A42,F16.10)') ligne,constf

      read(1,'(A70)') entete
      read(1,'(A42,F16.10)') ligne,fwhmgauss
      read(1,'(A70)') entete
      read(1,'(A42,F16.10)') ligne,fwhmgaussf
 
      read(1,'(A70)') entete
      read(1,'(A42,I4)') ligne,itergauss

      stepgauss = (fwhmgaussf-fwhmgauss)/itergauss

      read(1,'(A70)') entete
      read(1,'(A42,F16.10)') ligne,resi_min
      do i=1,5
         read(1,'(A70)') entete
      end do 
      read(1,*) (lambda(i),i=1,ni)
      do i=1,3
         read(1,'(A70)') entete
         do j=1,ni
            dplan(j,i) = ndplan
            db(j,i) = ndb(i)
         end do
      end do 
      read(1,*) fond
      do i=1,5
         read(1,'(A70)') entete
      end do 
      read(1,*) minimum_moffat
      if (minimum_moffat .eq. 'i') then
         do j=1,ni
            read(1,'(A20)') name_moffat(j)
         end do
      else if (minimum_moffat .eq. 'n') then
         do j=1,ni
            read(1,*) b(j,1),b(j,2),b(j,3),beta(j)
         end do  
      else if (minimum_moffat .eq. 'y') then
         do j=1,ni
            read(1,*) b(j,1),b(j,2),b(j,3),beta(j)
c            write(*,*) b(j,1),b(j,2),b(j,3),beta(j)
            if (b(j,1).eq.0. .and. b(j,2).eq.0. .and. b(j,3).eq.0.) then 
               beta(j) = 3.
               b(j,1) = 1./(((fwhm2*pas)**2)-(fwhm*fwhm))
               b(j,2) = b(j,1)
               b(j,3) = 0.
            end if    
         end do
      else 
         write(*,*) 'paramètre erroné : on accepte un n, y ou i'
         stop
      end if
      do i=1,3
         read(1,'(A70)') entete
      end do 
      do l=1,ni
         read(1,*) plan(l,1),plan(l,2),plan(l,3)
         dbeta(l) = ndbeta
      end do
      do i=1,4
         read(1,'(A70)') entete
      end do 
      do j=1,ni
         read(1,*) delta(j,1),delta(j,2)
         ddelta(j,1) = nddelta(1)
         ddelta(j,2) = nddelta(2)
      end do
      do i=1,5
         read(1,'(A70)') entete
      end do 
      do i=1,ns
         read(1,*) (a(j,i),j=1,ni)
         read(1,*) c(i,1),c(i,2)
         c(i,1) = c(i,1)*pas-((real(pas)-1)/real(pas))
         c(i,2) = c(i,2)*pas-((real(pas)-1)/real(pas))
         do j=1,ni
            nda(j,i) = (a(j,i)*k1)/100.
            da(j,i) = nda(j,i)
         end do
         dc(i,1) = ndc
         dc(i,2) = ndc
      end do 
      close(unit=1)

      open(unit=1,file='psfmofsour8.txt')
      open(unit=2,file='psfmofsour8.out')
      do i=1,72
         read(1,'(A70)') entete
         write(2,'(A70)') entete
      end do
      close(unit=1)

c     R DU TERME DE LISSAGE & INITIALISATION DU FOND
c     ----------------------------------------------
      som = 0.
      cent = (nxy2/2+1)
      do j=1,nxy2
         t2 = j-cent
         ind = (j-1)*nxy2
         do i=1,nxy2
            t1 = i-cent
            ind = ind+1
            tmp(ind) = exp(-br*(t1*t1+t2*t2))
            som = som + tmp(ind)
         end do
      end do
      half = int(nxy2/2)
c      write(*,*) 'normalisation de r: ',som
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
      call rlft2(rr,srr,nxy2,nxy2,1)

c      write(*,*) nbr1,nbr2,n1,n2,xy1,xy2,nxy1,nxy2,nbi,ni
c      write(*,*) plan(1,1),plan(1,2),plan(1,3)
c      write(*,*) dplan(1,1),dplan(1,2),dplan(1,3)
c      write(*,*) b(1,1),b(1,2),b(1,3),beta(1)
c      write(*,*) db(1,1),db(1,2),db(1,3),dbeta(1)
c      write(*,*) ns
c      write(*,*) bb
      do i=1,ns
c         write(*,*) a(1,i),c(i,1),c(i,2)
c         write(*,*) da(1,i),dc(i,1),dc(i,2)
      end do
c      write(*,*) delta(1,1),delta(1,2)
c      write(*,*) ddelta(1,1),ddelta(1,2)


c EN ATTENDANT SI UNE AUTRE BOUCLE A CHANGE
c ==========================================

      do j=1,ni
         do i=1,n2
            f(i,j) = fond
         end do
      end do

      qicible = 0
      do j=1,ni
         lettre = char(48+int(j/100))
         jj = j - int(j/100)
         lettre2 = char(48+int(jj/10))
         lettre3 = char(48+mod(jj,10))
         mot = lettre // lettre2 // lettre3 // '.fits'
         name = 'g' // mot
         call openima(name,nax1,nax2,tmp3)
         do i=1,nbr1
            g(i,j) = tmp3(i)
         end do
         name = 'sig' // mot
         call openima(name,nax1,nax2,tmp3)
         do i=1,n1
            sig2(i,j) = (tmp3(i)*tmp3(i))
            if (tmp3(i) .gt. 1.E-10) qicible = qicible + 1
         end do
      end do

c      write(*,*) 'qicible = ',qicible

      open(unit=4,file='valeur_minimi.txt')


      if (minimum_moffat .eq. 'y') then

c        MINIMISATION DE LA MOFFAT+SOURCES+PLAN
c        - - - - - - - - - - - - - - - - - - - -
          call minimi_moffat(nbitermax_mof,modu,qimin,its_final)
c         call gradient_moffat(1.E-08,iter,fret)
          call decomposition_moffat(1)
          do i=1,3*ni+2*ns+13
             backspace(unit=2)
          end do


          do i=1,ns
             do j=1,ni
                da(j,i) = ((a(j,i)*k1)/100.)/10.
             end do
             dc(i,1) = ndc/10.
             dc(i,2) = ndc/10.
          end do
          do j=1,ni
             ddelta(j,1) = nddelta(1)/10.
             ddelta(j,2) = nddelta(2)/10.
             do i=1,3
                dplan(j,i) = ndplan/10.
             end do
          end do
          write(4,*) '------------------------------------'
          write(4,*) '          MINIMI MOFFAT             '
          write(4,*) '------------------------------------'
          write(4,*) 'Nombre itérations:   ',its_final-1
          write(4,*) 'Valeur du minimum:   ',fpA
          write(4,*) 'Valeur du khi carré: ',qiA
          write(4,*)

      end if

      if (minimum_moffat .eq. 'y' .or. minimum_moffat .eq. 'n') then
c        CALCUL DES MOFFAT
c        - - - - - - - - - 
         centre = nxy2/2+1
         do k=1,ni
            somme = 0.
            do j=1,nxy2
               t2 = j-centre  
               do i=1,nxy2 
                  t1 = i-centre
                  ind = i + (j-1)*nxy2
                  phi = 1. + b(k,1)*t1*t1 + b(k,2)*t2*t2 + b(k,3)*t1*t2
                  moffatfixe(ind,k) = phi**(-beta(k))
                  df(ind,k) = ndf + constf
                  somme =  somme + moffatfixe(ind,k)
                end do
            end do
            do i=1,n2
              moffatfixe(i,k) = moffatfixe(i,k)/somme
            end do
         end do
      else
         do k=1,ni
            call openima(name_moffat(k),nax1,nax2,tmp)
            if (nax1.ne.nax2 .or. nax1.ne.nxy2) then
               write(*,*) 'ATTENTION: image moffat ',k,
     &                    ' pas de bonne taille'
               stop
            end if
            do i=1,n2
               df(i,k) = ndf + constf
               moffatfixe(i,k) = tmp(i)
            end do
         end do
      end if



c     MINIMISATION DU FOND+SOURCES+PLAN (MOFFAT FIXE)
c     - - - - - - - - - - - - - - - - - - - - - - - -

      if (Rmax .le. nxy2/2) then
         nb_iter = int((Rmax-ray)/marche)+1
      else
         nb_iter = int((nxy2/2-1-ray)/marche)+1
      end if
c      write(*,*) 'Nombre de relances de minimi ',ray,marche,nb_iter
      do i=1,nb_iter
         rayon = ray + (i-1)*marche
         xy_carre = rayon*2+1
         nb_carre = xy_carre*xy_carre
         deb = nxy2/2+1-rayon
         fin = nxy2/2+1+rayon

         call minimi_fond(nb_iter_mini,modu,qimin,its_final)
         if (i .ne. nb_iter) then
            do j=1,n2
               do l=1,ni
                 df(j,l) = ndf + constf
               end do 
               filtre(j) = 0.
            end do 
 
c            write(*,*) rayon,Rmin
            cc = rayon+1
            if (rayon .le. Rmin) then
               do j=1,xy_carre
                  t2 =  ((j-cc)/rayon)**2
                  do k=1,xy_carre
                     t1 = ((k-cc)/rayon)**2
                     ind= (j+deb-2)*nxy2+(k+deb-1)
                     filtre(ind) = (1.-t1)*(1.-t2)
                     do l=1,ni
                        f(ind,l) = f(ind,l)*filtre(ind)
                     end do
                  end do
               end do
            else
               r1 = rayon-Rmin
               do j=1,xy_carre
                  if ((Rmin.lt.j).and.(j.le.(xy_carre-Rmin))) then
                     t2 = 0.
                  else if (j .le. Rmin) then
                     t2 = ((Rmin-j)/float(Rmin))**2
                  else
                     t2 =  ((j-cc-r1)/Rmin)**2
                  end if
                  do k=1,xy_carre
                     if ((Rmin.lt.k).and.(k.le.(xy_carre-Rmin))) then
                        t1 = 0.
                     else if (k .le. Rmin) then
                        t1 = ((Rmin-k)/float(Rmin))**2
                     else
                        t1 = ((k-cc-r1)/Rmin)**2
                     end if
                     ind= (j+deb-2)*nxy2+(k+deb-1)
                     filtre(ind) = (1.-t1)*(1.-t2)
                     do l=1,ni
                        f(ind,l) = f(ind,l)*filtre(ind)
                     end do
                  end do
               end do
            end if

            results = "filtre.fits"
            call makeima(results,nxy2,filtre)
c            read(*,*) question
         end if
      end do
      call decomposition_fond(1)
      close(unit=2)

      write(4,*) '------------------------------------'
      write(4,*) '          MINIMI FOND   (cycle 2)   '
      write(4,*) '------------------------------------'
      write(4,*) 'Nombre itérations:   ',its_final-1
      write(4,*) 'Valeur du minimum:   ',fpA
      write(4,*) 'Valeur du khi carré: ',qiA
      close(unit=4)



c     AFFICHAGE DES RESULTATS A L'ECRAN
c     - - - - - - - - - - - - - - - - -
c      write(*,*) 
c      write(*,*) 
c      write(*,*) '==================================='
c      write(*,*) '             RESULTATS'
c      write(*,*) '==================================='
c      write(*,*) 'PLAN:'
c      write(*,*) '-----'
      do j=1,ni
c         write(*,*) j,' alpha beta gamma: ',
c     &              plan(j,1),plan(j,2),plan(j,3)
      end do
c      write(*,*) 
c      write(*,*) 'MOFFAT:'
c      write(*,*) '-------'
      do j=1,ni
c        write(*,*) j,' b1 b2,b3,beta:   ',b(j,1),b(j,2),b(j,3),beta(j)
      end do
c      write(*,*) 
c      write(*,*) 'SOURCES:'
c      write(*,*) '--------'
      do i=1,ns
c         write(*,*) 'source ',i,' a c1 c2 : ',
c     &              (a(j,i),j=1,ni),
c     &              c(i,1)+((real(pas)-1)/real(pas)),
c     &              c(i,2)+((real(pas)-1)/real(pas))
      end do
c      write(*,*) 'DECALAGES:'
 1    write(*,*) '-----------'
      do i=1,ni
c         write(*,*) 'décalage ',i,' :   ',delta(i,1),delta(i,2)
      end do
c      write(*,*) 
c      write(*,*) '==================================='
c      write(*,*) 
c      write(*,*) 


c     BOUCLE SUR LE MASQUE A EVENTUELLEMENT APPLIQUER
c     - - - - - - - - - - - - - - - - - - - - - - - -
c      question = 'a'
c      do while (question .ne. 'y' .and. question .ne. 'n')
c         write(*,*) 
c         write(*,*) '============================================='
c         write(*,*)
c         write(*,'(''Voulez-vous utiliser un MASQUE (y/n): '',$)')
c         read(*,'(A1)') question
c      end do
c      execute = .true.
c      do while (execute .eqv. .true.)
c          if (question .eq. 'y') then
c            write(*,*)
c            call mask()
c            question = 'a'
c            do while (question .ne. 'y' .and. question .ne. 'n')
c             write(*,*) 
c             write(*,*) '============================================='
c             write(*,*)
c             write(*,'(''Voulez-vous utiliser un AUTRE masque (y/n): '',
c     &               $)')
c             read(*,'(A1)') question
c            end do
c         else
c            execute = .false.
c            write(*,*)
c         end if
c      end do



      end 

c     ===========================================================
c     ===========================================================
c          MM   MM   OOOOO  FFFFFFF FFFFFFf  AAAAA  TTTTTTT
c          M MMM M  O     O F       F       A     A    T
c          M  M  M  O     O FFFF    FFFF    AAAAAAA    T
c          M     M  O     O F       F       A     A    T
c          M     M   OOOOO  F       F       A     A    T
c     ============================================================
C      MOFFAT + SOURCES  + DECALLAGES + PLAN
c     ============================================================

c     ==============================================
c     SUBROUTINE: minimi pour le calcul de la moffat
c     ==============================================

      subroutine minimi_moffat(itmax,modu,qimin,its)

      implicit none
 
      include 'param2.f'

      real*4 eps
      parameter (eps=1.E-10)

      real*4 xia(nbi,nbs),xic(nbs,2),xib(nbi,3),xibeta(nbi)
      real*4 xiplan(nbi,3),xidelta(nbi,2)
      real*4 xiaA(nbi,nbs),xicA(nbs,2),xibA(nbi,3),xibetaA(nbi)
      real*4 xiplanA(nbi,3),xideltaA(nbi,2)
      real*4 a(nbi,nbs),bb,c(nbs,2),b(nbi,3),beta(nbi)
      real*4 plan(nbi,3),delta(nbi,2)
      real*4 aN(nbi,nbs),cN(nbs,2),bN(nbi,3),betaN(nbi)
      real*4 planN(nbi,3),deltaN(nbi,2)
      real*4 da(nbi,nbs),dc(nbs,2),db(nbi,3),dbeta(nbi)
      real*4 dplan(nbi,3),ddelta(nbi,2)
      real*4 daN(nbi,nbs),dcN(nbs,2),dbN(nbi,3),dbetaN(nbi)
      real*4 dplanN(nbi,3),ddeltaN(nbi,2)
      real*4 nda(nbi,nbs),ndc,ndb(3),ndbeta
      real*4 ndplan,nddelta(2)
      real*4 vecteurqi(10),qimin,lis
      real*4 fp,fp2,qi,fpA,qiA
c     -------------
c     NORMALISATION
      real*4 somme(nbi),sommeA(nbi)
c     -------------
      integer i,k,l,ind,ind2,arret,arret2,kk,jj
      integer its,itmax,iter
      integer n1,n2,ns,ni,nxy1,nxy2,modu,pas

c     -------------
c     NORMALISATION
      common /normalisation/ somme,sommeA
c     -------------
      common /var_source/ a,bb,c,delta
      common /var_moffat/ b,beta
      common /var_plan/ plan
      common /delta_source/ da,dc,ddelta
      common /delta_moffat/ db,dbeta
      common /delta_plan/ dplan
      common /deltacons_source/ nda,ndc,nddelta
      common /deltacons_moffat/ ndb,ndbeta
      common /deltacons_plan/ ndplan
      common /tailles/ n1,n2,ns,nxy1,nxy2,pas,ni
      common /derivees_moffat/ xia,xic,xib,xibeta,xiplan,xidelta
      common /minimum/ fp,qi,lis
      common /minimum2/ fpA,qiA

      arret = 0    

c     CALCUL DU MINIMUM ET DES DERIVEES :
c     - - - - - - - - - - - - - - - - - - - -
      call inifunc_moffat(a,bb,c,delta,b,beta,plan,1)
      call dfunc_moffat(a,bb,c,delta,b,beta,plan)

      vecteurqi(1) = qi
      do i=2,10
         vecteurqi(i) = 0.
      end do
      do l=1,ni
         do i=1,3
            dbN(l,i) = db(l,i)
            dplanN(l,i) = dplan(l,i)
         end do
         do i=1,2
            ddeltaN(l,i) = ddelta(l,i)
         end do
         dbetaN(l) = dbeta(l)
      end do
      do i=1,ns
         do l=1,ni
            daN(l,i) = da(l,i)
         end do
         dcN(i,1) = dc(i,1)
         dcN(i,2) = dc(i,2)
      end do 


      do its=1,itmax

c         write(*,*) its,' M  (moffat)   min khi: ',fp,qi
c         write(*,*) 'Moffat iteration ',its,', min khi : ',fp,qi
c         write(*,*)
         iter = its

c        MODIFICATION MOFFAT ET PLAN
c        - - - - - - - - - - - - - - 
         do l=1,ni
c            write(*,'(''b1 b2 b3 beta :'',$)')
            do k=1,3
               if (xib(l,k) .lt. 0.) then
                  bN(l,k) = b(l,k) + dbN(l,k)
               else
                  bN(l,k) = b(l,k) - dbN(l,k)
               end if
c               write(*,'(E12.6,A1,$)') bN(l,k),' '
               if (xiplan(l,k) .lt. 0.) then
                  planN(l,k) = plan(l,k) + dplanN(l,k)
               else
                  planN(l,k) = plan(l,k) - dplanN(l,k)
               end if
            end do
            if (xibeta(l) .lt. 0.) then
               betaN(l) = beta(l) + dbetaN(l)
            else
               betaN(l) = beta(l) - dbetaN(l)
            end if
c            write(*,'(E12.6)') betaN(l)
c            write(*,*) 'plan :         ',planN(l,1),planN(l,2),
c     &                  planN(l,3)
         end do


c        MODIFICATION SOURCES
c        - - - - - - - - - - -
         do k=1,ns
c            write(*,'(''a ... a c1 c2   :'',$)')
            do l=1,ni
               if (xia(l,k) .lt. 0.) then
                  aN(l,k) = a(l,k) + daN(l,k)
               else
                  aN(l,k) = a(l,k) - daN(l,k)
               end if
c               write(*,'(E12.6,A1,$)') aN(l,k),' '
            end do
            do i=1,2
               if(xic(k,i) .lt. 0.) then
                  cN(k,i) = c(k,i) + dcN(k,i)
               else
                  cN(k,i) = c(k,i) - dcN(k,i)
               end if
            end do
c            write(*,'(2(E12.6,A1))') cN(k,1)+((real(pas)-1)/real(pas)),
c     &            ' ',cN(k,2)+((real(pas)-1)/real(pas)),' '

         end do

c        MODIFICATION DECALAGES
c        - - - - - - - - - - - - 
         deltaN(1,1) = delta(1,1)
         deltaN(1,2) = delta(1,2) 
c         write(*,'(''delta x   delta y   :'',$)')
c         write(*,'(2(E12.6,A1))') delta(1,1),' ',delta(1,2),' '
         do l=2,ni
c            write(*,'(''delta x   delta y   :'',$)')
            do i=1,2
               if(xidelta(l,i) .lt. 0.) then
                  deltaN(l,i) = delta(l,i) + ddeltaN(l,i)
               else
                  deltaN(l,i) = delta(l,i) - ddeltaN(l,i)
               end if
            end do
c            write(*,'(2(E12.6,A1))') delta(l,1),' ',delta(l,2),' '
         end do

         fpA = fp
         qiA = qi
         do l=1,ni
            sommeA(l) = somme(l)
         end do

         do k=1,ns
            do l=1,ni
               xiaA(l,k) = xia(l,k)
            end do
            xicA(k,1) = xic(k,1)
            xicA(k,2) = xic(k,2)
         end do
         do l=1,ni
            do i=1,3
               xiplanA(l,i) = xiplan(l,i)
               xibA(l,i) = xib(l,i)
            end do
            xibetaA(l) = xibeta(l)
            xideltaA(l,1) = xidelta(l,1)
            xideltaA(l,2) = xidelta(l,2)
         end do

c         write(*,*) '---------------------------------------'

c        SAUVEGARDE AUTOMATIQUE APRES X ITERATIONS :
c        - - - - - - - - - - - - - - - - - - - - - -
         call inifunc_moffat(aN,bb,cN,deltaN,bN,betaN,planN,2)
         call dfunc_moffat(aN,bb,cN,deltaN,bN,betaN,planN)
         kk = mod(its+1,10)
         jj = kk+1
         if (kk.eq.0) kk = 10
         vecteurqi(kk) = qi
         if (abs(abs(vecteurqi(kk)) - 
     &        abs(vecteurqi(jj))) .le. qimin) then
            write(*,*)
            write(*,*) '==================================='
            write(*,*) '  LA VARIATION DE KHI CARRE ENTRE'
            write(*,*) '  10 ITERATIONS EST INSIGNIFIANTE'
            write(*,*) '==================================='
            return
         end if
         if (mod(its,modu) .eq. 0) then
            call decomposition_moffat(2)
            do i=1,3*ni+2*ns+13
               backspace(unit=2)
            end do
         end if

c        TEST SUR LE MINIMUM, SI ON DEPASSE LE MIN ALORS STOP
c        - - - - - - - - - - - - - - - - - - - - - - - - - - -

         if (fpA .gt. fp) then
c           MINIMUM DIMINUE
c           ---------------  
            if (arret .ne. 0) arret = 0

c           MOFFAT ET PLAN
c           - - - - - - - -
            do l=1,ni
               do k=1,3
                  db(l,k) = dbN(l,k)
                  if (xibA(l,k)*xib(l,k) .lt. 0.) then
                     dbN(l,k) = db(l,k)/2.
                  else
                    if (db(l,k)*1.1 .le. ndb(k)) dbN(l,k) = db(l,k)*1.1
                  end if
                  b(l,k) = bN(l,k)
                  dplan(l,k) = dplanN(l,k) 
                  if (xiplanA(l,k)*xiplan(l,k) .lt. 0.) then
                     dplanN(l,k) = dplan(l,k)/2.
                  else
                     if (dplan(l,k)*1.1 .le. ndplan) 
     &                  dplanN(l,k) = dplan(l,k)*1.1
                  end if
                  plan(l,k) = planN(l,k)
               end do
               dbeta(l) = dbetaN(l)
               if (xibetaA(l)*xibeta(l) .lt. 0.) then
                  dbetaN(l) = dbeta(l)/2.
               else
                  if (dbeta(l)*1.1 .le. ndbeta) 
     &               dbetaN(l) = dbeta(l)*1.1
               end if
               beta(l) = betaN(l)
            end do

c           SOURCES
c           - - - - 
            do k=1,ns
               do l=1,ni
                  da(l,k) = daN(l,k)
                  if (xiaA(l,k)*xia(l,k) .lt. 0.) then
                     daN(l,k) = da(l,k)/2.
                  else
                     if (da(l,k)*1.1 .le. nda(l,k)) 
     &                  daN(l,k) = da(l,k)*1.1
                  end if
                  a(l,k) = aN(l,k)
               end do
               dc(k,1) = dcN(k,1)
               dc(k,2) = dcN(k,2)
               do i=1,2
                  if (xicA(k,i)*xic(k,i) .lt. 0.) then
                     dcN(k,i) = dc(k,i)/2.
                  else
                     if (dc(k,i)*1.1 .le. ndc) dcN(k,i) = dc(k,i)*1.1
                  end if
               end do
               c(k,1) = cN(k,1)
               c(k,2) = cN(k,2)
            end do

c           DECALAGES
c           - - - - - -
            delta(1,1) = deltaN(1,1)
            delta(1,2) = deltaN(1,2)
            do l=2,ni
               do i=1,2
                  ddelta(l,i) = ddeltaN(l,i)
                  if (xideltaA(l,i)*xidelta(l,i) .lt. 0.) then
                     ddeltaN(l,i) = ddelta(l,i)/2.
                 else
                     if (ddelta(l,i)*1.1 .le. nddelta(i)) 
     &                  ddeltaN(l,i) = ddelta(l,i)*1.1
                  end if
                  delta(l,i) = deltaN(l,i)
               end do
            end do

         else
            arret = arret + 1
c            write(*,*)
c            write(*,*) '==============================================='
c            write(*,*) 'Chi-square increases : ',arret
c            write(*,*) '==============================================='
c            write(*,*)
            if (arret .eq. 10) then
c               write(*,*)
c               write(*,*) '=============================='
c               write(*,*) 'Chi-square increased 10 times.'
c               write(*,*) '=============================='
               return
            end if

c           MOFFAT ET PLAN
c           - - - - - - - -
            do l=1,ni
               do k=1,3
                  if (xibA(l,k)*xib(l,k) .lt. 0.) then
                     db(l,k) = db(l,k)/2.
                  else
                     dbN(l,k) = db(l,k)/1.1
                  end if
                  dbN(l,k) = db(l,k)
                  xib(l,k) = xibA(l,k) 
                  if (xiplanA(l,k)*xiplan(l,k) .lt. 0.) then
                     dplan(l,k) = dplan(l,k)/2.
                  else
                     dplan(l,k) = dplan(l,k)/1.1
                  end if
                  dplanN(l,k) = dplan(l,k)
                  xiplan(l,k) = xiplanA(l,k) 
               end do

               if (xibetaA(l)*xibeta(l) .lt. 0.) then
                  dbeta(l) = dbeta(l)/2.
               else
                  dbeta(l) = dbeta(l)/1.1
               end if
               dbetaN(l) = dbeta(l)
            end do

c           SOURCES
c           - - - - 
            do k=1,ns
               do l=1,ni
                  if (xiaA(l,k)*xia(l,k) .lt. 0.) then
                     da(l,k) = da(l,k)/2.
                  else
                     da(l,k) = da(l,k)/1.1
                  end if
                  daN(l,k) = da(l,k)
                  xia(l,k) = xiaA(l,k)
               end do
               do i=1,2
                  if (xicA(k,i)*xic(k,i) .lt. 0.) then
                      dc(k,i) = dc(k,i)/2.
                  else
                      dc(k,i) = dc(k,i)/2.
                  end if
                  xic(k,i) = xicA(k,i)
                  dcN(k,i) = dc(k,i)
               end do
            end do


c           DECALAGES
c           - - - - - -
            do l=2,ni
               do i=1,2
                  if (xideltaA(l,i)*xidelta(l,i) .lt. 0.) then
                     ddelta(l,i) = ddelta(l,i)/2.
                  else
                     ddelta(l,i) = ddelta(l,i)/1.1
                  end if
                  ddeltaN(l,i) = ddelta(l,i)
                  xidelta(l,i) = xideltaA(l,i)
               end do
            end do
            fp = fpA
            qi = qiA
            do l=1,ni
               somme(l) = sommeA(l)
            end do

         end if
      end do

c      write(*,*) "Nombre d'iterations excédé"

      return
      end

c     ====================================
c     SOUS-ROUTINE: inifunc pour la moffat
c     ====================================

      subroutine inifunc_moffat(a,bb,c,delta,b,beta,plan,normali)

      implicit none

      include 'param2.f'

      real*4 a(nbi,nbs),c(nbs,2),bb
      real*4 b(nbi,3),beta(nbi),plan(nbi,3),tplan(nbr2,nbi)
      real*4 source(nbr2,nbi),moffat(nbr2,nbi),g(nbr1,nbi)
      real*4 delta(nbi,2),sig2(nbr1,nbi)
      real*4 Fsource(nbr2,nbi),Fmoffat(nbr2,nbi),Fssource(2*xy2,nbi)
      real*4 Fsmoffat(2*xy2,nbi),t1,t2,qi,sourmofdec(nbr2,nbi)
      real*4 sourmof(nbr2),sourmof2(nbr2),ssourmof(2*xy2)
      real*4 ssourmof2(2*xy2),sourmofbis(nbr1,nbi),image(nbr2)
      real*4 phi(nbr2,nbi),fp,tplanbis(nbr1,nbi),lis
c     -------------
c     NORMALISATION
      real*4 somme(nbi),sommeA(nbi)
c     -------------

      integer i,ind,nxy1,n1,ns,ii,j,k,jj,centre,ind2,n2,nxy2,ni
      integer pas,ind1,indice,l,l2,normali
      character*20 results

      common /gr1/ g,sig2
      common /gauss/ phi
      common /moff/ source
      common /moff2/ moffat,tplan
      common /Fmoff/ Fsource,Fmoffat,Fssource,Fsmoffat
      common /moffsourg/ sourmofbis,tplanbis
      common /moffsourg2/ sourmofdec
      common /tailles/ n1,n2,ns,nxy1,nxy2,pas,ni
      common /minimum/ fp,qi,lis
c     -------------
c     NORMALISATION
      common /normalisation/ somme,sommeA
c     -------------

      centre = nxy2/2+1
      fp = 0.
      qi = 0.

      do l=1,ni

c        CALCUL DE LA MOFFAT
c        - - - - - - - - - - 
c        -------------
c        NORMALISATION
         somme(l) = 0.
c        -------------
         do j=1,nxy2
            t2 = j-centre
            jj = j+centre-1
            if (jj .gt. nxy2) jj = jj-nxy2
            do i=1,nxy2
               t1 = i-centre
               ii = i+centre-1
               if (ii .gt. nxy2) ii = ii-nxy2
               ind = ii + (jj-1)*nxy2
               phi(ind,l) = 1.+b(l,1)*t1*t1+b(l,2)*t2*t2+b(l,3)*t1*t2
               moffat(ind,l) = phi(ind,l)**(-beta(l))
c              -------------
c              NORMALISATION
               somme(l) = somme(l) + moffat(ind,l)
c              -------------
               ind2 = (j-1)*nxy2+i
               tplan(ind2,l) = plan(l,1)*i + plan(l,2)*j + plan(l,3)
            end do
         end do
c         if (normali .eq. 2) then
c            do k=1,ns
c               a(l,k) = a(l,k)*somme(l)/sommeA(l)
c            end do    
c         end if

c        CALCUL DES SOURCES
c        - - - - - - - - - - 
         do i=1,n2
            source(i,l) = 0.
         end do

         do k=1,ns
            do j=1,nxy2
               t2 = j-(c(k,2)-delta(l,2))
               do i=1,nxy2
                  t1 = i-(c(k,1)-delta(l,1))
                  ind = i + (j-1)*nxy2
                  source(ind,l) = source(ind,l) + 
     &                 a(l,k)*exp(-bb*(t1*t1+t2*t2))
               end do
            end do
         end do

         do i=1,n2
c           -------------
c           NORMALISATION
            moffat(i,l) = moffat(i,l)/somme(l)
c           -------------
            sourmof(i) = moffat(i,l)
            sourmof2(i) = source(i,l)
         end do

         call rlft2(sourmof2,ssourmof2,nxy2,nxy2,1)
         call rlft2(sourmof,ssourmof,nxy2,nxy2,1)
         do i=1,n2
            Fsource(i,l) = sourmof2(i)
            Fmoffat(i,l) = sourmof(i)
         end do
         do i=1,2*nxy2
            Fssource(i,l) = ssourmof2(i)
            Fsmoffat(i,l) = ssourmof(i)
         end do
 
         call produit(sourmof,sourmof2,ssourmof,ssourmof2,nxy2)
         call rlft2(sourmof,ssourmof,nxy2,nxy2,-1)

c        PETITS PIXELS
c        - - - - - - - 
 
         do j=1,nxy1
            do i=1,nxy1
               ind1 = nxy2*pas*(j-1)+pas*(i-1)
               indice = (j-1)*nxy1+i
               sourmofbis(indice,l) = 0.
               tplanbis(indice,l) = 0.
               do l2=1,pas
                  ind2 = (l2-1)*nxy2
                  do k=1,pas
                     sourmofbis(indice,l) = sourmofbis(indice,l) + 
     &                                      sourmof(ind1+k+ind2) 
                     sourmofdec(ind1+k+ind2,l) = sourmof(ind1+k+ind2) 
                     tplanbis(indice,l) = tplanbis(indice,l) + 
     &                                    tplan(ind1+k+ind2,l) 
                  end do
               end do
               sourmofbis(indice,l) = sourmofbis(indice,l)/real(pas**2)
               tplanbis(indice,l) = tplanbis(indice,l)/real(pas**2)
               qi = qi + sig2(indice,l)*((sourmofbis(indice,l) + 
     &                   tplanbis(indice,l)-g(indice,l))**2)
            end do
         end do
      end do

      fp = qi

      return
      end

c     ==================================
c     SOUS-ROUTINE: dfunc pour la moffat
c     ==================================

      subroutine dfunc_moffat(a,bb,c,delta,b,beta,plan)

      implicit none

      include 'param2.f'

      real*4 xia(nbi,nbs),xic(nbs,2),xib(nbi,3),xibeta(nbi)
      real*4 xiplan(nbi,3),xidelta(nbi,2),xi
      real*4 a(nbi,nbs),c(nbs,2),bb,b(nbi,3),beta(nbi)
      real*4 plan(nbi,3),delta(nbi,2)
      real*4 Fsource(nbr2,nbi),Fmoffat(nbr2,nbi)
      real*4 Fssource(2*xy2,nbi),Fsmoffat(2*xy2,nbi)
      real*4 g(nbr1,nbi),sig2(nbr1,nbi)
      real*4 rr(nbr2),srr(2*xy2),lambda(nbi)
      real*4 phi(nbr2,nbi),tplanbis(nbr1,nbi),sourmofbis(nbr1,nbi)
      real*4 tmp(nbr2),stmp(2*xy2),tmpbis,tamp
      real*4 tmpF(nbr2),stmpF(2*xy2)
      real*4 tab(nbr2,5),t1,t2,tmp3,cons
c     -------------
c     NORMALISATION
      real*4 somme(nbi),sommeA(nbi)
c     -------------
      integer i,j,ind,n1,nxy1,ns,centre,ii,jj,k,ind2,i2,ni
      integer ind1,indice,l,k2,ind4,condi,condi2
      integer n2,nxy2,pas,ibis,jbis,l2

      common /derivees_moffat/ xia,xic,xib,xibeta,xiplan,xidelta
      common /gr1/ g,sig2
      common /tailles/ n1,n2,ns,nxy1,nxy2,pas,ni
      common /lissage/ rr,srr
      common /lissage3/ lambda
      common /gauss/ phi
      common /Fmoff/ Fsource,Fmoffat,Fssource,Fsmoffat
      common /moffsourg/ sourmofbis,tplanbis
c     -------------
c     NORMALISATION
      common /normalisation/ somme,sommeA
c     -------------

      do k=1,ns
         do l=1,ni 
            xia(l,k) = 0.
         end do
         do i=1,2
            xic(k,i) = 0.
         end do   
      end do
      do l=1,ni
         do i=1,3
            xib(l,i) = 0.
            xiplan(l,i) = 0.
         end do
         xibeta(l) = 0.
         do i=1,2
            xidelta(l,i) = 0.
         end do
      end do

      do i=1,5
         do j=1,n2
            tab(j,i) = 0.
         end do
      end do

      do l=1,ni
c        DERIVEE DU PLAN
c        - - - - - - - - 
         condi = (l-1)*(7+ns)
         do j=1,nxy1
            jbis = (j-1)*pas+((pas+1)/2)
            do i=1,nxy1
               ibis = (i-1)*pas+((pas+1)/2)
               ind2 = i + (j-1)*nxy1
               tamp = 2*sig2(ind2,l)*
     &                (sourmofbis(ind2,l)+tplanbis(ind2,l)-g(ind2,l))
               xiplan(l,1) = xiplan(l,1) + tamp*ibis
               xiplan(l,2) = xiplan(l,2) + tamp*jbis
               xiplan(l,3) = xiplan(l,3) + tamp
            end do
         end do

c        DERIVEE DE LA MOFFAT
c        - - - - - - - - - - - 
         centre = nxy2/2+1
         do j=1,nxy2
            t2 = j-centre
            jj = j+centre-1
            if (jj .gt. nxy2) jj = jj-nxy2
            do i=1,nxy2
               t1 = i-centre
               ii = i+centre-1
               if (ii .gt. nxy2) ii = ii-nxy2
               ind = ii + (jj-1)*nxy2
               tmp3 = phi(ind,l)**(-beta(l)-1)
               tab(ind,1) = tmp3*t1*t1
               tab(ind,2) = tmp3*t2*t2
               tab(ind,3) = tmp3*t1*t2
               tab(ind,4) = ((phi(ind,l)**(-beta(l)))*
     &                       log(phi(ind,l)))
c              ------------- 
c              NORMALISATION
               tab(ind,1) = tmp3*t1*t1/somme(l)
               tab(ind,2) = tmp3*t2*t2/somme(l)
               tab(ind,3) = tmp3*t1*t2/somme(l)
               tab(ind,4) = ((phi(ind,l)**(-beta(l)))*
     &                       log(phi(ind,l)))/somme(l)
c              -------------
            end do
         end do

         do i=1,n2
            tmpF(i) = Fsource(i,l)
         end do
         do i=1,2*nxy2
             stmpF(i) = Fssource(i,l)
         end do

         do i2=1,4
            do j=1,n2
               tmp(j) = tab(j,i2)
            end do
            call rlft2(tmp,stmp,nxy2,nxy2,1)
            call produit(tmp,tmpF,stmp,stmpF,nxy2)
            call rlft2(tmp,stmp,nxy2,nxy2,-1)

            if (1.le. i2 .and. i2 .le. 3) then
               cons = -2.*beta(l)
            else 
               cons = 2.
            end if

            xi = 0.
            do j=1,nxy1
               do i=1,nxy1
                  ind1 = nxy2*pas*(j-1)+pas*(i-1)
                  indice = (j-1)*nxy1+i
                  tmpbis = 0.
                  do l2=1,pas
                     ind2 = (l2-1)*nxy2
                     do k2=1,pas
                        tmpbis = tmpbis + tmp(ind1+k2+ind2)  
                     end do
                  end do
                  tmpbis = tmpbis/real(pas**2)
                  xi = xi + 
     &               (cons*sig2(indice,l) *
     &               (sourmofbis(indice,l)+tplanbis(indice,l)
     &               -g(indice,l))*tmpbis)

               end do
            end do
            if (1.le. i2 .and. i2 .le. 3) then
               xib(l,i2) = xi
            else 
               xibeta(l) = xi
            end if
         end do

c        DERIVEE DES SOURCES
c        - - - - - - - - - - 
         
         do i=1,n2
            tmpF(i) = Fmoffat(i,l)
         end do
         do i=1,2*nxy2
             stmpF(i) = Fsmoffat(i,l)
         end do

         do k=1,ns
            do j=1,nxy2
               t2 = j-(c(k,2)-delta(l,2))
               do i=1,nxy2
                  t1 = i-(c(k,1)-delta(l,1))
                  ind = i+(j-1)*nxy2
                  tmp3 = exp(-bb*(t1*t1+t2*t2))
                  tab(ind,1) = tmp3
                  tab(ind,2) = tmp3*2.*bb*t1
                  tab(ind,3) = tmp3*2.*bb*t2
                  tab(ind,4) = tab(ind,4) - tmp3*2.*bb*a(l,k)*t1
                  tab(ind,5) = tab(ind,5) - tmp3*2.*bb*a(l,k)*t2
               end do
            end do

            do i2=1,3
               do j=1,n2
                  tmp(j) = tab(j,i2)
               end do
               call rlft2(tmp,stmp,nxy2,nxy2,1)
               call produit(tmp,tmpF,stmp,stmpF,nxy2)
               call rlft2(tmp,stmp,nxy2,nxy2,-1)

               if (i2.eq.1) then
                  cons = 2.
               else if (i2.eq.2) then
                  cons = 2.*a(l,k)
               else if (i2.eq.3) then
                  cons = 2.*a(l,k)
               end if

               xi = 0.
               do j=1,nxy1
                  do i=1,nxy1
                     ind1 = nxy2*pas*(j-1)+pas*(i-1)
                     indice = (j-1)*nxy1+i
                     tmpbis = 0.
                     do l2=1,pas
                        ind2 = (l2-1)*nxy2
                        do k2=1,pas
                           tmpbis = tmpbis + tmp(ind1+k2+ind2)  
                        end do
                     end do
                     tmpbis = tmpbis/real(pas**2)
                     xi = xi + 
     &                   (cons*sig2(indice,l) * 
     &                   (sourmofbis(indice,l)+tplanbis(indice,l)
     &                    -g(indice,l))*tmpbis)
                  end do
               end do
               if (i2.eq.1) then
                  xia(l,k) = xi
               else if (i2.eq.2) then
                  xic(k,1) = xic(k,1) + xi
               else if (i2.eq.3) then
                  xic(k,2) = xic(k,2) + xi
               end if
            end do
         end do

c        DERIVEE DES DECALAGES
c        - - - - - - - - - - - -

         if (l .ne. 1) then
            do i2=4,5
               do j=1,n2
                  tmp(j) = tab(j,i2)
               end do
               call rlft2(tmp,stmp,nxy2,nxy2,1)
               call produit(tmp,tmpF,stmp,stmpF,nxy2)
               call rlft2(tmp,stmp,nxy2,nxy2,-1)

               do j=1,nxy1
                  do i=1,nxy1
                     ind1 = nxy2*pas*(j-1)+pas*(i-1)
                     indice = (j-1)*nxy1+i
                     tmpbis = 0.
                     do l2=1,pas
                        ind2 = (l2-1)*nxy2
                        do k2=1,pas
                           tmpbis = tmpbis + tmp(ind1+k2+ind2)  
                        end do
                     end do
                     tmpbis = tmpbis/real(pas**2)
                     xidelta(l,i2-3) = xidelta(l,i2-3) + 
     &                  (2.*sig2(indice,l) *
     &                  (sourmofbis(indice,l)+tplanbis(indice,l)
     &                  -g(indice,l))*tmpbis)

                  end do
               end do
            end do
         end if
      end do

      return
      end

c     ==========================================
c     SOUS-ROUTINE: décomposition pour la moffat
c     ==========================================

      subroutine decomposition_moffat(init)

      include 'param2.f'

      real*4 a(nbi,nbs),bb,c(nbs,2),tmp(nbr2),tmp2(nbr1)
      real*4 b(nbi,3),beta(nbi),sourmofbis(nbr1,nbi),tplanbis(nbr1,nbi)
      real*4 g(nbr1,nbi),sig2(nbr1,nbi),somme
      real*4 source(nbr2,nbi),moffat(nbr2,nbi),sourmofdec(nbr2,nbi)
      real*4 plan(nbi,3),tplan(nbr2,nbi),delta(nbi,2)
      integer i,n1,nxy1,n2,nxy2,pas,ni,init
      character*20 results,name_moffat(nbi)
      character*1 minimum_moffat,lettre,lettre2,lettre3
      character*8 mot

      common /gr1/ g,sig2
      common /var_moffat/ b,beta
      common /var_source/ a,bb,c,delta
      common /var_plan/ plan
      common /tailles/ n1,n2,ns,nxy1,nxy2,pas,ni
      common /moff/ source
      common /moff2/ moffat,tplan
      common /moffsourg/ sourmofbis,tplanbis
      common /moffsourg2/ sourmofdec
      common /fichier_sortie/ minimum_moffat,name_moffat

c      write(*,*) 'décomposition'
      if (init.eq.1) then
         call inifunc_moffat(a,bb,c,delta,b,beta,plan,1)
         call dfunc_moffat(a,bb,c,delta,b,beta,plan)
      end if

      do l=1,ni
         lettre = char(48+int(l/100))
         ll = l - int(l/100)
         lettre2 = char(48+int(ll/10))
         lettre3 = char(48+mod(ll,10))
         mot = lettre // lettre2 // lettre3 // '.fits'
   
         do i=1,n2
            tmp(i) =  source(i,l)  
         end do
         results = 'source' // mot
         call makeima(results,nxy2,tmp)

         do i=1,n2
            tmp(i) =  tplan(i,l)  
         end do
         results = 'plan' // mot
         call makeima(results,nxy2,tmp)

         somme = 0.
         centre = nxy2/2+1
         do j=1,nxy2
            t2 = j-centre
            do i=1,nxy2
               t1 = i-centre
               ind = i + (j-1)*nxy2
               phi = 1. + b(l,1)*t1*t1 + b(l,2)*t2*t2 + b(l,3)*t1*t2
               tmp(ind) = phi**(-beta(l))
               somme = somme + tmp(ind)
            end do
         end do
         do i=1,n2
            tmp(i) = tmp(i)/somme
         end do
         results = 'moffat' // mot
         call makeima(results,nxy2,tmp)

         do i=1,n2
            tmp(i) = sourmofdec(i,l)+tplan(i,l)
         end do
         results = 'somme' // mot
         call makeima(results,nxy2,tmp)

         do i=1,n1
            tmp2(i) = (sourmofbis(i,l)+tplanbis(i,l)-g(i,l))*
     &                sqrt(sig2(i,l))
         end do
         results = 'residu' // mot
         call makeima(results,nxy1,tmp2)
      end do

c        ECRITURE DANS LE FICHIER DE SORTIE
c        - - - - - - - - - - - - - - - - - -

      if (minimum_moffat .eq. 'y') then
         write(2,'(A1)') 'y'
         do l=1,ni
             write(2,*) b(l,1),b(l,2),b(l,3),beta(l)
         end do
      else if (minimum_moffat .eq. 'n') then
         write(2,'(A1)') 'n'
         do l=1,ni
             write(2,*) b(l,1),b(l,2),b(l,3),beta(l)
         end do
      else if (minimum_moffat .eq. 'i') then
         write(2,'(A1)') 'i'
         do l=1,ni
            write(2,'(A20)') name_moffat(l)
         end do
      end if            
      write(2,'(A55)') 
     &        '-------------------------------------------------------'
      write(2,'(A55)') 
     &        '| Paramètres initiaux du plan (alpha beta gamma) * ni |'
      write(2,'(A55)') 
     &        '-------------------------------------------------------'
      do l=1,ni
         write(2,*) plan(l,1),plan(l,2),plan(l,3)
      end do
      write(2,'(A55)') 
     &        '-------------------------------------------------------'
      write(2,'(A55)') 
     &        '| Paramètres initiaux des décalages                  |'
      write(2,'(A55)') 
     &        '| ( deltaX deltaY ) * ni                              |'
      write(2,'(A55)') 
     &        '-------------------------------------------------------'
      do l=1,ni
         write(2,*) delta(l,1),delta(l,2)
      end do
      write(2,'(A55)') 
     &        '-------------------------------------------------------'
      write(2,'(A55)') 
     &        '| Paramètres initiaux des sources                     |'
      write(2,'(A55)') 
     &        '| a(1) ... a(ni) }                                    |'
      write(2,'(A55)') 
     &        '| cx cy          } * ns                               |'
      write(2,'(A55)') 
     &        '-------------------------------------------------------'
      do i=1,ns
         write(2,*) (a(l,i),l=1,ni)
         write(2,*) (c(i,1)+((real(pas)-1)/real(pas)))/pas,
     &              (c(i,2)+((real(pas)-1)/real(pas)))/pas
      end do

      return
      end

c     ===========================================================
c     ===========================================================
C       FFFFFFF  OOOOO  NN    N DDDDD        +
C       F       O     O N N   N D    D       +   
C       FFFF    O     O N  N  N D    D    +++++++     OOOOOOOO
C       F       O     O N   N N D    D       +
C       F        OOOOO  N    NN DDDDD        +
c     ===========================================================
C      FOND + SOURCES + DECALAGES + PLAN
c     ===========================================================
c     ===========================================================

c     =========================================
c     SUBROUTINE: minimi pour le calcul du fond
c     =========================================

      subroutine minimi_fond(itmax,modu,qimin,its)

      implicit none
 
      include 'param2.f'

      real*4 eps
      parameter (eps=1.E-10)

      real*4 f(nbr2,nbi),a(nbi,nbs),bb,c(nbs,2),plan(nbi,3)
      real*4 fN(nbr2,nbi),aN(nbi,nbs),cN(nbs,2),planN(nbi,3)
      real*4 df(nbr2,nbi),da(nbi,nbs),dc(nbs,2),dplan(nbi,3)
      real*4 dfN(nbr2,nbi),daN(nbi,nbs),dcN(nbs,2),dplanN(nbi,3)
      real*4 delta(nbi,2),deltaN(nbi,2),ddelta(nbi,2),ddeltaN(nbi,2)
      real*4 ndf,nda(nbi,nbs),ndc,ndplan,nddelta(2)
      real*4 xia(nbi,nbs),xic(nbs,2),xiplan(nbi,3)
      real*4 xifA(nbr2,nbi),xiaA(nbi,nbs),xicA(nbs,2),xiplanA(nbi,3)
      real*4 xidelta(nbi,2),xideltaA(nbi,2),resi_min
      real*4 vecteurqi(10),fp,fpA,qi,qiA,qimin,lisA
      real*4 moffatfixe(nbr2,nbi),rxif(nbr2,nbi)
      real*4 xifterme(nbr2,nbi),xiflissage(nbr2,nbi)
      real*4 xiftermeA(nbr2,nbi),xiflissageA(nbr2,nbi)
      real*4 sommeXI,sommeXI2,lis,rr(nbr2),srr(2*xy2),terme2
      real*4 tmp2,tmp(nbr2),stmp(2*xy2),fwhmgauss,stepgauss,bgauss
      real*4 pasconst,cxgauss,cygauss,sommeA(nbi),t1,t2,dfgauss
      real*4 sommeXIA,xi,xi2,g(nbr1,nbi),sig2(nbr1,nbi),maxlissage(nbi)
      real*4 tmp4(nbr2),factqi
      integer its,itmax,modu,k,n1,ns,nxy1,ind,iter,i,n2,nxy2
      integer pas,j,ii,ni,l,ind2,arret,kk,jj,itergauss,flag
      integer ii2,ind3,qicible,aug
      integer rayon,xy_carre,nb_carre,deb,fin      

      common /gr1/ g,sig2
      common /var_fond/ f
      common /var_source/ a,bb,c,delta
      common /var_plan/ plan
      common /delta_fond/ df
      common /delta_source/ da,dc,ddelta
      common /delta_plan/ dplan
      common /deltacons_fond/ ndf
      common /deltacons_source/ nda,ndc,nddelta
      common /deltacons_plan/ ndplan
      common /tailles/ n1,n2,ns,nxy1,nxy2,pas,ni
      common /derivees_fond/ xia,xic,xiplan,xidelta
      common /derivees_extra/ xifterme,xiflissage
      common /minimum/ fp,qi,lis
      common /minimum2/ fpA,qiA
      common /moffat_fixe/ moffatfixe
      common /carre/ rayon,xy_carre,nb_carre,deb,fin
      common /sommedesXI/ sommeXI,sommeXI2
      common /lissage/ rr,srr
      common /gauss_lissage/ stepgauss,fwhmgauss,resi_min,itergauss
      common /surfit/ tmp4
      common /qi_cible/ qicible

      arret = 0
      aug = 0

c     CALCUL DU MINIMUM ET DES DERIVEES :
c     - - - - - - - - - - - - - - - - - -
      call inifunc_fond(f,a,bb,c,delta,plan)
      call dfunc_fond(f,a,bb,c,delta,plan)


      write(4,*) '------------------------------------'
      write(4,*) '          TEST des sigma            '
      write(4,*) '------------------------------------'
      if (qi .gt. 2*qicible) then
         factqi = qi-0.9*real(qicible)
         write(4,*) 'OK     (2*qicible < qi)'
      else if (qicible .lt. qi .and. qi .lt. 2*qicible) then
         factqi = qi-0.5*real(qicible)
         write(4,*) 'OK     (qicible < qi < 2*qicible)'
      else if (qi .le. qicible) then
         factqi = qi
         write(4,*) 'ATTENTION     (qi <= qicible)'
      end if
      write(4,*) '- - - - - - - - - - - - - - - - - - '
      write(4,*) 'qicible = ',qicible
      write(4,*) 'qi      = ',qi

      do l=1,ni
         do i=1,n2
            tmp(i) = 0.
         end do
         do j=deb,fin
            do i=deb,fin
               ind = (j-1)*nxy2+i
               tmp(ind) = abs(xifterme(ind,l))
            end do
         end do
         call rlft2(tmp,stmp,nxy2,nxy2,1)
         call produit(tmp,rr,stmp,srr,nxy2)
         call rlft2(tmp,stmp,nxy2,nxy2,-1)
         do i=1,n2
            rxif(i,l) = tmp(i)
         end do
      end do

      vecteurqi(1) = qi
      do i=2,10
         vecteurqi(i) = 0.
      end do

      do l=1,ni
         do j=1,n2
            fN(j,l) = f(j,l)
            df(j,l) = df(j,l)*(factqi/sommeXI2)
            dfN(j,l) = df(j,l)
         end do
         do i=1,3
            dplanN(l,i) = dplan(l,i)
         end do
         do i=1,2
            ddeltaN(l,i) = ddelta(l,i)
         end do
      end do
      do i=1,ns
         do l=1,ni
            daN(l,i) = da(l,i)
         end do
         dcN(i,1) = dc(i,1)
         dcN(i,2) = dc(i,2)
      end do 

      cxgauss = nxy2/2.+1. 
      cygauss = nxy2/2.+1.

      do its=1,itmax

         bgauss = 4.*log(2.)/(fwhmgauss**2)

c         write(*,*) 'Background iteration ', its,', min khi: ',fp,qi
        if (aug .eq. 0) then
c         write(*,*) '=================================================='
        else
c         write(*,*) '**************************************************'
c         write(*,*)
         aug = 0
        end if
         iter = its


c        MODIFICATION SOURCES
c        - - - - - - - - - - -
         do l=1,ni
            sommeA(l) = 0. 
         end do
         do k=1,ns
c            write(*,'(''a ... a cx cy       :'',$)')
            do l=1,ni
               sommeA(l) = sommeA(l) + a(l,k)
               if (xia(l,k) .lt. 0.) then
                  aN(l,k) = a(l,k) + daN(l,k)
               else
                  aN(l,k) = a(l,k) - daN(l,k)
               end if
c               write(*,'(E12.6,A1,$)') aN(l,k),' '
            end do
            do i=1,2
               if(xic(k,i) .lt. 0.) then
                  cN(k,i) = c(k,i) + dcN(k,i)
               else
                  cN(k,i) = c(k,i) - dcN(k,i)
               end if
            end do
c            write(*,'(2(E12.6,A1))') cN(k,1)+((real(pas)-1)/real(pas)),
c     &                ' ',cN(k,2)+((real(pas)-1)/real(pas)),' '
         end do

c        MODIFICATION DU FOND
c        - - - - - - - - - - -
         do l=1,ni
            flag = 0
            do j=deb,fin
               jj = int((j-1)/pas)+1
               t2 = j - cygauss
               do i=deb,fin
                  ii2 = int((i-1)/pas)+1
                  ind = (j-1)*nxy2+i
                  ind3 = (jj-1)*nxy1+ii2
                  t1 = i - cxgauss
                  dfgauss = exp(-bgauss*(t1*t1+t2*t2))
                  if (rxif(ind,l) .gt. tmp4(ind)*resi_min) then
                     fN(ind,l) = f(ind,l) - 
     &               (xifterme(ind,l)+xiflissage(ind,l))*
     &               (dfN(ind,l)*dfgauss)
                     flag = flag + 1
                  else
                     fN(ind,l) = f(ind,l)
                  end if
               end do
            end do
c            write(*,*) 'Image ',l,
c     &                 ', Nbr de pixels qui changent : ',flag 
            if (flag .eq. 0) then
c               write(*,*) 'Plus rien ne change'
               goto 10
            end if

         end do

c        MODIFICATION DECALAGES
c        - - - - - - - - - - - - 
         deltaN(1,1) = delta(1,1)
         deltaN(1,2) = delta(1,2)
c         write(*,'('' Delta x   Delta y : '',$)')
c        write(*,'(2(E12.6,A1))') deltaN(1,1),'  ',deltaN(1,2),' '
         do l=2,ni
c            write(*,'('' Delta x   Delta y : '',$)')
            do i=1,2
               if(xidelta(l,i) .lt. 0.) then
                  deltaN(l,i) = delta(l,i) + ddeltaN(l,i)
               else
                 deltaN(l,i) = delta(l,i) - ddeltaN(l,i)
               end if 
            end do
c            write(*,'(2(E12.6,A1))') deltaN(l,1),' ',deltaN(l,2),' '
         end do

c        MODIFICATION PLAN
c        - - - - - - - - -
         do l=1,ni
            do k=1,3
               if (xiplan(l,k) .lt. 0.) then
                  planN(l,k) = plan(l,k) + dplanN(l,k)
               else
                  planN(l,k) = plan(l,k) - dplanN(l,k)
               end if
            end do
c            write(*,*) 'Plan              :',
c     &                  planN(l,1),planN(l,2),planN(l,3)
         end do

         fpA = fp
         qiA = qi 
         sommeXIA = sommeXI
         do k=1,ns
            do l=1,ni
               xiaA(l,k) = xia(l,k)
            end do
            xicA(k,1) = xic(k,1)
            xicA(k,2) = xic(k,2)
         end do
         do l=1,ni
            do i=1,n2
               xiftermeA(i,l) = xifterme(i,l)
               xiflissageA(i,l) = xiflissage(i,l)
            end do
            do i=1,3
               xiplanA(l,i) = xiplan(l,i)
            end do
            xideltaA(l,1) = xidelta(l,1)
            xideltaA(l,2) = xidelta(l,2)
         end do

c         write(*,*) '---------------------------------------'

c        SAUVEGARDE AUTOMATIQUE APRES X ITERATIONS:
c        - - - - - - - - - - - - - - - - - - - - - -
         call inifunc_fond(fN,aN,bb,cN,deltaN,planN)
         call dfunc_fond(fN,aN,bb,cN,deltaN,planN)

         do l=1,ni
            do i=1,n2
               tmp(i) = 0.
            end do
            do j=deb,fin
               do i=deb,fin
                  ind = (j-1)*nxy2+i
                  tmp(ind) = abs(xifterme(ind,l))
               end do
            end do
            call rlft2(tmp,stmp,nxy2,nxy2,1)
            call produit(tmp,rr,stmp,srr,nxy2)
            call rlft2(tmp,stmp,nxy2,nxy2,-1)
            do i=1,n2
               rxif(i,l) = tmp(i)
            end do
         end do

         kk = mod(its+1,10)
         jj = kk+1
         if (kk.eq.0) kk = 10
         vecteurqi(kk) = qi
         if (abs(abs(vecteurqi(kk)) - 
     &        abs(vecteurqi(jj))) .le. qimin) then
c            write(*,*)
c            write(*,*) '==================================='
c            write(*,*) '  LA VARIATION DE KHI CARRE ENTRE'
c            write(*,*) '  10 ITERATIONS EST INSIGNIFIANTE'
c            write(*,*) '==================================='
            goto 10
         end if
         if (mod(its,modu) .eq. 0) then
            call decomposition_fond(2)
            do i=1,3*ni+2*ns+13
               backspace(unit=2)
            end do
         end if

c        TEST DU MINIMUM, SI LE MINIMUM AUGMENTE ALORS STOP
c        - - - - - - - - - - - - - - - - - - - - - - - - - -
         if (fpA .gt. fp) then
c           MINIMUM DIMINUE
c           ---------------  
            if (arret .ne. 0) arret = 0

c           FOND
c           - - -
            do l=1,ni
               do j=deb,fin
                  do i=deb,fin
                     ind = (j-1)*nxy2+i
                     df(ind,l) = dfN(ind,l)
                     xi2 = xiftermeA(ind,l)+xiflissageA(ind,l)
                     xi = xifterme(ind,l)+xiflissage(ind,l)
                     if (xi2*xi .lt. 0.) then
                        dfN(ind,l) = (df(ind,l)*sommeXIA)/(2.*sommeXI)
                     else
                        if (df(ind,l)*1.1 .le. 
     &                     moffatfixe(ind,l)*ndf) then
                           dfN(ind,l) = (df(ind,l)*sommeXIA*1.1)/sommeXI
                        end if
                     end if
                     f(ind,l) = fN(ind,l)
                  end do
               end do
            end do
 
c           SOURCES
c           - - - - 
            do k=1,ns
               do l=1,ni
                  da(l,k) = daN(l,k)
                  if (xiaA(l,k)*xia(l,k) .lt. 0.) then
                     daN(l,k) = da(l,k)/2.
                  else
                     if (da(l,k)*1.1 .le. nda(l,k)) 
     &                  daN(l,k) = da(l,k)*1.1
                  end if
                  a(l,k) = aN(l,k)
               end do
               dc(k,1) = dcN(k,1)
               dc(k,2) = dcN(k,2)
               do i=1,2
                  if (xicA(k,i)*xic(k,i) .lt. 0.) then
                     dcN(k,i) = dc(k,i)/2.
                  else
                     if (dc(k,i)*1.1 .le. ndc) dcN(k,i) = dc(k,i)*1.1
                  end if
               end do
               c(k,1) = cN(k,1)
               c(k,2) = cN(k,2)
            end do

c           DECALAGE
c           - - - - - 
            delta(1,1) = deltaN(1,1)
            delta(1,2) = deltaN(1,2)
            do l=2,ni
               do i=1,2
                  ddelta(l,i) = ddeltaN(l,i)
                  if (xideltaA(l,i)*xidelta(l,i) .lt. 0.) then
                     ddeltaN(l,i) = ddelta(l,i)/2.
                 else
                     if (ddelta(l,i)*1.1 .le. nddelta(i)) 
     &                  ddeltaN(l,i) = ddelta(l,i)*1.1
                  end if
                  delta(l,i) = deltaN(l,i)
               end do
            end do

c           PLAN
c           - - -
            do l=1,ni
               do k=1,3
                  dplan(l,k) = dplanN(l,k)
                  if (xiplanA(l,k)*xiplan(l,k) .lt. 0.) then
                     dplanN(l,k) = dplan(l,k)/2.
                  else
                     if (dplan(l,k)*1.1 .le. ndplan) then
                        dplanN(l,k) = dplan(l,k)*1.1
                     end if
                  end if
                  plan(l,k) = planN(l,k)
               end do
            end do
            if (itergauss .gt. 0) then
               fwhmgauss = fwhmgauss+stepgauss
               itergauss = itergauss - 1
            end if
         else  
            aug = 1
            arret = arret + 1

c            write(*,*) its+1,' M  (fond)   min khi: ',fp,qi
c            write(*,*)
c            write(*,*) '  ON DEPASSE LE MIN (dépassement n° ',arret,' )'
c            write(*,*) '==============================================='
c            write(*,*) '******* ON REPART DES VALEURS SUIVANTES *******'
            do k=1,ns
c               write(*,'(''a ... a cx cy       :'',$)')
               do l=1,ni
c                  write(*,'(E12.6,A1,$)') a(l,k),' '
               end do
c               write(*,'(2(E12.6,A1))') c(k,1),' ',c(k,2),' '
            end do
            do l=1,ni
c               write(*,'(''delta x   delta y   :'',$)')
c               write(*,'(2(E12.6,A1))') delta(l,1),' ',delta(l,2),' '
            end do
            do l=1,ni
c              write(*,*) 'plan =  ',
c    &           plan(l,3),' + ',plan(l,1),' x + ',plan(l,2),' y + '
            end do


            if (arret .eq. 10) then
c               write(*,*)
c               write(*,*) '=============================='
c               write(*,*) 'Chi-squared increased 10 times'
c               write(*,*) '=============================='
               goto 10
            end if

c           FOND
c           - - -
            do l=1,ni
               do j=deb,fin
                  do i=deb,fin
                     ind = (j-1)*nxy2+i
                     xi2 = xiftermeA(ind,l)+xiflissageA(ind,l)
                     xi = xifterme(ind,l)+xiflissage(ind,l)
                     if (xi2*xi .lt. 0.) then
                        df(ind,l) = df(ind,l)/2.
                     else
                        df(ind,l) = df(ind,l)/1.1
                     end if
                     dfN(ind,l) = df(ind,l)
                     xiflissage(ind,l) = xiflissageA(ind,l)
                     xifterme(ind,l) = xiftermeA(ind,l)
                  end do
               end do
            end do 

c           SOURCES
c           - - - - 
            do k=1,ns
               do l=1,ni
                  if (xiaA(l,k)*xia(l,k) .lt. 0.) then
                     da(l,k) = da(l,k)/2.
                  else
                     da(l,k) = da(l,k)/1.1
                  end if
                  daN(l,k) = da(l,k)
                  xia(l,k) = xiaA(l,k)
               end do
               do i=1,2
                  if (xicA(k,i)*xic(k,i) .lt. 0.) then
                      dc(k,i) = dc(k,i)/2.
                  else
                      dc(k,i) = dc(k,i)/1.1
                  end if
                  xic(k,i) = xicA(k,i)
                  dcN(k,i) = dc(k,i)
               end do
            end do

c           DECALAGES
c           - - - - - -
            do l=2,ni
               do i=1,2
                  if (xideltaA(l,i)*xidelta(l,i) .lt. 0.) then
                     ddelta(l,i) = ddelta(l,i)/2.
                  else
                     ddelta(l,i) = ddelta(l,i)/1.1
                  end if
                  ddeltaN(l,i) = ddelta(l,i)
                  xidelta(l,i) = xideltaA(l,i)
               end do
            end do

c           PLAN
c           - - -
            do l=1,ni
               do k=1,3
                  if (xiplanA(l,k)*xiplan(l,k) .lt. 0.) then
                     dplan(l,k) = dplan(l,k)/2.
                  else
                      dplan(l,k) = dplan(l,k)/1.1
                  end if
                  dplanN(l,k) = dplan(l,k)
                  xiplan(l,k) = xiplanA(l,k)
               end do
            end do
            fp = fpA
            qi = qiA
            sommeXI = sommeXIA

         end if
      end do

c      write(*,*) "Nombre d'iterations excédé"

 10       write(4,*) '------------------------------------'
          write(4,*) '          MINIMI FOND               '
          write(4,*) '------------------------------------'
          write(4,*) 'Nombre itérations:   ',its
          write(4,*) 'Valeur du minimum:   ',fpA
          write(4,*) 'Valeur du khi carré: ',qiA
          write(4,*)

c     *************************************************
c     *************************************************
c     CYCLE 2:  ATTENTION NE MARCHE QUE POUR UNE IMAGE
c     *************************************************
c     *************************************************

      arret = 0
      do l=1,ni
         maxlissage(l) = 0.
         do i=1,n2
            tmp(i) = 0.
         end do
         do j=deb,fin
            do i=deb,fin
               ind = (j-1)*nxy2+i
               tmp(ind) = abs(xifterme(ind,l))
               if (abs(xiflissage(ind,l)).gt.maxlissage(l)) then
                  maxlissage(l)=abs(xiflissage(ind,l))
              end if
            end do
         end do
         call rlft2(tmp,stmp,nxy2,nxy2,1)
         call produit(tmp,rr,stmp,srr,nxy2)
         call rlft2(tmp,stmp,nxy2,nxy2,-1)
         do i=1,n2
            rxif(i,l) = tmp(i)
         end do
c         write(*,*) 'Maxlissage ',l,' : ',maxlissage(l)
      end do

      vecteurqi(1) = qi
      do i=2,10
         vecteurqi(i) = 0.
      end do

      do l=1,ni
         do j=1,n2
            df(j,l) = 0.00001/maxlissage(l)
            dfN(j,l) = df(j,l)
         end do
         do i=1,3
            dplanN(l,i) = dplan(l,i)
         end do
         do i=1,2
            ddeltaN(l,i) = ddelta(l,i)
         end do
      end do
      do i=1,ns
         do l=1,ni
            daN(l,i) = da(l,i)
         end do
         dcN(i,1) = dc(i,1)
         dcN(i,2) = dc(i,2)
      end do 

      aug = 0
      do its=1,100

c         write(*,*) '2nd cycle iteration ', its, ', min khi lis : ',
c     &        fp,qi,lis
        if (aug .eq. 0) then
c         write(*,*) '=================================================='
        else
c         write(*,*) '**************************************************'
c         write(*,*)
         aug = 0
        end if
         iter = its


c        MODIFICATION SOURCES
c        - - - - - - - - - - -
         do l=1,ni
            sommeA(l) = 0. 
         end do
         do k=1,ns
c            write(*,'(''a ... a cx cy       :'',$)')
            do l=1,ni
               sommeA(l) = sommeA(l) + a(l,k)
               if (xia(l,k) .lt. 0.) then
                  aN(l,k) = a(l,k) + daN(l,k)
               else
                  aN(l,k) = a(l,k) - daN(l,k)
               end if
c               write(*,'(E12.6,A1,$)') aN(l,k),' '
            end do
            do i=1,2
               if(xic(k,i) .lt. 0.) then
                  cN(k,i) = c(k,i) + dcN(k,i)
               else
                  cN(k,i) = c(k,i) - dcN(k,i)
               end if
            end do
c            write(*,'(2(E12.6,A1))') cN(k,1)+((real(pas)-1)/real(pas)),
c     &                ' ',cN(k,2)+((real(pas)-1)/real(pas)),' '
         end do

c        MODIFICATION DU FOND
c        - - - - - - - - - - -
         do l=1,ni
            flag = 0
            do j=deb,fin
               jj = int((j-1)/pas)+1
               do i=deb,fin
                  ii2 = int((i-1)/pas)+1
                  ind = (j-1)*nxy2+i
                  ind3 = (jj-1)*nxy1+ii2
c                  tmp2 = rxif(ind,l)/(2.*sommeA(l)*sqrt(sig2(ind3,l)))
                  if (rxif(ind,l) .lt. tmp4(ind)*resi_min) then
                     fN(ind,l) = f(ind,l) - xiflissage(ind,l)*dfN(ind,l)
                     flag = flag + 1
                  else
                     fN(ind,l) = f(ind,l)
                  end if
               end do
            end do
c            write(*,*) 'Image ',l,
c     &                 ', Nbr de pixels qui changent : ',flag 
            if (flag .eq. 0) then
c               write(*,*) 'Plus rien ne change'
               return
            end if
         end do

c        MODIFICATION DECALAGES
c        - - - - - - - - - - - - 
         deltaN(1,1) = delta(1,1)
         deltaN(1,2) = delta(1,2)
c         write(*,'('' Delta x   Delta y : '',$)')
c         write(*,'(2(E12.6,A1))') deltaN(1,1),' ',deltaN(1,2),' '
         do l=2,ni
c            write(*,'('' Delta x   Delta y : '',$)')
            do i=1,2
               if(xidelta(l,i) .lt. 0.) then
                  deltaN(l,i) = delta(l,i) + ddeltaN(l,i)
               else
                 deltaN(l,i) = delta(l,i) - ddeltaN(l,i)
               end if 
            end do
c            write(*,'(2(E12.6,A1))') deltaN(l,1),'  ',deltaN(l,2),' '
         end do

c        MODIFICATION PLAN
c        - - - - - - - - -
         do l=1,ni
            do k=1,3
               if (xiplan(l,k) .lt. 0.) then
                  planN(l,k) = plan(l,k) + dplanN(l,k)
               else
                  planN(l,k) = plan(l,k) - dplanN(l,k)
               end if
            end do
c            write(*,*) 'Plan              :',
c     &                  planN(l,1),planN(l,2),planN(l,3)
         end do

         fpA = fp
         qiA = qi 
         lisA = lis
         sommeXIA = sommeXI
         do k=1,ns
            do l=1,ni
               xiaA(l,k) = xia(l,k)
            end do
            xicA(k,1) = xic(k,1)
            xicA(k,2) = xic(k,2)
         end do
         do l=1,ni
            do i=1,n2
               xiftermeA(i,l) = xifterme(i,l)
               xiflissageA(i,l) = xiflissage(i,l)
            end do
            do i=1,3
               xiplanA(l,i) = xiplan(l,i)
            end do
            xideltaA(l,1) = xidelta(l,1)
            xideltaA(l,2) = xidelta(l,2)
         end do

c         write(*,*) '---------------------------------------'

c        SAUVEGARDE AUTOMATIQUE APRES 10 ITERATIONS :
c        - - - - - - - - - - - - - - - - - - - - - - -
         call inifunc_fond(fN,aN,bb,cN,deltaN,planN)
         call dfunc_fond(fN,aN,bb,cN,deltaN,planN)

         do l=1,ni
            do i=1,n2
               tmp(i) = 0.
            end do
            do j=deb,fin
               do i=deb,fin
                  ind = (j-1)*nxy2+i
                  tmp(ind) = abs(xifterme(ind,l))
               end do
            end do
            call rlft2(tmp,stmp,nxy2,nxy2,1)
            call produit(tmp,rr,stmp,srr,nxy2)
            call rlft2(tmp,stmp,nxy2,nxy2,-1)
            do i=1,n2
               rxif(i,l) = tmp(i)
            end do
         end do

         kk = mod(its+1,10)
         jj = kk+1
         if (kk.eq.0) kk = 10
         vecteurqi(kk) = qi
         if (abs(abs(vecteurqi(kk)) - 
     &        abs(vecteurqi(jj))) .le. qimin) then
            write(*,*)
            write(*,*) '==================================='
            write(*,*) '  LA VARIATION DE KHI CARRE ENTRE'
            write(*,*) '  10 ITERATIONS EST INSIGNIFIANTE'
            write(*,*) '==================================='
            return
         end if
         if (mod(its,modu) .eq. 0) then
            call decomposition_fond(2)
            do i=1,3*ni+2*ns+13
               backspace(unit=2)
            end do
         end if

c        TEST SUR LE MINIMUM, SI ON DEPASSE LE MIN ALORS STOP
c        - - - - - - - - - - - - - - - - - - - - - - - - - -
         if (lisA .gt. lis) then
c           MINIMUM DIMINUE
c           ---------------  
            if (arret .ne. 0) arret = 0

c           FOND
c           - - -
            do l=1,ni
               do j=deb,fin
                  do i=deb,fin
                     ind = (j-1)*nxy2+i
                     df(ind,l) = dfN(ind,l)
                     if (xiflissageA(ind,l)*xiflissage(ind,l) 
     &                   .lt. 0.) then
                        dfN(ind,l) = df(ind,l)/2.
                     else
                        if (df(ind,l)*1.1 .le. 
     &                     moffatfixe(ind,l)*ndf) then
                           dfN(ind,l) = df(ind,l)*1.1
                        end if
                     end if
                     f(ind,l) = fN(ind,l)
                  end do
               end do
            end do
 
c           SOURCES
c           - - - - 
            do k=1,ns
               do l=1,ni
                  da(l,k) = daN(l,k)
                  if (xiaA(l,k)*xia(l,k) .lt. 0.) then
                     daN(l,k) = da(l,k)/2.
                  else
                     if (da(l,k)*1.1 .le. nda(l,k)) 
     &                  daN(l,k) = da(l,k)*1.1
                  end if
                  a(l,k) = aN(l,k)
               end do
               dc(k,1) = dcN(k,1)
               dc(k,2) = dcN(k,2)
               do i=1,2
                  if (xicA(k,i)*xic(k,i) .lt. 0.) then
                     dcN(k,i) = dc(k,i)/2.
                  else
                     if (dc(k,i)*1.1 .le. ndc) dcN(k,i) = dc(k,i)*1.1
                  end if
               end do
               c(k,1) = cN(k,1)
               c(k,2) = cN(k,2)
            end do

c           DECALAGE
c           - - - - - 
            delta(1,1) = deltaN(1,1)
            delta(1,2) = deltaN(1,2)
            do l=2,ni
               do i=1,2
                  ddelta(l,i) = ddeltaN(l,i)
                  if (xideltaA(l,i)*xidelta(l,i) .lt. 0.) then
                     ddeltaN(l,i) = ddelta(l,i)/2.
                 else
                     if (ddelta(l,i)*1.1 .le. nddelta(i)) 
     &                  ddeltaN(l,i) = ddelta(l,i)*1.1
                  end if
                  delta(l,i) = deltaN(l,i)
               end do
            end do

c           PLAN
c           - - -
            do l=1,ni
               do k=1,3
                  dplan(l,k) = dplanN(l,k)
                  if (xiplanA(l,k)*xiplan(l,k) .lt. 0.) then
                     dplanN(l,k) = dplan(l,k)/2.
                  else
                     if (dplan(l,k)*1.1 .le. ndplan) then
                        dplanN(l,k) = dplan(l,k)*1.1
                     end if
                  end if
                  plan(l,k) = planN(l,k)
               end do
            end do
         else  
            aug = 1
            arret = arret + 1

            write(*,*) its+1,' M  (cycle 2)   min khi lis: ',fp,qi,lis
c            write(*,*)
c            write(*,*) '  ON DEPASSE LE LISSAGE (dépas. n° ',arret,' )'
c            write(*,*) '==============================================='
c            write(*,*) '******* ON REPART DES VALEURS SUIVANTES *******'
            do k=1,ns
c               write(*,'(''a ... a cx cy       :'',$)')
               do l=1,ni
c                  write(*,'(E12.6,A1,$)') a(l,k),' '
               end do
c               write(*,'(2(E12.6,A1))') c(k,1),' ',c(k,2),' '
            end do
            do l=1,ni
c               write(*,'(''delta x   delta y   :'',$)')
c               write(*,'(2(E12.6,A1))') delta(l,1),' ',delta(l,2),' '
            end do
            do l=1,ni
c               write(*,*) 'plan =  ',
c     &           plan(l,3),' + ',plan(l,1),' x + ',plan(l,2),' y + '
            end do

            if (arret .eq. 10) then
c               write(*,*)
c               write(*,*) '=============================='
               write(*,*) 'Chi-square increased 10 times.'
c               write(*,*) '=============================='
               return
            end if

c           FOND
c           - - -
            do l=1,ni
               do j=deb,fin
                  do i=deb,fin
                     ind = (j-1)*nxy2+i
                     if (xiflissageA(ind,l)*xiflissage(ind,l) 
     &                  .lt. 0.) then
                        df(ind,l) = df(ind,l)/2.
                     else
                        df(ind,l) = df(ind,l)/1.1
                     end if
                     dfN(ind,l) = df(ind,l)
                     xiflissage(ind,l) = xiflissageA(ind,l)
                  end do
               end do
            end do 

c           SOURCES
c           - - - - 
            do k=1,ns
               do l=1,ni
                  if (xiaA(l,k)*xia(l,k) .lt. 0.) then
                     da(l,k) = da(l,k)/2.
                  else
                     da(l,k) = da(l,k)/1.1
                  end if
                  daN(l,k) = da(l,k)
                  xia(l,k) = xiaA(l,k)
               end do
               do i=1,2
                  if (xicA(k,i)*xic(k,i) .lt. 0.) then
                      dc(k,i) = dc(k,i)/2.
                  else
                      dc(k,i) = dc(k,i)/2.
                  end if
                  xic(k,i) = xicA(k,i)
                  dcN(k,i) = dc(k,i)
               end do
            end do

c           DECALAGES
c           - - - - - -
            do l=2,ni
               do i=1,2
                  if (xideltaA(l,i)*xidelta(l,i) .lt. 0.) then
                     ddelta(l,i) = ddelta(l,i)/2.
                  else
                     ddelta(l,i) = ddelta(l,i)/1.1
                  end if
                  ddeltaN(l,i) = ddelta(l,i)
                  xidelta(l,i) = xideltaA(l,i)
               end do
            end do

c           PLAN
c           - - -
            do l=1,ni
               do k=1,3
                  if (xiplanA(l,k)*xiplan(l,k) .lt. 0.) then
                     dplan(l,k) = dplan(l,k)/2.
                  else
                      dplan(l,k) = dplan(l,k)/1.1
                  end if
                  dplanN(l,k) = dplan(l,k)
                  xiplan(l,k) = xiplanA(l,k)
               end do
            end do
            fp = fpA
            qi = qiA
            lis = lisA
            sommeXI = sommeXIA
         end if
      end do

c      write(*,*) "Nombre d'iterations excédé"


      return
      end

c     ==================================
c     SOUS-ROUTINE: inifunc pour le fond
c     ==================================

      subroutine inifunc_fond(f,a,bb,c,delta,plan)

      implicit none

      include 'param2.f'

      real*4 a(nbi,nbs),c(nbs,2),bb,f(nbr2,nbi),sig2(nbr1,nbi)
      real*4 b(nbi,3),beta(nbi),plan(nbi,3),tplan(nbr2,nbi)
      real*4 source(nbr2,nbi),moffat(nbr2,nbi),g(nbr1,nbi)
      real*4 Fsource(nbr2,nbi),Fmoffat(nbr2,nbi),Fssource(2*xy2,nbi)
      real*4 Fsmoffat(2*xy2,nbi),t1,t2,lambda(nbi),qi,lis
      real*4 moffatfixe(nbr2,nbi),sum3
      real*4 sourmof(nbr2),sourmof2(nbr2),ssourmof(2*xy2)
      real*4 ssourmof2(2*xy2),rr(nbr2),srr(2*xy2),delta(nbi,2)
      real*4 fp,frf(nbr2,nbi),sfrf(2*xy2),sum2
      real*4 sourmofbis(nbr1,nbi),tplanbis(nbr1,nbi)
      real*4 tmp(nbr2),sourmofdec(nbr2,nbi)
c     -------------
c     NORMALISATION
      real*4 somme(nbi)
c     ---------------
      integer i,ind,nxy1,n1,ns,j,k,centre,n2,nxy2,pas
      integer ind1,indice,l,ind2,ii,jj,ni,l2

      character*20 results

      common /moffat_fixe/ moffatfixe
      common /var_moffat/ b,beta
      common /gr1/ g,sig2
      common /moff/ source
      common /moff2/ moffat,tplan
      common /Fmoff/ Fsource,Fmoffat,Fssource,Fsmoffat
      common /moffsourg/ sourmofbis,tplanbis
      common /moffsourg2/ sourmofdec
      common /tailles/ n1,n2,ns,nxy1,nxy2,pas,ni
      common /minimum/ fp,qi,lis
c     -------------
c     NORMALISATION
      common /normalisation2/ somme
c     ---------------
      common /lissage/ rr,srr
      common /lissage2/ frf
      common /lissage3/ lambda


      lis = 0.
      sum2 = 0.
      fp = 0.
      qi = 0.
      do l=1,ni
         sum3 = 0.

c        CALCUL DU TERME DE LISSAGE
c        - - - - - - - - - - - - - - 
         do i=1,n2
            tmp(i) = f(i,l)
         end do
         call rlft2(tmp,sfrf,nxy2,nxy2,1)
         call produit(tmp,rr,sfrf,srr,nxy2)
         call rlft2(tmp,sfrf,nxy2,nxy2,-1)

         do i=1,n2
            frf(i,l) = f(i,l)-tmp(i)
            sum3 = sum3 + frf(i,l)**2
         end do

c        CALCUL DU FOND
c        - - - - - - - -
c        -------------
c        NORMALISATION
         somme(l) = 0.
c        ---------------
         centre = nxy2/2+1
         do j=1,nxy2
            jj = j+centre-1
            if (jj .gt. nxy2) jj = jj-nxy2
            do i=1,nxy2
               ii = i+centre-1
               if (ii .gt. nxy2) ii = ii-nxy2
               ind = i + (j-1)*nxy2
               ind2 = ii + (jj-1)*nxy2
               source(ind,l) = 0.
               moffat(ind2,l) = moffatfixe(ind,l) + f(ind,l)
c              -------------
c              NORMALISATION
               somme(l) = somme(l) + moffat(ind2,l)
c              ---------------
               tmp(ind2) = moffat(ind2,l)
            end do
         end do

c        CALCUL DES SOURCES
c        - - - - - - - - - -
         do k=1,ns
            do j=1,nxy2
               t2 = j-(c(k,2)-delta(l,2))
               do i=1,nxy2
                  t1 = i-(c(k,1)-delta(l,1))
                  ind = i + (j-1)*nxy2
                  source(ind,l) = source(ind,l) + 
     &                 a(l,k)*exp(-bb*(t1*t1+t2*t2))
               end do
            end do
         end do
         do j=1,nxy2
            do i=1,nxy2
               tplan((j-1)*nxy2+i,l) = plan(l,1)*i+plan(l,2)*j+plan(l,3)
            end do
         end do
         centre = nxy2/2+1

         do i=1,n2
c           -------------
c           NORMALISATION
            moffat(i,l) = moffat(i,l)/somme(l)
c           -------------
            sourmof(i) = moffat(i,l)
            sourmof2(i) = source(i,l)
         end do

         call rlft2(sourmof2,ssourmof2,nxy2,nxy2,1)
         call rlft2(sourmof,ssourmof,nxy2,nxy2,1)
         do i=1,n2
            Fsource(i,l) = sourmof2(i)
            Fmoffat(i,l) = sourmof(i)
         end do
         do i=1,2*nxy2
            Fssource(i,l) = ssourmof2(i)
            Fsmoffat(i,l) = ssourmof(i)
         end do

         call produit(sourmof,sourmof2,ssourmof,ssourmof2,nxy2)
         call rlft2(sourmof,ssourmof,nxy2,nxy2,-1)


         do j=1,nxy1
            do i=1,nxy1
               ind1 = nxy2*pas*(j-1)+pas*(i-1)
               indice = (j-1)*nxy1+i
               sourmofbis(indice,l) = 0.
               tplanbis(indice,l) = 0.
               do l2=1,pas
                  ind2 = (l2-1)*nxy2
                  do k=1,pas
                     sourmofbis(indice,l) = sourmofbis(indice,l) + 
     &                                    sourmof(ind1+k+ind2) 
                     sourmofdec(ind1+k+ind2,l) = sourmof(ind1+k+ind2) 
                     tplanbis(indice,l) = tplanbis(indice,l) + 
     &                                  tplan(ind1+k+ind2,l) 
                  end do
                end do
               sourmofbis(indice,l) = sourmofbis(indice,l)/real(pas**2)
               tplanbis(indice,l) = tplanbis(indice,l)/real(pas**2)
               qi = qi + sig2(indice,l)*((sourmofbis(indice,l) + 
     &                   tplanbis(indice,l)-g(indice,l))**2)
            end do
         end do

         lis = lis + sum3
         sum2 = sum2 + lambda(l)*sum3

      end do

      fp = qi + sum2

      return
      end


c     ================================
c     SOUS-ROUTINE: dfunc pour le fond
c     ================================

      subroutine dfunc_fond(f,a,bb,c,delta,plan)

      implicit none

      include 'param2.f'

      real*4 f(nbr2,nbi),plan(nbi,3)
      real*4 a(nbi,nbs),c(nbs,2),bb,b(nbi,3),beta(nbi)
      real*4 g(nbr1,nbi),sig2(nbr1,nbi),tamp
      real*4 tplanbis(nbr1,nbi)
      real*4 sourmofbis(nbr1,nbi),tmp(nbr2),stmp(2*xy2)
      real*4 tmp2(nbr2),stmp2(2*xy2),delta(nbi,2),tmpF(nbr2)
      real*4 stmpF(2*xy2),source(nbr2,nbi)
      real*4 Fsource(nbr2,nbi),Fmoffat(nbr2,nbi),Fssource(2*xy2,nbi)
      real*4 Fsmoffat(2*xy2,nbi),lambda(nbi)
      real*4 tab(nbr2,5),t1,t2,tmp3,cons,tmpbis
      real*4 rr(nbr2),srr(2*xy2),frf(nbr2,nbi)
      real*4 xia(nbi,nbs),xic(nbs,2),xiplan(nbi,3)
      real*4 xidelta(nbi,2),xi,terme2
      real*4 xifterme(nbr2,nbi),xiflissage(nbr2,nbi)
      real*4 sommeXI,sommeXI2,somme(nbi)
      real*4 tmp4(nbr2),stmp4(2*xy2),ttt(nbr2)
      character*20 results
      integer i,j,ind,n1,nxy1,ns,ii,jj,k,ind2,n2,nxy2,ii2
      integer pas,i2,l,k2,ibis,jbis,ind1,indice,centre,l2,condi2
      integer rayon,xy_carre,nb_carre,deb,fin,ni,condi,ind4

      common /gr1/ g,sig2
      common /var_moffat/ b,beta
      common /tailles/ n1,n2,ns,nxy1,nxy2,pas,ni
      common /lissage/ rr,srr
      common /lissage3/ lambda
      common /derivees_fond/ xia,xic,xiplan,xidelta
      common /derivees_extra/ xifterme,xiflissage
      common /sommedesXI/ sommeXI,sommeXI2
      common /Fmoff/ Fsource,Fmoffat,Fssource,Fsmoffat
      common /moffsourg/ sourmofbis,tplanbis
      common /lissage2/ frf
      common /carre/ rayon,xy_carre,nb_carre,deb,fin
      common /moff/ source
      common /surfit/ tmp4
      common /normalisation2/ somme

      do k=1,ns
         do l=1,ni
            xia(l,k) = 0.
         end do
         xic(k,1) = 0.
         xic(k,2) = 0.
      end do
      do l=1,ni
         do i=1,n2
            xifterme(i,l) = 0.
            xiflissage(i,l) = 0.
         end do
         do i=1,3
            xiplan(l,i) = 0.
         end do
         xidelta(l,1) = 0.
         xidelta(l,2) = 0.
      end do

      do i=1,5
         do j=1,n2
            tab(j,i) = 0.
         end do
      end do

      do l=1,ni
       
c     DERIVEE DES SOURCES
c     - - - - - - - - - - 
         do i=1,n2
            tmpF(i) = Fmoffat(i,l)
         end do
         do i=1,2*nxy2
             stmpF(i) = Fsmoffat(i,l)
         end do

         condi = (l-1)*(nb_carre+ns+3)+nb_carre

         do k=1,ns
            do j=1,nxy2
               t2 = j-(c(k,2)-delta(l,2))
               do i=1,nxy2
                  t1 = i-(c(k,1)-delta(l,1))
                  ind = i+(j-1)*nxy2
                  tmp3 = exp(-bb*(t1*t1+t2*t2))
                  tab(ind,1) = tmp3
                  tab(ind,2) = tmp3*2.*bb*t1
                  tab(ind,3) = tmp3*2.*bb*t2
                  tab(ind,4) = tab(ind,4) - tmp3*2.*bb*a(l,k)*t1
                  tab(ind,5) = tab(ind,5) - tmp3*2.*bb*a(l,k)*t2
               end do
            end do

            do i2=1,3
               do j=1,n2
                  tmp(j) = tab(j,i2)
               end do
               call rlft2(tmp,stmp,nxy2,nxy2,1)
               call produit(tmp,tmpF,stmp,stmpF,nxy2)
               call rlft2(tmp,stmp,nxy2,nxy2,-1)
  
               if (i2.eq.1) then
                  cons = 2.
               else if (i2.eq.2) then
                  cons = 2.*a(l,k)
               else if (i2.eq.3) then
                  cons = 2.*a(l,k)
               end if

               xi = 0.
               do j=1,nxy1
                  do i=1,nxy1
                     ind1 = nxy2*pas*(j-1)+pas*(i-1)
                     indice = (j-1)*nxy1+i
                     tmpbis = 0.
                     do l2=1,pas
                        ind2 = (l2-1)*nxy2
                        do k2=1,pas
                           tmpbis = tmpbis + tmp(ind1+k2+ind2)  
                        end do
                     end do
                     tmpbis = tmpbis/real(pas**2)
                     xi = xi + 
     &                 (cons*sig2(indice,l) * 
     &                 (sourmofbis(indice,l)+tplanbis(indice,l)
     &                  -g(indice,l))*tmpbis)
                  end do
               end do
               if (i2.eq.1) then
                  xia(l,k) = xi
               else if (i2.eq.2) then
                  xic(k,1) = xic(k,1) + xi
               else if (i2.eq.3) then
                  xic(k,2) = xic(k,2) + xi
               end if
            end do
         end do

c        DERIVEE DES DECALAGES
c        - - - - - - - - - - - -

         if (l .ne. 1) then
            do i2=4,5
               do j=1,n2
                  tmp(j) = tab(j,i2)
               end do
               call rlft2(tmp,stmp,nxy2,nxy2,1)
               call produit(tmp,tmpF,stmp,stmpF,nxy2)
               call rlft2(tmp,stmp,nxy2,nxy2,-1)

               do j=1,nxy1
                  do i=1,nxy1
                     ind1 = nxy2*pas*(j-1)+pas*(i-1)
                     indice = (j-1)*nxy1+i
                     tmpbis = 0.
                     do l2=1,pas
                        ind2 = (l2-1)*nxy2
                        do k2=1,pas
                           tmpbis = tmpbis + tmp(ind1+k2+ind2)  
                        end do
                     end do
                     tmpbis = tmpbis/real(pas**2)
                     xidelta(l,i2-3) = xidelta(l,i2-3) + 
     &                  (2.*sig2(indice,l) *
     &                  (sourmofbis(indice,l)+tplanbis(indice,l)
     &                  -g(indice,l))*tmpbis)

                  end do
               end do
            end do
         end if

c        DERIVEE DU FOND
c        - - - - - - - - 
         condi = condi+ns
         do j=1,nxy1
            jbis = (j-1)*pas+((pas+1)/2)
            do i=1,nxy1
               ibis = (i-1)*pas+((pas+1)/2)
               ind = i + (j-1)*nxy1
               tamp =  sig2(ind,l)*
     &                 (sourmofbis(ind,l)+tplanbis(ind,l)-g(ind,l))
               ind1 = nxy2*pas*(j-1)+pas*(i-1)
               do l2=1,pas
                  ind2 = (l2-1)*nxy2
                  do k=1,pas
                     tmp(ind1+k+ind2) = tamp
                     tmp4(ind1+k+ind2) = 2.*(sqrt(sig2(ind,l)))
                  end do
               end do

c              DERIVEE DU PLAN
c              - - - - - - - - 
               tamp = 2*tamp
               xiplan(l,1) = xiplan(l,1) + tamp*ibis
               xiplan(l,2) = xiplan(l,2) + tamp*jbis
               xiplan(l,3) = xiplan(l,3) + tamp
            end do
         end do

         centre = nxy2/2+1
         do j=1,nxy2
            jj = nxy2-j+1+centre
            if (jj .gt. nxy2) jj = jj-nxy2
            do i=1,nxy2
               ii = nxy2-i+1+centre
               if (ii .gt. nxy2) ii = ii-nxy2
               ind = i + (j-1)*nxy2
               ind2 = ii + (jj-1)*nxy2
               tmp2(ind) = source(ind2,l)/somme(l)
            end do
         end do

         call rlft2(tmp,stmp,nxy2,nxy2,1)
         call rlft2(tmp2,stmp2,nxy2,nxy2,1)
         call rlft2(tmp4,stmp4,nxy2,nxy2,1)
         call produit(tmp,tmp2,stmp,stmp2,nxy2)
         call produit(tmp4,tmp2,stmp4,stmp2,nxy2)
         call rlft2(tmp,stmp,nxy2,nxy2,-1)
         call rlft2(tmp4,stmp4,nxy2,nxy2,-1)
 
         do i=1,n2
            tmp2(i) = frf(i,l)
         end do

         call rlft2(tmp2,stmp2,nxy2,nxy2,1)
         call produit(tmp2,rr,stmp2,srr,nxy2)
         call rlft2(tmp2,stmp2,nxy2,nxy2,-1)

         sommeXI = 0.
         sommeXI2 = 0.
         do j=deb,fin
            jj = int((j-1)/pas)+1
            do i=deb,fin
               ii2 = int((i-1)/pas)+1
               ind = (j-1)*nxy2+i
               ind2 = (jj-1)*nxy1+ii2
               xifterme(ind,l) = 2.*tmp(ind)
               xiflissage(ind,l)=2.*lambda(l)*(frf(ind,l)-tmp2(ind))
               terme2 =  xifterme(ind,l) + xiflissage(ind,l)
               sommeXI = sommeXI + abs(terme2)
               sommeXI2 = sommeXI2 + terme2*terme2
               ttt(ind) = terme2
            end do
         end do
      end do


      return
      end


c     ========================================
c     SOUS-ROUTINE: decomposition pour le fond
c     ========================================

      subroutine decomposition_fond(init)

      implicit none

      include 'param2.f'

      real*4 a(nbi,nbs),bb,c(nbs,2),tmp(nbr2),moffatfixe(nbr2,nbi)
      real*4 b(nbi,3),beta(nbi),sourmofbis(nbr1,nbi),f(nbr2,nbi)
      real*4 plan(nbi,3),tplan(nbr2,nbi),delta(nbi,2)
      real*4 phi(nbr2,nbi),g(nbr1,nbi),sig2(nbr1,nbi)
      real*4 tplanbis(nbr1,nbi),tmp3(nbr2)
      real*4 source(nbr2,nbi),moffat(nbr2,nbi),tmp2(nbr1)
      real*4 sourmofdec(nbr2,nbi)
      real*8 somme
      integer i,n1,nxy1,n2,nxy2,pas,init,ni,taille,ii,jj,debut,fin
      integer ns,l,ll,j,j2,i2,half,centre
      character*20 results,name_moffat(nbi)
      character*1 minimum_moffat,lettre,lettre2,lettre3
      character*1 recompose
      character*8 mot

      common /gr1/ g,sig2
      common /gauss/ phi
      common /var_fond/ f
      common /var_moffat/ b,beta
      common /var_source/ a,bb,c,delta
      common /var_plan/ plan
      common /tailles/ n1,n2,ns,nxy1,nxy2,pas,ni
      common /moff/ source
      common /moff2/ moffat,tplan
      common /moffsourg/ sourmofbis,tplanbis
      common /moffsourg2/ sourmofdec
      common /moffat_fixe/ moffatfixe
      common /fichier_sortie/ minimum_moffat,name_moffat
      common /image_recomposee/ recompose

c      write(*,*) 'décomposition du fond'
      if (init.eq.1) then
         call inifunc_fond(f,a,bb,c,delta,plan)
         call dfunc_fond(f,a,bb,c,delta,plan)
      end if

      do l=1,ni
         lettre = char(48+int(l/100))
         ll = l - int(l/100)
         lettre2 = char(48+int(ll/10))
         lettre3 = char(48+mod(ll,10))
         mot = lettre // lettre2 // lettre3 // '.fits'

         do i=1,n2
            tmp(i) =  source(i,l)  
         end do
         results = 'source' // mot
         call makeima(results,nxy2,tmp)

         do i=1,n2
            tmp(i) =  tplan(i,l)  
         end do
         results = 'plan' // mot
         call makeima(results,nxy2,tmp)

c        CALCUL DE LA MOFFAT
c        - - - - - - - - - - 
c        -------------
c        NORMALISATION
         somme = 0.
c        -------------
         centre = nxy2/2+1
         do i=1,n2
            tmp(i) = moffatfixe(i,l) + f(i,l)
            tmp3(i) = f(i,l)
c          -------------
c          NORMALISATION
           somme = somme + moffatfixe(i,l) + f(i,l)
c          -------------
         end do
c        -------------
c        NORMALISATION
         do i=1,n2
            tmp(i) = tmp(i)/somme
         end do
c        -------------
         results = 'fond' // mot
         call makeima(results,nxy2,tmp3)
         results = 'moffond' // mot
         call makeima(results,nxy2,tmp)

         if ((recompose .eq. 'y') .and. (ns .ne. 1)) then
            debut = (nxy2/2+1) - nxy2/4
            fin = nxy2/2 + nxy2/4
            taille = int(nxy2/2)
c            write(*,*) 'DECOUPAGE DE S SUITE A LA RECONSTRUCTION'
         else 
            debut = 1
            fin = nxy2
            taille = nxy2
         end if

         half = int(taille/2.)
         jj=1
         somme = 0.
         do j=debut,fin
            ii=1
            j2 = jj+half
            if (j2 .gt. taille) j2 = j2-taille
            do i=debut,fin
               i2 = ii+half
               if (i2 .gt. taille) i2 = i2-taille
               tmp3((j2-1)*taille+i2) = tmp((j-1)*nxy2+i)
               somme = somme + tmp((j-1)*nxy2+i)
               ii=ii+1
            end do
            jj=jj+1
         end do
         do i=1,taille*taille
            tmp3(i) = tmp3(i)/somme
         end do
         results = 's' // mot
         call makeima(results,taille,tmp3)

         do i=1,n2
            tmp(i) = sourmofdec(i,l)+tplan(i,l)
         end do
         results = 'somme' // mot
         call makeima(results,nxy2,tmp)

         do i=1,n1
            tmp2(i) = (sourmofbis(i,l)+tplanbis(i,l)-g(i,l))*
     &                sqrt(sig2(i,l))
         end do
         results = 'residu' // mot
         call makeima(results,nxy1,tmp2)
      end do

c     ECRITURE DANS LE FICHIER DE SORTIE
c     - - - - - - - - - - - - - - - - - -


      if (minimum_moffat .eq. 'y') then
         write(2,'(A1)') 'y'
         do l=1,ni
             write(2,*) b(l,1),b(l,2),b(l,3),beta(l)
         end do
      else if (minimum_moffat .eq. 'n') then
         write(2,'(A1)') 'n'
         do l=1,ni
             write(2,*) b(l,1),b(l,2),b(l,3),beta(l)
         end do
      else if (minimum_moffat .eq. 'i') then
         write(2,'(A1)') 'i'
         do l=1,ni
            write(2,'(A20)') name_moffat(l)
         end do
      end if            
      write(2,'(A55)') 
     &        '-------------------------------------------------------'
      write(2,'(A55)') 
     &        '| Paramètres initiaux du plan (alpha beta gamma) * ni |'
      write(2,'(A55)') 
     &        '-------------------------------------------------------'
      do l=1,ni
         write(2,*) plan(l,1),plan(l,2),plan(l,3)
      end do
      write(2,'(A55)') 
     &        '-------------------------------------------------------'
      write(2,'(A55)') 
     &        '| Paramètres initiaux des décalages                   |'
      write(2,'(A55)') 
     &        '| ( deltaX deltaY ) * ni                              |'
      write(2,'(A55)') 
     &        '-------------------------------------------------------'
      do l=1,ni
         write(2,*) delta(l,1),delta(l,2)
      end do
      write(2,'(A55)') 
     &        '-------------------------------------------------------'
      write(2,'(A55)') 
     &        '| Paramètres initiaux des sources                     |'
      write(2,'(A55)') 
     &        '| a(1) ... a(ni) }                                    |'
      write(2,'(A55)') 
     &        '| cx cy          } * ns                               |'
      write(2,'(A55)') 
     &        '-------------------------------------------------------'
      do i=1,ns
         write(2,*) (a(l,i),l=1,ni)
         write(2,*) (c(i,1)+((real(pas)-1)/real(pas)))/pas,
     &              (c(i,2)+((real(pas)-1)/real(pas)))/pas
      end do

      return
      end

c     ==================================================================
c     ==================================================================
C       RRRRRR   OOOOO  U     U TTTTTTT I NN    N EEEEEEE
C       R     R O     O U     U    T    I N N   N E
C       RRRRRR  O     O U     U    T    I N  N  N EEEEE
C       R   R   O     O U     U    T    I N   N N E
C       R    R   OOOOO   UUUUU     T    I N    NN EEEEEEE
c     ==================================================================
C      ROUTINE
c     ==================================================================


c     ==================
c     SOUS-ROUTINE: mask
c     ==================

      subroutine mask()

      implicit none
      
      include 'param2.f'

      real*4 fond(nbr2),ma(nbr2),tmp(nbr2),f(nbr2,nbi)
      real*4 moffatfixe(nbr2,nbi)
      real*4 c1,c2,X0,d,xx,al
      real*4 lamb1,lamb2,eps
      real*4 t1,t2,somme
      integer n1,n2,nxy1,nxy2,pas,ind,ind2,i,j,ns,centre
      integer ni,l,ll,i2,j2,half
      character*20 results
      character*1 lettre,lettre2,lettre3
      character*8 mot

      common /tailles/ n1,n2,ns,nxy1,nxy2,pas,ni
      common /var_fond/ f
      common /moffat_fixe/ moffatfixe

      write(*,'(''Entrez le rayon de la zone à masquer: '',$)')
      read(*,*) X0
      eps = 0.4

      c1=nxy2/2.+1.
      c2=nxy2/2.+1.
      lamb2=1.E+06
      lamb1=1.
      al=log(lamb2/lamb1)

      do j=1,nxy2
         ind2 = (j-1)*nxy2
         t2 = (j-c2)*(j-c2)
         do i=1,nxy2
            ind = i+ind2  
            ma(ind) = 1.
            t1 = (i-c1)*(i-c1)
            d = sqrt(t1+t2)
            if (d .ge. X0) then
               ma(ind) = lamb2
            else if (d .le. X0) then
               ma(ind) = lamb1
            end if
            if (d.gt.((1.-eps)*X0).and.d.lt.((1.+eps)*X0)) then
               xx = (d/X0-1.)/eps
               ma(ind) = lamb1*exp(al*(0.5+0.75*xx-0.25*xx*xx*xx))
            endif
         end do
      end do
      results = 'mask.fits'
      call makeima(results,nxy2,ma)
    
      do l=1,ni
         lettre = char(48+int(l/100))
         ll = l - int(l/100)
         lettre2 = char(48+int(ll/10))
         lettre3 = char(48+mod(ll,10))
         mot = lettre // lettre2 // lettre3 // '.fits'

c        -------------
c        NORMALISATION
c         somme = 0.
c        -------------
         centre = nxy2/2+1
         do j=1,nxy2
            do i=1,nxy2
               ind = i + (j-1)*nxy2
               fond(ind) = f(ind,l)/ma(ind)
               tmp(ind) = moffatfixe(ind,l) + fond(ind)
c              -------------
c              NORMALISATION
c               somme = somme + tmp(ind)
c              -------------
            end do
         end do
c        -------------
c        NORMALISATION
c         do i=1,n2
c            tmp(i) = tmp(i)/somme
c         end do
c        -------------
         results = 'fond_mask' // mot
         call makeima(results,nxy2,fond)
         results = 'moffond_mask' // mot
         call makeima(results,nxy2,tmp)

         half = int(nxy2/2.)
         somme = 0.
         do j=1,nxy2
            j2 = j+half
            if (j2 .gt. nxy2) j2 = j2-nxy2
            do i=1,nxy2
               i2 = i+half
               if (i2 .gt. nxy2) i2 = i2-nxy2
               ma((j-1)*nxy2+i) = tmp((j2-1)*nxy2+i2)
               somme = somme + ma((j-1)*nxy2+i)
            end do
         end do
         results = 's_mask' // mot
         call makeima(results,nxy2,ma)

      end do

      return
      end 

c     ---------------------
c     SUBROUTINE: new fourrier
c     ---------------------

      subroutine rlft2(data,speq,nn1,nn2,isign)
 
      integer isign,nn1,nn2
      reaL*4 data(nn1*nn2)
      integer i1,i2,j1,j2,nn(2),i,ind1,ind2
      double precision theta,wi,wpi,wpr,wr,wtemp
      real*4 c1,c2,h1r,h1i,h2r,h2i
      real*4 speq(nn1*2)

      c1 = 0.5
      c2 = -0.5*isign
      theta = 6.28318530717959d0/dble(isign*nn2)
      wpr = -2.0d0*sin(0.5d0*theta)**2
      wpi = sin(theta)
      nn(1) = nn1/2
      nn(2) = nn2
      if (isign .eq. 1) then
         call fourn(data,nn(1),nn(2),2,isign)
        do i=1,nn1
            speq(i*2-1) = data((i-1)*nn1+1)
            speq(i*2) = data((i-1)*nn1+2)
        end do
      end if
      wr = 1.0d0
      wi = 0.0d0
      do i2=1,nn1/2+1,2
         j2 = nn1-i2+2
         do i1=1,nn2
            j1 = 1
            if (i1 .ne. 1) j1 = nn1-i1+2
            if (i2 .eq. 1) then
               h1r = c1*(data((i1-1)*nn2+1)+speq(j1*2-1))
               h1i = c1*(data((i1-1)*nn2+2)-speq(j1*2))
               h2i = c2*(data((i1-1)*nn2+1)-speq(j1*2-1))
               h2r = -c2*(data((i1-1)*nn2+2)+speq(j1*2))
               data((i1-1)*nn2+1) = h1r+h2r
               data((i1-1)*nn2+2) = h1i+h2i
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
         call fourn(data,nn(1),nn(2),2,isign)
      end if

      return
      end  

c     SOUS-ROUTINE: fourrier
c     ---------------------

      subroutine fourn(data,n1,n2,ndim,isign)

      integer n1,n2,isign,ndim
      double precision wr,wi,wpr,wpi,wtemp,theta
      real*4 data(n1*n2*2),tempi,tempr
      integer i1,i2,i2rev,i3,i3rev,ibit,idim,ifp1,ifp2,ip1,ip2,ip3
      integer k1,k2,n,nprev,nrem,ntot,nn(2)

      nn(1) = n1
      nn(2) = n2
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

c     SOUS-ROUTINE: produit
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


c     SOUS-ROUTINE: openima
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

c     SOUS-ROUTINE: makeima
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

c     SOUS-ROUTINE: printerror
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

c     SOUS-ROUTINE: printerror
c     ------------------------

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

