c     PROGRAMME DE MINIMISATION
c     -------------------------

c     DECLARATION DES VARIABLES
c     -------------------------

      implicit none

      include 'param_psf.f'

      integer i,j,iter,n1,n2,m,ind,j2,i2
      integer nax1,nax2,nxy1,nxy2
      
      real*4 bb,mof(nbr2),fwhm,som,t2,t1,tmp(nbr2),half
      real*4 lambda,pas,x0,al,tab(nbr1),tab2(nbr1)
      real*4 g(nbg,nbr1),sig2(nbg,nbr1),p(nbr2)
      real*4 r(nbr2),sr(2*xy2),phi(nbg,nbr2)

      character*20 ima_name
      character*20 moffat
      character*70 entete
      character*1 lettre1,lettre2,question
      character*7 fin
      character*42 ligne

      common /gr1/ g,sig2
      common /param/ nxy1,nxy2,pas
      common /smooth/ lambda,x0,al
      common /cmoffat/ mof
      common /param2/ bb
      common /tailles/ n1,n2,m
      common /var/ p
      common /gauss/ r,sr,phi

      open(unit=1,file='psfmof.txt')
      do i=1,3
         read(1,'(A70)') entete
      end do 
      read(1,'(A42,I4)') ligne,m
      read(1,'(A70)') entete
      read(1,'(A42,F16.10)') ligne,fwhm 
      if (fwhm .ge. 2.) then
         bb = 4*log(2.)/(fwhm*fwhm)
      else
         write(*,*) 'FWHM < 2 --> error sampling'
         stop
      end if     
      close(unit=1)

c     DEBUT DE PROGRAMME
c     ------------------

      n1 = nbr1
      n2 = nbr2
      nxy1 = xy1
      nxy2 = xy2
      pas = int(nxy2/nxy1)

      moffat='mofc.fits'

c     -------------------------------------------------------
c     Les sigmas sont deja au carre et divises par a au carre
c     -------------------------------------------------------

      do i=1,m
         lettre1 = char(48+int(i/10))
         lettre2 = char(48+mod(i,10))
         fin = lettre1 // lettre2 // '.fits'
         ima_name = 'difc' // fin
         call openima(ima_name,nax1,nax2,tab)
         ima_name = 'sigc' // fin
         call openima(ima_name,nax1,nax2,tab2)
         do j=1,nbr1
            g(i,j) = tab(j)
            sig2(i,j) = tab2(j)
         end do
      end do

      call openima(moffat,nax1,nax2,mof)

c     CREATION OF TABLE R:
c     - - - - - - - - - - 
      som = 0.
      do j=1,nxy2
         t2 = j-(nxy2/2+1)
         do i=1,nxy2
            t1 = i-(nxy2/2+1)
            ind = i+(j-1)*nxy2
            tmp(ind) = exp(-bb*(t1*t1+t2*t2))
            som = som + tmp(ind)
         end do
      end do

      half = int(nxy2/2.)

      do j=1,nxy2
         j2 = j+half
         if (j2 .gt. nxy2) j2 = j2-nxy2
         do i=1,nxy2
            i2 = i+half
            if (i2 .gt. nxy2) i2 = i2-nxy2
            r((j-1)*nxy2+i) = tmp((j2-1)*nxy2+i2)/som
         end do
      end do
           
      call rlft2(r,sr,nxy2,1)

c     CALCUL DU FOND DE LA PSF
c      - - - - - - - - - - - -

      open(unit=2,file='lambda.txt')
      read(2,*) lambda
      read(2,*) al
      read(2,*) x0
      close(2)

      al=log(al/lambda)
                  
      call gradient(1.E-08,iter)
      call decomposition()
      call mask()

      end


