c     PROGRAMME DE MINIMISATION
c     -------------------------

c     DECLARATION DES VARIABLES
c     -------------------------

      implicit none

      include 'param_psf.f'

      integer m,i,j,iter,n1,n2,k,ind,half,j2,i2
      integer nax1,nax2,nxy1,nxy2
      
      real*4 a(nbg),c(2,nbg),fret,b(3),beta,tmp(nbr2)
      real*4 a0(nbg),c0(2,nbg),b0(3),be0,pas
      real*4 aa0(nbg),cc0(2,nbg),bb0(3),betabe0
      real*4 g(nbg,nbr1),sig2(nbg,nbr1)
      real*4 tab(nbr1),tab2(nbr1),bb,fwhm,som,t1,t2
      real*4 r(nbr2),sr(2*xy2),phi(nbg,nbr2)

      character*80 ima_name
      character*70 entete
      character*40 ligne
      character*1 lettre1,lettre2
      character*7 fin

      common /gr1/ g,sig2
      common /param/ nxy1,nxy2,pas,bb
      common /fixparam/ a0,c0,b0,be0
      common /var/ a,c,b,beta
      common /mult/ aa0,cc0,bb0,betabe0
      common /tailles/ n1,n2,m
      common /gauss/ r,sr,phi

c     DEBUT DE PROGRAMME
c     ------------------

      n1 = nbr1
      nxy1 = xy1
      n2 = nbr2
      nxy2 = xy2
      pas = int(nxy2/nxy1)

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
      read(1,'(A70)') entete
      read(1,'(A42,F16.10)') ligne,fwhm
      if (fwhm .gt. 2.) then
         b0(1) = 4*log(2.)/(fwhm*fwhm)
         b0(2) = 4*log(2.)/(fwhm*fwhm)
         b(1)=0.01
         b(2)=0.01
         bb0(1) = b0(1)*(1.+b(1))
         bb0(2) = b0(2)*(1.+b(2))
      else
         write(*,*) 'FWHM <= 2 --> error sampling'
         stop
      end if
      read(1,'(A70)') entete
      read(1,'(A70)') entete
      read(1,'(A42,F16.10)') ligne,b0(3)
      b(3)=0.01
      bb0(3) = b0(3)*(1.+b(3))
      read(1,'(A70)') entete
      read(1,'(A70)') entete
      read(1,'(A42,F16.10)') ligne,be0
      beta=0.01
      betabe0 = be0*(1.+beta)
      do i=1,4
         read(1,'(A70)') entete
      end do
      do i=1,m
         read(1,*) a0(i),c0(1,i),c0(2,i)
         a(i)=0.01
         c(1,i)=0.01
         c(2,i)=0.01
         aa0(i) = a0(i)*(1.+a(i))
         cc0(1,i) = c0(1,i)*(1.+c(1,i))
         cc0(2,i) = c0(2,i)*(1.+c(2,i))
      end do  
      close(unit=1)
      do k=1,m
c         write(*,*) '         a  c(1) c(2) ',k,': ',
c    &           a0(k),c0(1,k),c0(2,k)
c	write(*,'(A)',ADVANCE='NO') '+'
      end do
c      write(*,*) '         b1 b2 b3 beta : ',b0(1),b0(2),b0(3),
c     &           be0
c      write(*,*) '---------------------------------------'
	

      do k=1,m
         lettre1 = char(48+int(k/10))
         lettre2 = char(48+mod(k,10))
         fin = lettre1 // lettre2 // '.fits'
         ima_name = 'psf' // fin
         call openima(ima_name,nax1,nax2,tab)
         ima_name = 'psfsig' // fin
         call openima(ima_name,nax1,nax2,tab2)
         do j=1,n1
            g(k,j) = tab(j)
            sig2(k,j) = tab2(j)**2
         end do
      end do

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
           
      call rlft2(r,sr,nxy2,nxy2,1)
      
      call gradient(1.E-08,iter,fret)
      call decomposition()

      end 

