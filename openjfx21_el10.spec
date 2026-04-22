# OpenJFX 21 for RHEL 10 / EL10
#
# Based on the Fedora 40 openjfx (jfx17u) spec, adapted for:
#   - jfx21u source (OpenJFX 21 LTS)
#   - RHEL 10 build environment
#   - Native Gradle 8 build for libjfxmedia.so
#
# Key differences from the Fedora 40 jfx17u spec:
#   1.  Source upgraded from jfx17u-17.0.11 to jfx21u-21.0.11
#   2.  GTK 2 removed upstream in JavaFX 21; libglassgtk2 and gtk2
#       BuildRequires dropped (also absent from RHEL 10 base)
#   3.  xxf86vm dropped (absent from RHEL 10 base repos)
#   4.  java-21-openjdk-devel explicit BuildRequires
#   5.  GStreamer 1.x BuildRequires added for libjfxmedia native build
#   6.  alsa-lib-devel BuildRequires added (required by gstreamer-lite make)
#   7.  Patch0: gstclock GWeakRef fix for GLib 2.80+ (glib 2.80.5 on RHEL 10)
#   8.  Gradle native build for libjfxmedia.so via :media:buildLinuxNative
#       and :media:buildLinuxGStreamer (bypasses full sdk target to avoid
#       Java compilation conflicts with the Maven build phase)
#   9.  Maven class bridging added between Maven and Gradle phases
#  10.  buildAVPlugin disabled: avplugin source is incompatible with
#       FFmpeg 7.x (ffmpeg-free 7.x in EPEL 10); GStreamer handles media
#       playback without it. Re-enable when upstream fixes FFmpeg 7 compat.
#  11.  offline_gradle bcond added (disabled by default)
#  12.  C99 patches dropped (not needed for jfx21u)
#  13.  Maven POM shim sources updated for jfx21u module layout
#       (libglassgtk2 removed, sources renumbered)

# ---------------------------------------------------------------------------
# Build conditionals
# ---------------------------------------------------------------------------

# Offline Gradle build support.
# To use: pre-populate a Gradle cache on a networked machine:
#
#   cd ~/rpmbuild/BUILD/jfx21u-21.0.11-4
#   export GRADLE_USER_HOME=$(pwd)/gradle-cache
#   ./gradlew -PCOMPILE_MEDIA=true --no-daemon \
#       :media:buildLinuxGStreamer :media:buildLinuxNative
#   tar czf gradle-cache-jfx21u-21.0.11.tar.gz gradle-cache/
#   cp gradle-cache-jfx21u-21.0.11.tar.gz ~/rpmbuild/SOURCES/
#
# Then build with: rpmbuild -ba openjfx21.spec --with offline_gradle
%bcond_with offline_gradle

%global forgeurl https://github.com/openjdk/jfx21u
%global openjfxdir %{_jvmdir}/%{name}
%global rtdir jfx21u-21.0.11-4

Name:           openjfx
Epoch:          3
Version:        21.0.11.0
Release:        1%{?dist}
Summary:        Rich client application platform for Java
%forgemeta

License:        GPL-2.0-only WITH Classpath-exception-2.0 AND BSD-3-Clause
URL:            %{forgeurl}

Source0:        %{forgesource}
Source1:        pom-base.xml
Source2:        pom-controls.xml
Source3:        pom-fxml.xml
Source4:        pom-graphics.xml
Source5:        pom-graphics_antlr.xml
Source6:        pom-graphics_decora.xml
Source7:        pom-graphics_compileJava.xml
Source8:        pom-graphics_compileJava-decora.xml
Source9:        pom-graphics_compileJava-java.xml
Source10:       pom-graphics_compileJava-prism.xml
Source11:       pom-graphics_graphics.xml
Source12:       pom-graphics_libdecora.xml
Source13:       pom-graphics_libglass.xml
# Note: pom-graphics_libglassgtk2.xml intentionally omitted –
# GTK 2 was removed upstream in JavaFX 21 (JDK-8299595) and is
# also absent from RHEL 10 base repos.
Source14:       pom-graphics_libglassgtk3.xml
Source15:       pom-graphics_libjavafx_font.xml
Source16:       pom-graphics_libjavafx_font_freetype.xml
Source17:       pom-graphics_libjavafx_font_pango.xml
Source18:       pom-graphics_libjavafx_iio.xml
Source19:       pom-graphics_libprism_common.xml
Source20:       pom-graphics_libprism_es2.xml
Source21:       pom-graphics_libprism_sw.xml
Source22:       pom-graphics_prism.xml
Source23:       pom-media.xml
Source24:       pom-openjfx.xml
Source25:       pom-swing.xml
Source26:       pom-swt.xml
Source27:       pom-web.xml
Source28:       build.xml
%if %{with offline_gradle}
# Offline Gradle cache – generate with instructions in bcond comment above
Source29:       gradle-cache-jfx21u-21.0.11.tar.gz
%endif