c     ----------------------
c     SOUS-ROUTINE: gradient
c     ----------------------

      subroutine gradient(ftol,iter)

      include 'param_psf.f'

      parameter (itmax=500,eps=1.E-10)

      real*4 gr(nbr2),h(nbr2),xi(nbr2),p(nbr2)
      real*4 fp,qi,fp2,qi2

      common /var/ p
      common /tailles/ n1,n2,m
      common /minimum/ fp,qi
      common /derivees/ xi

      call inifunc(p)
      call dfunc()

      do j=1,n2
         gr(j) = -xi(j)
         h(j) = gr(j)
         xi(j) = h(j)
      end do

      do its=1,itmax
         write(*,*) its,'   min: ',fp,'   qi: ',qi
         iter = its
         fp2 = fp
         qi2 = qi
         call linmin(fret)
         if (2.*abs(fret-fp2).le.ftol*(abs(fret)+abs(fp2)+ eps)) goto 1
         call inifunc(p)
         call dfunc()
         gg = 0.
         dgg = 0.
         do j=1,n2
            gg = gg + gr(j)**2
            dgg = dgg + (xi(j) + gr(j))*xi(j)
         end do
         if (gg .eq. 0.) goto1
         gam = dgg/gg
         do j=1,n2
            gr(j) = -xi(j)
            h(j) = gr(j) + gam*h(j)
            xi(j) = h(j)
         end do
   
      end do
      write(*,*) "nombre d'iteration excede"

   1  call chi2mod(fp2,qi2)

      return
      end

c     ---------------------
c     SOUS-ROUTINE: inifunc
c     ---------------------

      subroutine inifunc(p)

      include 'param_psf.f'

      real*4 r(nbr2),p(nbr2),phi(nbg,nbr2)
      real*4 rmf(nbr2),rmfbis(nbr1)
      real*4 g(nbg,nbr1),sig2(nbg,nbr1),lambda,x0,al
      real*4 srmf(2*xy2),sr(2*xy2)
      integer i,ind,ii,jj,ind2,nxy1,nxy2

      common /gr1/ g,sig2
      common /param/ nxy1,nxy2,pas
      common /gauss/ r,sr,phi
      common /moff/ rmfbis
      common /moff2/ rmf
      common /tailles/ n1,n2,m
      common /minimum/ fp,qi
      common /smooth/ lambda,x0,al

      do j=1,nxy2
         ind2 = (j-1)*nxy2
         do i=1,nxy2
            ind = i + ind2
            rmf(ind) = p(ind)
         end do
      end do

      call rlft2(rmf,srmf,xy2,1)
      call produit(rmf,r,srmf,sr,xy2)
      call rlft2(rmf,srmf,xy2,-1)

      do j=1,nxy1
         do i=1,nxy1
            ind1 = nxy2*pas*(j-1)+pas*(i-1)
            indice = (j-1)*nxy1+i
            rmfbis(indice) = 0.
            do l=1,pas
               ind2 = (l-1)*nxy2
               do k2=1,pas
                  rmfbis(indice) = rmfbis(indice) + 
     &                             rmf(ind1+k2+ind2)
               end do
            end do
            rmfbis(indice) = rmfbis(indice)/real(pas**2)
         end do
      end do

      qi = 0.
      do k=1,m
         do i=1,n1
            qi = qi +
     &      ((rmfbis(i)-g(k,i))**2)/sig2(k,i)  
         end do
      end do

      c1=nxy2/2.+1.
      eps=0.5

      somme = 0.
      do i=1,n2
         ii=i/nxy2+1
         jj=i-nxy2*(ii-1)
         d2=sqrt((ii-c1)**2+(jj-c1)**2)
         fact=1.
         if(d2.ge.((1.+eps)*x0)) fact=exp(al)
         if(d2.gt.((1.-eps)*x0).and.d2.lt.((1.+eps)*x0)) then
           xx=(d2/x0-1.)/eps
           fact=exp(al*(0.5+0.75*xx-0.25*xx*xx*xx))
         endif
         somme = somme + fact*lambda*((p(i)-rmf(i))**2)
      end do

      fp = qi + somme

      return
      end