c     SOUS-ROUTINE: gradient
c     ----------------------

      subroutine gradient(ftol,iter,fret)

      include 'param_psf.f'

      integer nb
      parameter (itmax=1000,eps=1.E-10,nb=3*nbg+4)

      real*4 gr(nb),h(nb),xi(nb)
      real*4 aa0(nbg),cc0(2,nbg),bb0(3),betabe0,fp,fp2
      integer n1,n2,m

      common /mult/ aa0,cc0,bb0,betabe0
      common /tailles/ n1,n2,m
      common /derivees/ xi
      common /minimum/ fp

      call inifunc(aa0,cc0,bb0,betabe0)
      call dfunc()

      condi = 3*m+4
      do j=1,condi
         gr(j) = -xi(j)
         h(j) = gr(j)
         xi(j) = h(j)
      end do

      do its=1,itmax
         fp2 = fp
c         write(*,*) its,'   minimum: ',fp2,'  khi carre: ',fp2
c         write(*,*)
         iter = its
         call linmin(fret)
         if (2.*abs(fret-fp2).le.ftol*(abs(fret)+abs(fp2)+ eps)) return
         call inifunc(aa0,cc0,bb0,betabe0)
         call dfunc()
         gg = 0.
         dgg = 0.
         do j=1,condi
            gg = gg + gr(j)**2
            dgg = dgg + (xi(j) + gr(j))*xi(j)
         end do
         if (gg .eq. 0.) return
         gam = dgg/gg
         do j=1,condi
            gr(j) = -xi(j)
            h(j) = gr(j) + gam*h(j)
            xi(j) = h(j)
         end do
      end do
      write(*,*) "nombre d'iteration excede"

      return
      end

c     SOUS-ROUTINE: inifunc
c     ---------------------

      subroutine inifunc(aa0,cc0,bb0,betabe0)

      include 'param_psf.f'

      real*4 cc0(2,nbg),bb0(3),betabe0,r(nbr2)
      real*4 rmf(nbr2),bb,aa0(nbg),g(nbg,nbr1),sig2(nbg,nbr1),pas
      real*4 rmfbis(nbg,nbr1),phi(nbg,nbr2),fp
      real*4 srmf(2*xy2),sr(2*xy2)
      integer i,ind,nxy1,nxy2

      common /gr1/ g,sig2
      common /param/ nxy1,nxy2,pas,bb
      common /gauss/ r,sr,phi
      common /moff/ rmfbis
      common /tailles/ n1,n2,m
      common /minimum/ fp

      fp = 0.
      do k=1,m
         do j=1,nxy2
            t2 = j-cc0(2,k)
            do i=1,nxy2
               t1 = i-cc0(1,k)
               ind = i + (j-1)*nxy2
               phi(k,ind) = 1. + bb0(1)*t1*t1 + bb0(2)*t2*t2 + 
     &                      bb0(3)*t1*t2
               rmf(ind) = phi(k,ind)**(-betabe0)
            end do
         end do

         call rlft2(rmf,srmf,nxy2,nxy2,1)
         call produit(rmf,r,srmf,sr,xy2)
         call rlft2(rmf,srmf,nxy2,nxy2,-1)

         do j=1,nxy1
            do i=1,nxy1
               ind1 = nxy2*pas*(j-1)+pas*(i-1)
               indice = (j-1)*nxy1+i
               rmfbis(k,indice) = 0.
               do l=1,pas
                  ind2 = (l-1)*nxy2
                  do k2=1,pas
                     rmfbis(k,indice) = rmfbis(k,indice) + 
     &                                    rmf(ind1+k2+ind2)
                  end do
               end do
               rmfbis(k,indice) = rmfbis(k,indice)/real(pas**2)
               fp = fp+((aa0(k)*rmfbis(k,indice)-
     &             g(k,indice))**2) /sig2(k,indice)  
            end do
         end do
      end do

      return
      end