# openjfx-c99.patch dropped: only hunk (pango.c FcConfigAppFontAddFile
# jboolean->int cast) is already applied upstream in jfx21u.
# C99 patches 2 and 3 carried forward from jfx17u Fedora spec
Patch0:         openjfx-c99-2.patch
Patch1:         openjfx-c99-3.patch
# Fix jbyte* -> jfloat* pointer type in freetype.c (jfx21u source)
Patch2:         openjfx21-freetype-pointer.patch
# openjfx21-pango-glib280.patch dropped: fix already applied in jfx21u source
# Fix GWeakRef** vs GWeakRef* type mismatch in bundled gstreamer-lite
# gstclock.c against GLib 2.80+ (RHEL 10 ships GLib 2.80.5).
# The GSTREAMER_LITE/LINUX macro incorrectly takes the address of a
# GWeakRef* member, yielding GWeakRef** where GLib expects GWeakRef*.
# Upstream fix: jfx21u commit 41acdb60 (not yet in a tagged release).
Patch3:         openjfx21-gstclock-glib280.patch

ExclusiveArch:  x86_64

Requires:       java-21-openjdk-headless
Requires:       gtk3
Requires:       gstreamer1
Requires:       gstreamer1-plugins-base

BuildRequires:  javapackages-tools
BuildRequires:  java-21-openjdk-devel
BuildRequires:  maven-local
BuildRequires:  ant
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  libstdc++-static
BuildRequires:  make
BuildRequires:  mvn(org.eclipse.swt:swt)
BuildRequires:  mvn(org.antlr:antlr)
BuildRequires:  mvn(org.antlr:antlr4-maven-plugin)
BuildRequires:  mvn(org.antlr:stringtemplate)
BuildRequires:  mvn(org.apache.ant:ant)
BuildRequires:  mvn(org.codehaus.mojo:native-maven-plugin)
BuildRequires:  mvn(org.codehaus.mojo:exec-maven-plugin)
BuildRequires:  mvn(org.apache.maven.plugins:maven-antrun-plugin)

BuildRequires:  pkgconfig(gtk+-3.0)
BuildRequires:  pkgconfig(gthread-2.0)
BuildRequires:  pkgconfig(xtst)
BuildRequires:  pkgconfig(libjpeg)
BuildRequires:  pkgconfig(gl)
# xxf86vm absent from RHEL 10 base repos – omitted

# GStreamer devel for libjfxmedia native build (gstreamer-lite make)
BuildRequires:  gstreamer1-devel
BuildRequires:  gstreamer1-plugins-base-devel
BuildRequires:  pkgconfig(gstreamer-1.0)
BuildRequires:  pkgconfig(gstreamer-app-1.0)
BuildRequires:  pkgconfig(gstreamer-audio-1.0)
BuildRequires:  pkgconfig(gstreamer-base-1.0)
BuildRequires:  pkgconfig(gstreamer-pbutils-1.0)
BuildRequires:  pkgconfig(gstreamer-video-1.0)
# alsa-lib-devel required by gstreamer-lite Makefile pkg-config call
BuildRequires:  alsa-lib-devel
BuildRequires:  pkgconfig(alsa)

BuildRequires:  cmake
BuildRequires:  gperf
BuildRequires:  perl
BuildRequires:  python3