c     -------------------
c     SOUS-ROUTINE: dfunc
c     -------------------

      subroutine dfunc()

      include 'param_psf.f'

      real*4 xi(nbr2),r(nbr2),rmf(nbr2)
      real*4 p(nbr2),lambda,movex
      real*4 vect1(nbr1),vect2(nbr1)
      real*4 g(nbg,nbr1),sig2(nbg,nbr1),rmfbis(nbr1)
      real*4 phi(nbg,nbr2),tmp(nbr1),sr(2*xy2)
      real*4 tmp2(nbr2),stmp2(2*xy2)
      integer i,j,ind2,nxy1,nxy2

      common /gr1/ g,sig2
      common /param/ nxy1,nxy2,pas
      common /gauss/ r,sr,phi
      common /moff/ rmfbis
      common /moff2/ rmf
      common /smooth/ lambda,x0,al
      common /var/ p
      common /tailles/ n1,n2,m
      common /derivees/ xi

      c1=nxy2/2.+1.
      eps=0.5
    
        do i=1,n2
           tmp2(i)=p(i)-rmf(i)
        end do

        call rlft2(tmp2,stmp2,xy2,1)
        call produit(tmp2,r,stmp2,sr,xy2)
        call rlft2(tmp2,stmp2,xy2,-1)

       do i=1,n2
         ii=i/nxy2+1
         jj=i-nxy2*(ii-1)
         d2=sqrt((ii-c1)**2+(jj-c1)**2)
         fact=1.
         if(d2.ge.((1.+eps)*x0)) fact=exp(al)
         if(d2.gt.((1.-eps)*x0).and.d2.lt.((1.+eps)*x0)) then
           xx=(d2/x0-1.)/eps
           fact=exp(al*(0.5+0.75*xx-0.25*xx*xx*xx))
         endif
         xi(i) = 2.*fact*lambda*(p(i)-rmf(i)-tmp2(i))
       end do

       do k=1,m

        do i=1,n1
           vect1(i) = rmfbis(i)-g(k,i)
        end do
        movex=nxy1/2.+1.

        do j=1,n1
           tmp(j) = sig2(k,j)
        end do
        call centrage(vect1,vect2,movex,movex,n1)
        call centrage(tmp,vect1,movex,movex,n1)

        do j=1,nxy1
           do i=1,nxy1
              ind1 = nxy2*pas*(j-1)+pas*(i-1)
              indice = (j-1)*nxy1+i
              do l=1,pas
                 ind2 = (l-1)*nxy2
                 do kk=1,pas
                   tmp2(ind1+kk+ind2) = vect2(indice)
     &                                  /vect1(indice) 
                 end do
              end do
           end do
        end do

        call rlft2(tmp2,stmp2,xy2,1)
        call produit(tmp2,r,stmp2,sr,xy2)
        call rlft2(tmp2,stmp2,xy2,-1)
        do i=1,n2
           xi(i) = xi(i) + 2.*tmp2(i)
        end do

      enddo

      return
      end

c     --------------------
c     SOUS-ROUTINE: linmin
c     --------------------

      subroutine linmin(fret)

      include 'param_psf.f'      

      parameter(epsi=1.E-15)

      real*4 p(nbr2),xi(nbr2)
      real*4 rap(nbr2),raptol(nbr2),tol,max

      common /var/ p
      common /derivees/ xi
      common /tailles/ n1,n2,m

      max = 0.
      tol=1./epsi
      do i=1,n2
         rap(i)=abs(xi(i)/0.1)
         if(abs(xi(i)).gt.epsi) then
            raptol(i) = abs(0.001/xi(i))
         else
            raptol(i) = 1./epsi
         endif
         if (rap(i) .gt. max) then
            max = rap(i)
         end if
         if(raptol(i).lt.tol) then
            tol = raptol(i)
            im=i
         end if
      end do
 
      if (max .gt. 0.5) then
         xx = 0.5/max
      else
         xx = 1.
      end if

      ax = 0.
      bx = 2.*xx

      fret = recherche(ax,xx,bx,tol,xmin)
      do i=1,n2
         xi(i) = xmin*xi(i)
         p(i) = p(i) + xi(i)
      end do

      write(*,*) '---------------------------------------'

      return
      end

c     ---------------
c     FONCTION: f1dim
c     ---------------

      function f1dim(x)

      include 'param_psf.f'

      real*4 xt(nbr2),p(nbr2),xi(nbr2)

      common /tailles/ n1,n2,m
      common /var/ p
      common /derivees/ xi
      common /minimum/ fp,qi

      do i=1,n2
         xt(i) = p(i)+x*xi(i)
      end do

      call inifunc(xt)
      f1dim = fp

      return
      end

c     -------------------
c     FONCTION: recherche
c     -------------------

      function recherche(ax,bx,cx,tol,xmin)

      parameter (gold=1.618034,glimit=100.,tiny=1.E-20)
      parameter (itmax=300,cgold=0.381966,zeps=1.0E-15)

      fa = f1dim(ax)
      fb = f1dim(bx)
      if (fb .gt. fa) then
         dum = ax
         ax = bx
         bx = dum
         dum = fb
         fb = fa
         fa = dum
      end if
      cx = bx+gold*(bx-ax)
      fc = f1dim(cx)