c     SOUS-ROUTINE: dfunc
c     -------------------

      subroutine dfunc()

      include 'param_psf.f'

      real*4 xi(nbg*3+4),r(nbr2)
      real*4 tmp1,tmp2,tmp3,cons
      real*4 aa0(nbg),cc0(2,nbg),bb0(3),betabe0,pas,tabbis(nbr1)
      real*4 a0(nbg),c0(2,nbg),b0(3),be0
      real*4 g(nbg,nbr1),sig2(nbg,nbr1),rmfbis(nbg,nbr1),tab(6,nbr2)
      real*4 phi(nbg,nbr2),tmp(nbr2),bb
      real*4 sr(2*xy2),stmp(2*xy2)
      integer i,j,ind,ind2,n1,n2,m,nxy1,nxy2

      common /gr1/ g,sig2
      common /param/ nxy1,nxy2,pas,bb
      common /gauss/ r,sr,phi
      common /moff/ rmfbis
      common /mult/ aa0,cc0,bb0,betabe0
      common /fixparam/ a0,c0,b0,be0
      common /derivees/ xi
      common /tailles/ n1,n2,m

      do i=1,m*3+4
         xi(i) = 0.
      end do
      do k=1,m
         do j=1,nxy2
            tmp2 = j-cc0(2,k)
            do i=1,nxy2
               ind = i+(j-1)*nxy2
               tmp1 = i-cc0(1,k)
               tmp3 = phi(k,ind)**(-betabe0-1)
               tab(1,ind) = (2.*bb0(1)*c0(1,k)*tmp1
     &                         +bb0(3)*c0(1,k)*tmp2)*tmp3 
               tab(2,ind) = (2.*bb0(2)*c0(2,k)*tmp2
     &                         +bb0(3)*c0(2,k)*tmp1)*tmp3 
               tab(3,ind) = b0(1)*(tmp1**2)*tmp3
               tab(4,ind) = b0(2)*(tmp2**2)*tmp3
               tab(5,ind) = b0(3)*tmp1*tmp2*tmp3
               tab(6,ind) = be0*(phi(k,ind)**(-betabe0))
     &                          *log(phi(k,ind))
            end do
         end do

         do i=1,7
            if (i .eq. 1) then
               do j=1,n1
                  xi(3*k-2) = xi(3*k-2) + 
     &            (2*a0(k)*(aa0(k)*rmfbis(k,j)-g(k,j))*
     &            rmfbis(k,j))/sig2(k,j)
               end do
            else
               do j=1,n2
                  tmp(j) = tab(i-1,j)
               end do
               call rlft2(tmp,stmp,xy2,xy2,1)
               call produit(tmp,r,stmp,sr,xy2)
               call rlft2(tmp,stmp,xy2,xy2,-1)

               do j=1,nxy1
                  do ii=1,nxy1
                     ind1 = nxy2*pas*(j-1)+pas*(ii-1)
                     indice = (j-1)*nxy1+ii
                     tabbis(indice) = 0.
                     do l=1,pas
                        ind2 = (l-1)*nxy2
                        do k2=1,pas
                           tabbis(indice) = tabbis(indice) + 
     &                                   tmp(ind1+k2+ind2)
                        end do
                     end do
                     tabbis(indice) = tabbis(indice)/real(pas**2)
                  end do
               end do

               if (4 .le. i .and. i .le. 6) then
                  cons = -2*aa0(k)*betabe0
                  ind = 3*m+(i-3)
               else if (i .eq. 7) then
                  cons = -2*aa0(k)
                  ind = 3*m+4
               else
                  cons = 2*aa0(k)*betabe0
                  ind = i+(k-1)*3
               end if
               do j=1,n1
                 xi(ind) = xi(ind) + 
     &               (cons*(aa0(k)*rmfbis(k,j)-
     &               g(k,j))*tabbis(j))/sig2(k,j)
               end do
            end if
         end do
      end do

      return
      end