%description
JavaFX/OpenJFX is a set of graphics and media APIs that enables Java
developers to design, create, test, debug, and deploy rich client
applications that operate consistently across diverse platforms.

This package includes libjfxmedia.so built from source using the
OpenJFX native Gradle build system. The AVPlugin (FFmpeg-based codec
support) is disabled pending upstream FFmpeg 7.x compatibility fixes;
GStreamer provides full media playback functionality.

%global debug_package %{nil}


%prep
%autosetup -p1 -n %{rtdir}

# Ensure gradlew is executable (GitHub tarballs strip execute bits)
chmod +x gradlew

# Disable buildAVPlugin: the bundled avplugin source is not compatible
# with FFmpeg 7.x (ffmpeg-free 7.x in EPEL 10). GStreamer handles media
# playback without it. Re-enable when upstream fixes FFmpeg 7 compat.
sed -i 's/buildNative\.dependsOn buildAVPlugin/\/\/ buildNative.dependsOn buildAVPlugin  \/\/ disabled: FFmpeg 7.x incompatible/' \
    build.gradle

rm -f modules/javafx.base/src/main/java/com/sun/javafx/runtime/VersionInfo.java

%if %{with offline_gradle}
# Extract pre-populated Gradle cache for offline build
tar xzf %{SOURCE29} -C %{_builddir}/
%endif

#Drop *src/test folders
rm -rf modules/javafx.{base,controls,fxml,graphics,media,swing,swt,web}/src/test/
rm -rf modules/jdk.packager/src/test/ 2>/dev/null || true