10    if (fb .ge. fc) then
         r = (bx-ax)*(fb-fc)
         q = (bx-cx)*(fb-fa)
         u = bx-((bx-cx)*q-(bx-ax)*r)/(2.*sign(max(abs(q-r),tiny),q-r))
         ulim = bx + glimit*(cx-bx)
         if ((bx-u)*(u-cx) .gt. 0.) then
            fu = f1dim(u)
            if (fu .lt. fc) then
               ax = bx
               fa = fb
               bx = u
               fb = fu
               goto 40
            else if (fu .gt. fb) then
               cx = u
               fc = fu
               goto 40
            end if
            u = cx+gold*(cx-bx)
            fu = f1dim(u)
         else if ((cx-u)*(u-ulim) .gt. 0.) then
            fu = f1dim(u)
            if (fu .lt. fc) then
               bx = cx
               cx = u
               u = cx+gold*(cx-bx)
               fb = fc
               fc = fu
               fu = f1dim(u)
            end if
         else if ((u-ulim)*(ulim-cx) .ge. 0.) then
            u = ulim
            fu = f1dim(u)
         else
            u = cx+gold*(cx-bx)
            fu = f1dim(u)
         end if
         ax = bx
         bx = cx
         cx = u
         fa = fb
         fb = fc
         fc = fu
         goto 10
      end if

40    a = min(ax,cx)
      b = max(ax,cx)
      v = bx
      w = v
      x = v
      e = 0.
      fx = fb
      fv = fx
      fw = fx
      do iter=1,itmax
         xm = 0.5*(a+b)
         tol1 = 0.001*abs(x)
         if (tol1.lt.tol) then
           tol1 = tol
         endif
         tol2 = 2.*tol1
         if (abs(x-xm) .le. (tol2-.5*(b-a))) then
            goto 22
         endif   
         if (abs(e) .gt. tol1) then
            r=(x-w)*(fx-fv)
            q=(x-v)*(fx-fw)
            p=(x-v)*q-(x-w)*r
            q=2.*(q-r)
            if(q.gt.0.) p = -p
            q=abs(q)
            etemp=e
            e = d
            if (abs(p).ge.abs(0.5*q*etemp).or.p.le.q*(a-x).or.
     *        p.ge.q*(b-x)) goto 20
            d=p/q
            u = x+d
            if (u-a .lt. tol2 .or. b-u .lt. tol2) d=sign(tol1,xm-x)
            goto 21
         end if
20       if (x.ge.xm) then
            e = a-x
         else
            e = b-x
         end if
         d = cgold*e
21       if (abs(d) .ge. tol1) then
            u = x+d
         else
            u = x+sign(tol1,d)   
         end if
         fu = f1dim(u)
         if (fu .le. fx) then
            if ( u .ge. x) then
               a = x
            else
               b = x
            end if
            v = w
            fv = fw
            w = x
            fw = fx
            x = u
            fx = fu
         else
            if (u .lt. x) then
               a = u
            else
               b = u
            end if
            if (fu .le. fw .or. w .eq. x) then
               v = w
               fv = fw
               w = u
               fw = fu
            else if (fu .le. fv .or. v .eq. x .or. v .eq. w) then
               v = u
               fv = fu
            end if
         end if
      end do
      print*,'nombre iteration depasse.'
22    xmin = x
      recherche = fx
  
      return
      end


c     ---------------------
c     SUBROUTINE: new fourier
c     ---------------------

      subroutine rlft2(data,speq,nn1,isign)
 
      integer isign,nn1
      reaL*4 data(nn1*nn1)
      integer i1,i2,j1,j2,nn(2),i,ind1,ind2
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
c     SOUS-ROUTINE: fourier
c     ---------------------

      subroutine fourn(data,nn,nb,ndim,isign)

      integer nn(ndim),isign,ndim
      double precision wr,wi,wpr,wpi,wtemp,theta
      real*4 data(nb*2),tempi,tempr
      integer i1,i2,i2rev,i3,i3rev,ibit,idim,ifp1,ifp2,ip1,ip2,ip3
      integer k1,k2,n,nprev,nrem,ntot,nb

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