c     SOUS-ROUTINE: linmin
c     --------------------

      subroutine linmin(fret)

      include 'param_psf.f'

      parameter(epsi=1.E-15)

      real*4 xi(nbg*3+4),a(nbg),c(2,nbg),b(3),beta,max
      real*4 rap(nbg*3+4),raptol(nbg*3+4)
      real*4 aa0(nbg),cc0(2,nbg),bb0(3),betabe0
      real*4 a0(nbg),c0(2,nbg),b0(3),be0

      common /mult/ aa0,cc0,bb0,betabe0
      common /fixparam/ a0,c0,b0,be0
      common /var/ a,c,b,beta
      common /derivees/ xi
      common /tailles/ n1,n2,m

      do k=1,m*3+4
          rap(k) = abs(xi(k)/0.1)
      end do

      max = 0.
      tol=1./epsi
      do i=1,3*m+4
        if (rap(i) .gt. max) then
           max = rap(i)
        end if
        raptol(i) = 0.00001
        if(abs(xi(i)) .gt. epsi) then
          raptol(i) = abs(raptol(i)/xi(i))
        else
          raptol(i) = 1./epsi
        endif
        if(raptol(i) .lt. tol) then
          tol = raptol(i)
          im=i
        endif
      end do
      if (max .gt. 0.2) then
         xx = 0.2/max
      else
         xx = 1.
      end if

      ax = 0.
      bx = 2*xx
      fret = recherche(ax,xx,bx,tol,xmin)
      do k=1,m
         xi(3*k-2) = xmin*xi(3*k-2)
         a(k) = a(k) + xi(3*k-2)
         xi(3*k-1) = xmin*xi(3*k-1)
         c(1,k) = c(1,k) + xi(3*k-1)
         xi(3*k) = xmin*xi(3*k)
         c(2,k) = c(2,k) + xi(3*k)
         aa0(k) = a0(k)*(1.+a(k))
         cc0(1,k) = c0(1,k)*(1.+c(1,k))
         cc0(2,k) = c0(2,k)*(1.+c(2,k))
      end do
      do j=1,3
         xi(3*m+j) = xmin*xi(3*m+j)
         b(j) = b(j) + xi(3*m+j)
         bb0(j) = b0(j)*(1.+b(j))
      end do
      xi(3*m+4) = xmin*xi(3*m+4)
      beta = beta + xi(3*m+4)
      betabe0 = be0*(1.+beta)

      do k=1,m
c         write(*,*) '         a  c(1) c(2) ',k,': ',
c     &           aa0(k),cc0(1,k),cc0(2,k)
      end do
c      write(*,*) '         b1 b2 b3 beta : ',bb0(1),bb0(2),bb0(3),
c     &           betabe0
c      write(*,*) '---------------------------------------'

      return
      end

c     FONCTION: f1dim
c     ---------------

      function f1dim(x)

      include 'param_psf.f'

      real*4 xt1(nbg),xt2(2,nbg),xt3(3),xt4
      real*4 a(nbg),c(2,nbg),b(3),beta,xi(3*nbg+4)
      real*4 a0(nbg),c0(2,nbg),b0(3),be0
      integer n1,n2,m

      common /var/ a,c,b,beta
      common /derivees/ xi
      common /tailles/ n1,n2,m
      common /minimum/ fp
      common /fixparam/ a0,c0,b0,be0

      do k=1,m
         xt1(k) = a0(k)*(1.+(a(k)+x*xi(3*k-2)))
         xt2(1,k) = c0(1,k)*(1.+(c(1,k)+x*xi(3*k-1)))
         xt2(2,k) = c0(2,k)*(1.+(c(2,k)+x*xi(3*k)))
      end do
      do j=1,3
         xt3(j) = b0(j)*(1.+(b(j)+x*xi(3*m+j)))
      end do
      xt4 = be0*(1.+(beta+x*xi(3*m+4)))

      call inifunc(xt1,xt2,xt3,xt4)
      f1dim = fp
 
      return
      end

c     FONCTION: recherche
c     -------------------

      FUNCTION recherche(ax,bx,cx,tol,xmin)

      parameter (gold=1.618034,glimit=100.,tiny=1.E-20)
      parameter (itmax=300,cgold=.381966,zeps=1.0E-10)

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
         tol1 = 0.0001*abs(x)
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

c     SOUS-ROUTINE: fourier
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