#prep for javafx.graphics
cp -a modules/javafx.graphics/src/jslc/antlr modules/javafx.graphics/src/main/antlr3
cp -a modules/javafx.graphics/src/main/resources/com/sun/javafx/tk/quantum/*.properties \
      modules/javafx.graphics/src/main/java/com/sun/javafx/tk/quantum

find -name '*.class' -delete
# Preserve gradle-wrapper.jar – needed for the Gradle media build phase
find -name '*.jar' -not -name 'gradle-wrapper.jar' -delete

#copy maven files
cp -a %{_sourcedir}/pom-*.xml .
mv pom-openjfx.xml pom.xml

for MODULE in base controls fxml graphics media swing swt web
do
    mv pom-$MODULE.xml ./modules/javafx.$MODULE/pom.xml
done

# Remove mvn-libglassgtk2 child module reference from the graphics
# aggregator POM now that it has been moved into place. GTK 2 was
# removed upstream in JavaFX 21 so we have no pom-graphics_libglassgtk2.xml
# and never create the mvn-libglassgtk2 directory.
sed -i '/<module>mvn-libglassgtk2<\/module>/d' \
    ./modules/javafx.graphics/pom.xml

# GTK 2 removed in JavaFX 21 – no libglassgtk2 directory or POM
mkdir ./modules/javafx.graphics/mvn-{antlr,decora,compileJava,graphics,libdecora,libglass,libglassgtk3,libjavafx_font,libjavafx_font_freetype,libjavafx_font_pango,libjavafx_iio,libprism_common,libprism_es2,libprism_sw,prism}
for GRAPHMOD in antlr decora compileJava graphics libdecora libglass libglassgtk3 libjavafx_font libjavafx_font_freetype libjavafx_font_pango libjavafx_iio libprism_common libprism_es2 libprism_sw prism
do
    mv pom-graphics_$GRAPHMOD.xml ./modules/javafx.graphics/mvn-$GRAPHMOD/pom.xml
done

mkdir ./modules/javafx.graphics/mvn-compileJava/mvn-{decora,java,prism}
for SUBMOD in decora java prism
do
    mv pom-graphics_compileJava-$SUBMOD.xml \
       ./modules/javafx.graphics/mvn-compileJava/mvn-$SUBMOD/pom.xml
done

# Fix Java release level in Maven POM shims.
# jfx21u source uses Java 16+ features (pattern matching instanceof)
# so --release 11 / <release>11</release> in the POM shims must be
# updated to 17 (jfx.jdk.target.version=17 in build.properties).
# Must run AFTER all pom.xml files have been moved into place.
find . -name 'pom.xml' | xargs sed -i \
    -e 's|<release>11</release>|<release>17</release>|g' \
    -e 's|<source>11</source>|<source>17</source>|g' \
    -e 's|<target>11</target>|<target>17</target>|g' \
    -e "s|'release', '11'|'release', '17'|g"

#set VersionInfo
cp -a %{_sourcedir}/build.xml .
ant -f build.xml

mkdir -p ./modules/javafx.graphics/mvn-antlr/src/main
mv ./modules/javafx.graphics/src/main/antlr3 \
   ./modules/javafx.graphics/mvn-antlr/src/main/antlr4

# Fix -h javac header output paths in mvn-compileJava sub-modules.
# Each POM passes a bare relative path to javac -h which resolves
# relative to the sub-module working directory, not the source root.
# Correct to ../../ so headers land at the top-level build/gensrc/headers/
# where the native compile (libdecora_sse etc.) looks for them.
sed -i 's|<arg>modules/javafx.graphics/build/gensrc/headers/</arg>|<arg>../../build/gensrc/headers/</arg>|' \
    ./modules/javafx.graphics/mvn-compileJava/mvn-decora/pom.xml
sed -i 's|<arg>modules/javafx.graphics/build/gensrc/headers/</arg>|<arg>../../build/gensrc/headers/</arg>|' \
    ./modules/javafx.graphics/mvn-compileJava/mvn-java/pom.xml
sed -i 's|<arg>modules/javafx.graphics/build/gensrc/headers/</arg>|<arg>../../build/gensrc/headers/</arg>|' \
    ./modules/javafx.graphics/mvn-compileJava/mvn-prism/pom.xml
mkdir -p ./modules/javafx.graphics/build/gensrc/headers

# Same -h path fix for javafx.web
sed -i 's|<arg>modules/javafx.web/build/gensrc/headers/javafx.web/</arg>|<arg>build/gensrc/headers/javafx.web/</arg>|' \
    ./modules/javafx.web/pom.xml
mkdir -p ./modules/javafx.web/build/gensrc/headers/javafx.web

rm -rf ./modules/javafx.web/src/main/native/Source/WTF/icu
rm -rf ./modules/javafx.web/src/main/native/Source/ThirdParty/icu


%build

export CFLAGS="${RPM_OPT_FLAGS}"
export CXXFLAGS="${RPM_OPT_FLAGS}"

# Phase 1: Maven build – all Java modules + native glass/prism/font libs.
# COMPILE_MEDIA is intentionally absent; libjfxmedia is handled by the
# Gradle phase below.
%mvn_build --skip-javadoc

# Disable libjfxwebkit build (fails since F36)
#{cmake} ...
#{cmake_build}

# ---------------------------------------------------------------------------
# Phase 2: Gradle native build for libjfxmedia.so
#
# We target only the media native tasks rather than the full 'sdk' target.
# The full sdk target recompiles all Java which conflicts with the Maven
# build output already in place.  The media native tasks only run make.
#
# Bridge Maven-compiled classes to where Gradle expects them so that
# generateMediaErrorHeader can find them on the module path.
# ---------------------------------------------------------------------------

# Clean Maven-generated gensrc/java directories before Gradle phase.
# Maven leaves behind build/gensrc/java/ with generated files like
# VersionInfo.java. Gradle regenerates these and will fail with
# 'duplicate class' if it finds both copies on the module source path.
find modules -path '*/build/gensrc/java' -type d -exec rm -rf {} + 2>/dev/null || true

# Bridge Maven output to Gradle's expected class directories
mkdir -p modules/javafx.media/build/classes/java/main
cp -a modules/javafx.media/target/classes/. \
      modules/javafx.media/build/classes/java/main/

mkdir -p modules/javafx.graphics/build/classes/java/main
cp -a modules/javafx.graphics/target/classes/. \
      modules/javafx.graphics/build/classes/java/main/

mkdir -p modules/javafx.base/build/classes/java/main
cp -a modules/javafx.base/target/classes/. \
      modules/javafx.base/build/classes/java/main/