c     ---------------------------
c     SOUS-ROUTINE: decomposition
c     ---------------------------

      subroutine decomposition()

c      implicit none

      include 'param_psf.f'

      real*4 pp(nbr2),p(nbr2),g(nbg,nbr1),sig2(nbg,nbr1)
      real*4 pp2(nbr2),tmp(nbr1),pp3(nbr2)
      real*4 r(nbr2),mof(nbr2)
      real*4 movex,movey,phi(nbg,nbr2),spp2(2*xy2),sr(2*xy2)
      integer i,m,indice,ind1,ind2,k,ii,j,nxy1,nxy2
      character*1 lettre1,lettre2
      character*7 fin
      character*20 results,resultat

      common /param/ nxy1,nxy2,pas
      common /gauss/ r,sr,phi
      common /cmoffat/ mof
      common /gr1/ g,sig2
      common /tailles/ n1,n2,m
      common /var/ p
      common /masque/ pp

      if(pas.eq.2.) then
         movex=sqrt(real(nbr2))/2.
         movey=sqrt(real(nbr2))/2.
         call centrage2(p,pp,movex,movey,n2)
         do i=1,n2
            pp2(i) = pp(i)
         end do         
      endif

      if (pas.eq.1.) then
      do i=1,n2
         pp(i)=p(i)
         pp2(i) = pp(i)
      end do
      endif
   
      call rlft2(pp2,spp2,xy2,1)
      call produit(pp2,r,spp2,sr,xy2)
      call rlft2(pp2,spp2,xy2,-1)

      resultat = 'psfr.fits'
      call makeima(resultat,nxy2,pp2)

      do ii=1,m
         lettre1 = char(48+int(ii/10))
         lettre2 = char(48+mod(ii,10))
         fin = lettre1 // lettre2 // '.fits'
         do j=1,nxy1
            do i=1,nxy1
               ind1 = nxy2*pas*(j-1)+pas*(i-1)
               indice = (j-1)*nxy1+i
               tamp = 0.
               do l=1,pas
                  ind2 = (l-1)*nxy2
                  do k=1,pas
                    tamp = tamp + pp2(ind1+k+ind2)
                  end do
               end do
               tamp = tamp/(pas*pas)
               tmp(indice) = (tamp -g(ii,indice))/
     &                      sqrt(sig2(ii,indice))
            end do
         end do
         results = ' '
         results = 'xixi' // fin
         call makeima(results,nxy1,tmp)
      end do

      som = 0.
      do i=1,n2
         pp2(i) = pp(i) + mof(i)
         som = som + pp2(i)
      end do

      half = int(nxy2/2.)
      do j=1,nxy2
         j2 = j+half
         if (j2 .gt. nxy2) j2 = j2-nxy2
         do i=1,nxy2
            i2 = i+half
            if (i2 .gt. nxy2) i2 = i2-nxy2
            pp3((j-1)*nxy2+i) = pp2((j2-1)*nxy2+i2)/som
         end do
      end do
      resultat = 's.fits'
      call makeima(resultat,nxy2,pp3)

      call rlft2(pp2,spp2,xy2,1)
      call produit(pp2,r,spp2,sr,xy2)
      call rlft2(pp2,spp2,xy2,-1)

      resultat = 't.fits'
      call makeima(resultat,nxy2,pp2)

      resultat = 'psff.fits'
      call makeima(resultat,nxy2,pp)

      return
      end

