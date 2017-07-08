# License

MCS is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY ; without 
even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
General Public License for more details (LICENSE.txt).

You should have received a copy of the GNU General Public License along with MCS ; if not, 
write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA.


# Compilation of F77 MCS for cosmouline


The PSF here is the "new" one (old one is no longer supported)
deconv has been modified to support individual fwhm-des-g, in May 2010

We need :
 - extract.exe
 - psf.exe
 - deconv.exe
For the last two, we also want versions with reduced verbosity (but otherwise identical) :
 - psf_silence.exe
 - deconv_silence.exe


Some sample compilation commands can be found in the csh scripts of this directory.


Some hard-to find lines I had to tweak for psf_silence :
69
656