c     SOUS-ROUTINE: decomposition
c     ---------------------------

      subroutine decomposition()

      include 'param_psf.f'

      real*4 a(nbg),c(2,nbg),tmp(nbr1),tmp2(nbr2),stmp2(2*xy2)
      real*4 b(3),beta,pas,r(nbr2),tamp1,tamp2
      real*4 a0(nbg),c0(2,nbg),b0(3),be0,sr(2*xy2)
      real*4 aa0(nbg),cc0(2,nbg),bb0(3),betabe0
      real*4 ima(nbr1),ima5(nbr1),sigc(nbr1),bb
      real*4 phi(nbg,nbr2),g(nbg,nbr1),sig2(nbg,nbr1)
      integer j,i,chiffre,n1,n2,m,nxy1,nxy2
      character*20 results,results2,results3
      character*1 lettre1,lettre2

      common /gr1/ g,sig2
      common /param/ nxy1,nxy2,pas,bb
      common /fixparam/ a0,c0,b0,be0
      common /mult/ aa0,cc0,bb0,betabe0
      common /gauss/ r,sr,phi
      common /var/ a,c,b,beta
      common /tailles/ n1,n2,m

      do k=1,m
         chiffre = (k - mod(k,10))/10
         lettre1 = char(48+chiffre)
         lettre2 = char(48+k-chiffre*10)
         results = ''
         results2 = ''

         do j=1,nxy2
            tamp2 = j-cc0(2,k)
            do i=1,nxy2
               ind = i+(j-1)*nxy2
               tamp1 = i-cc0(1,k)
               tmp2(ind) = aa0(k)*(1.+bb0(1)*tamp1*tamp1 + 
     &                     bb0(2)*tamp2*tamp2 + 
     &                     bb0(3)*tamp1*tamp2)**(-betabe0)
            end do
         end do
         call rlft2(tmp2,stmp2,xy2,xy2,1)
         call produit(tmp2,r,stmp2,sr,xy2)
         call rlft2(tmp2,stmp2,xy2,xy2,-1)

         do j=1,nxy1
            do ii=1,nxy1
               ind1 = nxy2*pas*(j-1)+pas*(ii-1)
               indice = (j-1)*nxy1+ii
               ima(indice) = 0.
               do l=1,pas
                  ind2 = (l-1)*nxy2
                  do k2=1,pas
                     ima(indice) = ima(indice) + tmp2(ind1+k2+ind2)
                  end do
               end do
               ima(indice) = (g(k,indice)-(ima(indice)/real(pas*pas)))
     &                       /aa0(k)
               sig2(k,indice) = sig2(k,indice)/(aa0(k)*aa0(k))
            end do
         end do

         xx = nxy1+2-cc0(1,k)/pas
         yy = nxy1+2-cc0(2,k)/pas
c         write(*,*) '------------------------'
c         write(*,*) 'xx,yy, :',xx,yy
         call centrage(ima,ima5,xx,yy,n1)
         do j=1,n1
            tmp(j) = sig2(k,j)
         end do
         call centrage(tmp,sigc,xx,yy,n1)
         do j=1,n1
            if (sigc(j).le.0.) sigc(j) = 1000000.
         end do
         results = 'difc' // lettre1 // lettre2 // '.fits'
         results2 ='sigc' // lettre1 // lettre2 // '.fits'
         call makeima(results,nxy1,ima5)
         call makeima(results2,nxy1,sigc)
         results2 = ''
         results = ''
      end do

      do j=1,nxy2
         do i=1,nxy2
            ind = i+(j-1)*nxy2
            tamp1 = i-(nxy2/2+1)
            tamp2 = j-(nxy2/2+1)
            tmp2(ind) = (1.+bb0(1)*tamp1*tamp1  +
     &                 bb0(2)*tamp2*tamp2 + 
     &                 bb0(3)*tamp1*tamp2)**(-betabe0)
         end do
      end do

      results3 = 'mofc.fits'
      call makeima(results3,nxy2,tmp2)
  

      return
      end

c     SOUS_ROUTINE: centrage
c     ----------------------

      subroutine centrage(t,tt,c1,c2,n)

      include 'param_psf.f'

      real*4 tt(nbr1),t(nbr1),ttt((xy1+2)**2),c1,c2
      real*4 x1(3),x2(3),y1(3,3),ytt,xtt,tamp(nbr1)
      real*4 pas,bb
      integer nxy1,nxy2

      common /param/ nxy1,nxy2,pas,bb

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
      else
         do i=1,n
            tamp(i) = tt(i)
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
      else
         do i=1,n
            tt(i) = tamp(i)
         end do
      end if

      return
      end

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