c     ------------------
c     SOUS-ROUTINE: mask
c     ------------------
      subroutine mask()

      implicit none
      
      include 'param_psf.f'

      real*4 mof(nbr2),pp(nbr2),psffond(nbr2),ma(nbr2)
      real*4 c1,c2,X0,d,xx,al
      real*4 lamb1,lamb2,eps,half
      real*4 norm,t1,t2
      integer n1,n2,m,nxy1,nxy2,pas,ind,ind2,i,j,j2,i2
      character*20 resultat
     
      common /cmoffat/ mof
      common /masque/ pp      
      common /tailles/ n1,n2,m
      common /param/ nxy1,nxy2,pas

      open(unit=3,file='lambda.txt')
      read(3,*) x0
      read(3,*) x0
      read(3,*) x0
      close(3)
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
            psffond(ind)=pp(ind)/ma(ind)
         end do
      end do
      resultat = 'mask.fits'
      call makeima(resultat,nxy2,ma)
    
      norm=0.
      do j=1,nxy2
         do i=1,nxy2
         ind=i+(j-1)*nxy2   
         psffond(ind) = mof(ind) + psffond(ind)
         norm = norm + psffond(ind)
         end do
      end do

      half = int(nxy2/2.)
      do j=1,nxy2
         j2 = j+half
         if (j2 .gt. nxy2) j2 = j2-nxy2
         do i=1,nxy2
            i2 = i+half
            if (i2 .gt. nxy2) i2 = i2-nxy2
            ma((j-1)*nxy2+i) = psffond((j2-1)*nxy2+i2)/norm
         end do
      end do
     
      resultat = 's.fits'
      call makeima(resultat,nxy2,ma)

      return
      end 

c     ----------------------
c     SOUS_ROUTINE: centrage
c     ----------------------

      subroutine centrage(t,tt,c1,c2,n)

      include 'param_psf.f'

      real*4 tt(nbr1),t(nbr1),ttt((xy1+2)**2),c1,c2
      real*4 x1(3),x2(3),y1(3,3),ytt,xtt,tamp(nbr1),pas
      integer nxy1,nxy2

      common /param/ nxy1,nxy2,pas

      ttt(1)= t(n)
      ttt(nxy1+2) = t(1+(nxy1-1)*nxy1)
      ttt(1+(nxy1+1)*(nxy1+2)) = t(nxy1)
      ttt((nxy1+2)*(nxy1+2)) = t(1)

      do i=1,nxy1
         ttt(i+1) = t(i+(nxy1-1)*nxy1)
         ttt((i+1)+(nxy1+1)*(nxy1+2)) = t(i)
         ttt(1+i*(nxy1+2)) = t(i*nxy1)
         ttt(nxy1+2+i*(nxy1+2)) = t(1+(i-1)*nxy1)
      end do

      do j=2,nxy1+1
         do i=2,nxy1+1
            ttt(i+(j-1)*(nxy1+2)) = t((i-1)+(j-2)*nxy1)
         end do
      end do

      debut = real(-((nxy1+2)/2.))
      do i2=2,nxy1+1
         ytt = debut+c2+i2-1
         deby = nint(ytt)
         do i1=2,nxy1+1
            xtt = debut+c1+i1-1
            debx = nint(xtt)
            do j=1,3
               x1(j) = (j-2)+xtt
               x2(j) = (j-2)+ytt
               indx = (j-2)+i1
               do k=1,3
                  indy = (k-2)+i2
                  y1(j,k) = ttt(indx+(indy-1)*(nxy1+2))
               end do
            end do
            call polin2(x1,x2,y1,real(debx),real(deby),y,dy)
            tt(i1-1+(i2-2)*nxy1) = y
         end do
      end do

      difx = nxy1/2.+1-nint(c1)
      dify = nxy1/2.+1-nint(c2)

      if (difx .gt. 0) then
         do i=1,difx
            do j=1,nxy1
               tamp(i-difx+nxy1+(j-1)*nxy1) = tt(i+(j-1)*nxy1) 
            end do
         end do
         do i=difx+1,nxy1
            do j=1,nxy1
               tamp(i-difx+(j-1)*nxy1) = tt(i+(j-1)*nxy1)
            end do
         end do
      else if (difx .lt. 0) then
         do i=1,nxy1+difx
            do j=1,nxy1
               tamp(i-difx+(j-1)*nxy1) = tt(i+(j-1)*nxy1) 
            end do
         end do
         do i=nxy1+difx+1,nxy1
            do j=1,nxy1
               tamp(i-difx-nxy1+(j-1)*nxy1) = tt(i+(j-1)*nxy1)
            end do
         end do
      end if

      if (dify .gt. 0.) then
         do j=1,dify
            do i=1,nxy1
               tt(i+(j-dify+nxy1-1)*nxy1) = tamp(i+(j-1)*nxy1) 
            end do
         end do
         do j=dify+1,nxy1
            do i=1,nxy1
               tt(i+(j-dify-1)*nxy1) = tamp(i+(j-1)*nxy1)
            end do
         end do
      else if (dify .lt. 0.) then
         do j=1,nxy1+dify
            do i=1,nxy1
               tt(i+(j-dify-1)*nxy1) = tamp(i+(j-1)*nxy1) 
            end do
         end do
         do j=nxy1+dify+1,nxy1
            do i=1,nxy1
               tt(i+(j-dify-nxy1-1)*nxy1) = tamp(i+(j-1)*nxy1)
            end do
         end do
      end if

      return
      end

