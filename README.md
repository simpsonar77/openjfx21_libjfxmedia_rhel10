# openjfx21_libjfxmedia_rhel10
files necessary for building openjfx with libjfxmedia.so on RHEL 10

Why:  I needed openjfx to contain/build libjfxmedia.so, which has been removed for a long time due to "dependency" issues.

Source:  https://github.com/openjdk/jfx21u/archive/refs/tags/21.0.11+4.tar.gz  ( matches where fedora grabs their source for this )

1.  This  spec file is based on Fedora 40 Openjfx 17 source rpms
2.  While RHEL/Fedora uses maven, I'm not familiar enough with maven to get new pom files working to build libjfxmedia.so
3.  I didn't want to download gluon's .so files and "hope" it worked
4.  The spec file builds f40 version of the source, updated to openjfx 21.  (due to compatibility issues with gradle 7.5 vs 8, etc...)
5.  rpm then does some cleanup and runs gradle to only build libjfxmedia.so
6.  A few additional patch files were needed for RHEL 10.

hope this helps someone else, as this was non-trivial to get working.  Probably should just stop trying to use libjfxmedia ;)