export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which javac))))

%if %{with offline_gradle}
export GRADLE_USER_HOME="%{_builddir}/gradle-cache"
%else
export GRADLE_USER_HOME="%{_builddir}/gradle-home"
mkdir -p "${GRADLE_USER_HOME}"
%endif

find . -path "*/src/main/java/com/sun/javafx/runtime/VersionInfo.java" -delete
find . -path "*/build/gensrc/java/*/VersionInfo.java" -delete
./gradlew \
    -PCOMPILE_MEDIA=true \
%if %{with offline_gradle}
    --offline \
%endif
     :media:buildLinuxNative \
     --no-daemon 
#    --no-configuration-cache \
#    -x test \
#    :media:generateMediaErrorHeader \
#    :media:buildLinuxGStreamer \
#    :media:buildLinuxNative

# Locate the built library
JFXMEDIA_SO=$(find modules/javafx.media/build/native -name libjfxmedia.so | head -1)
if [ -z "${JFXMEDIA_SO}" ]; then
    echo "ERROR: libjfxmedia.so not found after Gradle build" >&2
    exit 1
fi
cp -a "${JFXMEDIA_SO}" %{_builddir}/libjfxmedia.so

# Also locate libgstreamer-lite.so (built alongside libjfxmedia)
GSTLITE_SO=$(find modules/javafx.media/build/native -name libgstreamer-lite.so | head -1)
if [ -z "${GSTLITE_SO}" ]; then
    echo "ERROR: libgstreamer-lite.so not found after Gradle build" >&2
    exit 1
fi
cp -a "${GSTLITE_SO}" %{_builddir}/libgstreamer-lite.so


%install

install -d -m 755 %{buildroot}%{openjfxdir}
cp -a modules/javafx.{base,controls,fxml,media,swing,swt,web}/target/*.jar \
      %{buildroot}%{openjfxdir}
cp -a modules/javafx.graphics/mvn-compileJava/mvn-java/target/*.jar \
      %{buildroot}%{openjfxdir}
# GTK 2 removed in JavaFX 21 – no libglassgtk2
cp -a modules/javafx.graphics/mvn-lib{decora,javafx_font,javafx_font_freetype,javafx_font_pango,glass,glassgtk3,javafx_iio,prism_common,prism_es2,prism_sw}/target/*.so \
      %{buildroot}%{openjfxdir}
#cp -a %_target_platform/lib/libjfxwebkit.so %{buildroot}%{openjfxdir}

# Install libjfxmedia.so and its bundled gstreamer-lite from Gradle build
install -m 755 %{_builddir}/libjfxmedia.so    %{buildroot}%{openjfxdir}/
install -m 755 %{_builddir}/libgstreamer-lite.so %{buildroot}%{openjfxdir}/


%files
%{openjfxdir}/
%license LICENSE
%license ADDITIONAL_LICENSE_INFO
%license ASSEMBLY_EXCEPTION
%doc README.md


%changelog
* Wed Apr 22 2026 Andrew Simpson <andrew.r.simpson6.civ@us.navy.mil> - 3:21.0.11.0-1
- Initial RHEL 10 port of OpenJFX 21 (jfx21u-21.0.11+4)
- Upgrade from jfx17u-17.0.11 to jfx21u-21.0.11
- Add Patch0: gstclock GWeakRef fix for GLib 2.80+ (RHEL 10 ships 2.80.5)
- Add Gradle native build for libjfxmedia.so via targeted media tasks
   :media:buildLinuxNative) to avoid Java recompilation conflicts
- Add Maven class bridging between Maven and Gradle build phases
- Add alsa-lib-devel BuildRequires (required by gstreamer-lite make)
- Disable buildAVPlugin: incompatible with ffmpeg-free 7.x (EPEL 10);
  GStreamer handles media playback without it; re-enable when upstream
  fixes FFmpeg 7 API compatibility in the avplugin source
- Add offline_gradle bcond (disabled by default; see bcond comment)
- Install libgstreamer-lite.so alongside libjfxmedia.so