c     -----------------------
c     SOUS_ROUTINE: centrage2
c     -----------------------

      subroutine centrage2(t,tt,c1,c2,n)

      include 'param_psf.f'

      real*4 tt(nbr2),t(nbr2),ttt((xy2+2)**2),c1,c2
      real*4 x1(3),x2(3),y1(3,3),ytt,xtt,tamp(nbr2),pas
      integer nxy1,nxy2

      common /param/ nxy1,nxy2,pas

      ttt(1)= t(n)
      ttt(nxy2+2) = t(1+(nxy2-1)*nxy2)
      ttt(1+(nxy2+1)*(nxy2+2)) = t(nxy2)
      ttt((nxy2+2)*(nxy2+2)) = t(1)

      do i=1,nxy2
         ttt(i+1) = t(i+(nxy2-1)*nxy2)
         ttt((i+1)+(nxy2+1)*(nxy2+2)) = t(i)
         ttt(1+i*(nxy2+2)) = t(i*nxy2)
         ttt(nxy2+2+i*(nxy2+2)) = t(1+(i-1)*nxy2)
      end do

      do j=2,nxy2+1
         do i=2,nxy2+1
            ttt(i+(j-1)*(nxy2+2)) = t((i-1)+(j-2)*nxy2)
         end do
      end do

      debut = real(-((nxy2+2)/2.))
      do i2=2,nxy2+1
         ytt = debut+c2+i2-1
         deby = nint(ytt)
         do i1=2,nxy2+1
            xtt = debut+c1+i1-1
            debx = nint(xtt)
            do j=1,3
               x1(j) = (j-2)+xtt
               x2(j) = (j-2)+ytt
               indx = (j-2)+i1
               do k=1,3
                  indy = (k-2)+i2
                  y1(j,k) = ttt(indx+(indy-1)*(nxy2+2))
               end do
            end do
            call polin2(x1,x2,y1,real(debx),real(deby),y,dy)
            tt(i1-1+(i2-2)*nxy2) = y
         end do
      end do

      difx = nxy2/2.+1-nint(c1)
      dify = nxy2/2.+1-nint(c2)

      if (difx .gt. 0) then
         do i=1,difx
            do j=1,nxy2
               tamp(i-difx+nxy2+(j-1)*nxy2) = tt(i+(j-1)*nxy2) 
            end do
         end do
         do i=difx+1,nxy2
            do j=1,nxy2
               tamp(i-difx+(j-1)*nxy2) = tt(i+(j-1)*nxy2)
            end do
         end do
      else if (difx .lt. 0) then
         do i=1,nxy2+difx
            do j=1,nxy2
               tamp(i-difx+(j-1)*nxy2) = tt(i+(j-1)*nxy2) 
            end do
         end do
         do i=nxy2+difx+1,nxy2
            do j=1,nxy2
               tamp(i-difx-nxy2+(j-1)*nxy2) = tt(i+(j-1)*nxy2)
            end do
         end do
      end if

      if (dify .gt. 0.) then
         do j=1,dify
            do i=1,nxy2
               tt(i+(j-dify+nxy2-1)*nxy2) = tamp(i+(j-1)*nxy2) 
            end do
         end do
         do j=dify+1,nxy2
            do i=1,nxy2
               tt(i+(j-dify-1)*nxy2) = tamp(i+(j-1)*nxy2)
            end do
         end do
      else if (dify .lt. 0.) then
         do j=1,nxy2+dify
            do i=1,nxy2
               tt(i+(j-dify-1)*nxy2) = tamp(i+(j-1)*nxy2) 
            end do
         end do
         do j=nxy2+dify+1,nxy2
            do i=1,nxy2
               tt(i+(j-dify-nxy2-1)*nxy2) = tamp(i+(j-1)*nxy2)
            end do
         end do
      end if

      return
      end

c     --------------------
c     SOUS-ROUTINE: polin2
c     --------------------

      subroutine polin2(x1a,x2a,ya,x1,x2,y,dy)

      real*4 dy,x1,x2,y,x1a(3),x2a(3),ya(3,3)
      real*4 ymtmp(3),yntmp(3)
      integer j,k

      do j=1,3
         do k=1,3
            yntmp(k) = ya(j,k)
         end do
         call polint(x2a,yntmp,x2,ymtmp(j),dy)
      end do
      call polint(x1a,ymtmp,x1,y,dy)

      return
      end

c     --------------------
c     SOUS-ROUTINE: polin
c     -------------------

      subroutine polint(xa,ya,x,y,dy)
      
      real*4 dy,x,y,xa(3),ya(3)
      real*4 den,dif,dift,ho,hp,w,c(3),d(3)
      integer i,m,ns

      ns = 1
      dif = abs(x-xa(1))
      do i=1,3
         dift = abs(x-xa(i))
         if (dift .lt.dif) then
            ns = i
            dif = dift
         end if
         c(i) = ya(i)
         d(i) = ya(i)
      end do
      y = ya(ns)
      ns = ns-1
      do m=1,2
         do i=1,3-m
            ho = xa(i)-x
            hp = xa(i+m)-x
            w = c(i+1)-d(i)
            den = ho-hp
            if (den .eq. 0.) pause 'failure in polint'
            den = w/den
            d(i) = hp*den
            c(i) = ho*den
         end do
         if (2*ns .lt. 3-m) then
            dy = c(ns+1) 
         else 
            dy = d(ns)
            ns = ns-1
         end if
         y = y+dy
      end do

      return
      end

c     ---------------------
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

c     ---------------------
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

c     ------------------------
c     SOUS-ROUTINE: printerror
c     ------------------------

      subroutine printerror(status)


      integer status
      character errtext*30,errmessage*20

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

c     ------------------------
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

c     SOUS-ROUTINE: chi2mod
c     ---------------------

      subroutine chi2mod(min,sum1)

      include 'param_psf.f'

      real*4 min,sum1,lambda,somme,pas
      real*4 p(nbr2),mof(nbr2),mofbis(nbr1)
      real*4 g(nbg,nbr1),sig2(nbg,nbr1),rmfbis(nbr1)
      integer i,nxy1,nxy2

      common /gr1/ g,sig2
      common /moff/ rmfbis
      common /smooth/ lambda,x0,al
      common /cmoffat/ mof
      common /param/ nxy1,nxy2,pas
      common /var/ p
      common /tailles/ n1,n2,m

      do j=1,nxy1
         do i=1,nxy1
            ind1 = nxy2*pas*(j-1)+pas*(i-1)
            indice = (j-1)*nxy1+i
            mofbis(indice) = 0.
            do l=1,pas
               ind2 = (l-1)*nxy2
               do k2=1,pas
                  mofbis(indice) = mofbis(indice) + 
     &                             mof(ind1+k2+ind2)
               end do
            end do
            mofbis(indice) = mofbis(indice)/real(pas**2)
         end do
      end do

      somme = 0.
      do i=1,n1
         somme = somme + mofbis(i)
      end do

      sum1 = 0.
      do k=1,m
         do i=1,n1
            sum1 = sum1 + mofbis(i) *
     &      ((rmfbis(i)-g(k,i))**2)/sig2(k,i)  
         end do
      end do

      sum1 = sum1 / somme

      return
      end
 
c     SOUS-ROUTINE: dlambda
c     ---------------------

      subroutine dlambda(n1)

      include 'param_psf.f'

      real*4 sum1,somme,dd(12),sr(12)
      real*4 g(nbg,nbr1),sig2(nbg,nbr1)

      common /gr1/ g,sig2

      c1=33.
      c2=33.
      do j=1,12
        sum1=0.
        somme=0.
        dd(j)=(j-1)*2.
        do k=1,2
          do i=1,n2
            ii=i/32+1
            jj=i-32*(ii-1)
            d=sqrt((ii-c1)**2+(jj-c2)**2)
            if(d.gt.dd(j).and.d.le.dd(j)+2.)then
              somme=somme+1.
              sum1=sum1+g(k,i)**2
            end if
          end do
        end do
        sr(j)=sqrt(sum1)/somme
        print*,' sr(',j,') = ',sr(j),'   ',somme
      end do

      return
      end
