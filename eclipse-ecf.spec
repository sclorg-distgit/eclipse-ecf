%{?scl:%scl_package eclipse-ecf}
%{!?scl:%global pkg_name %{name}}
%{?java_common_find_provides_and_requires}

%global baserelease 2

# The core sub-package must be archful because it is required to be in
# libdir by the platform, but we have no natives, so suppress debuginfo
%global debug_package %{nil}

# This exclude breaks the cyclic dependency on the platform to aide in
# bootstrapping
%global __requires_exclude .*org\.eclipse\.equinox.*

%global git_tag R-Release_HEAD-sdk_feature-3.13.3-Hipp-Tycho-49

Name:           %{?scl_prefix}eclipse-ecf
Version:        3.13.3
Release:        1.%{baserelease}%{?dist}
Summary:        Eclipse Communication Framework (ECF) Eclipse plug-in

License:        EPL
URL:            http://www.eclipse.org/ecf/
Source0:        http://git.eclipse.org/c/ecf/org.eclipse.ecf.git/snapshot/org.eclipse.ecf-%{git_tag}.tar.xz

# Change how feature deps are specified, to avoid embedding versions
Patch0:         eclipse-ecf-feature-deps.patch

BuildRequires:  %{?scl_prefix}tycho
BuildRequires:  %{?scl_prefix}tycho-extras
BuildRequires:  %{?scl_prefix_maven}maven-plugin-build-helper
BuildRequires:  %{?scl_prefix}eclipse-filesystem
BuildRequires:  %{?scl_prefix}eclipse-emf-runtime
BuildRequires:  %{?scl_prefix}eclipse-pde
BuildRequires:  %{?scl_prefix}osgi-annotation
BuildRequires:  %{?scl_prefix_java_common}xpp3-minimal
BuildRequires:  %{?scl_prefix_java_common}httpcomponents-client
BuildRequires:  %{?scl_prefix_java_common}httpcomponents-core
BuildRequires:  %{?scl_prefix_java_common}apache-commons-codec
BuildRequires:  %{?scl_prefix_java_common}apache-commons-logging

%description
ECF is a set of frameworks for building communications into applications and
services. It provides a lightweight, modular, transport-independent, fully
compliant implementation of the OSGi Remote Services standard.

%package   core
Summary:   Eclipse ECF Core
Requires:  %{?scl_prefix}eclipse-filesystem
Requires:  %{?scl_prefix_java_common}httpcomponents-client
Requires:  %{?scl_prefix_java_common}httpcomponents-core

%description core
ECF bundles required by eclipse-platform.

%package   runtime
Summary:   Eclipse Communication Framework (ECF) Eclipse plug-in

BuildArch: noarch

%description runtime
ECF is a set of frameworks for building communications into applications and
services. It provides a lightweight, modular, transport-independent, fully
compliant implementation of the OSGi Remote Services standard.

%package   sdk
Summary:   Eclipse ECF SDK

BuildArch: noarch

%description sdk
Documentation and developer resources for the Eclipse Communication Framework
(ECF) plug-in.

%prep
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
%setup -q -n org.eclipse.ecf-%{git_tag}

find . -type f -name "*.jar" -exec rm {} \;
find . -type f -name "*.class" -exec rm {} \;

%patch0

# Allow building on java > 1.4
sed -i -e 's#(Object) ((URIID) o)#((URIID) o)#g' framework/bundles/org.eclipse.ecf.identity/src/org/eclipse/ecf/core/identity/URIID.java

# Correction for content of runtime package
%pom_xpath_remove "feature/plugin[@id='org.eclipse.ecf.presence']" releng/features/org.eclipse.ecf.core/feature.xml

# Don't build examples or tests
sed -i -e '/<module>examples/d' -e '/<module>tests/d' pom.xml
%pom_disable_module releng/features/org.eclipse.ecf.tests.feature
%pom_disable_module releng/features/org.eclipse.ecf.eventadmin.examples.feature
%pom_disable_module releng/features/org.eclipse.ecf.remoteservice.examples.feature
%pom_disable_module releng/features/org.eclipse.ecf.remoteservice.sdk.examples.feature
%pom_xpath_remove "feature/requires/import[@feature='org.eclipse.ecf.remoteservice.sdk.examples.feature']" releng/features/org.eclipse.ecf.core/feature.xml
%pom_xpath_remove "feature/plugin[@id='org.eclipse.ecf.example.clients']" releng/features/org.eclipse.ecf.core/feature.xml
%pom_xpath_remove "feature/plugin[@id='org.eclipse.ecf.example.collab']" releng/features/org.eclipse.ecf.core/feature.xml
%pom_xpath_remove "feature/plugin[@id='org.eclipse.ecf.example.collab.editor']" releng/features/org.eclipse.ecf.core/feature.xml

# Don't use target platform or jgit packaging bits
%pom_xpath_remove "pom:target"
%pom_xpath_remove "pom:plugin[pom:artifactId='tycho-packaging-plugin']/pom:dependencies"
%pom_xpath_remove "pom:plugin[pom:artifactId='tycho-packaging-plugin']/pom:configuration/pom:sourceReferences"
%pom_xpath_remove "pom:plugin[pom:artifactId='tycho-packaging-plugin']/pom:configuration/pom:timestampProvider"
%pom_disable_module releng/org.eclipse.ecf.releng.repository

# Remove unnecesary dep on json
%pom_xpath_remove "feature/requires/import[@plugin='org.json']" releng/features/org.eclipse.ecf.remoteservice.rest.feature/feature.xml

# Using latest zookeeper requires non-trivial port
%pom_disable_module releng/features/org.eclipse.ecf.discovery.zookeeper.feature
%pom_disable_module providers/bundles/org.eclipse.ecf.provider.zookeeper
%pom_xpath_remove "feature/includes[@id='org.eclipse.ecf.discovery.zookeeper.feature']" releng/features/org.eclipse.ecf.remoteservice.sdk.feature/feature.xml

# Using latest rome requires non-trivial port
%pom_disable_module releng/features/org.eclipse.ecf.remoteservice.rest.synd.feature
%pom_disable_module framework/bundles/org.eclipse.ecf.remoteservice.rest.synd
%pom_xpath_remove "feature/includes[@id='org.eclipse.ecf.remoteservice.rest.synd.feature']" releng/features/org.eclipse.ecf.remoteservice.sdk.feature/feature.xml

# Use system libs
ln -s %{_javadir}/osgi-annotation/osgi.annotation.jar osgi/bundles/org.eclipse.osgi.services.remoteserviceadmin/osgi/
ln -s %{_javadir}/xpp3-minimal.jar protocols/bundles/org.jivesoftware.smack/jars/xpp.jar
ln -s %{_javadir}/irclib.jar providers/bundles/org.eclipse.ecf.provider.irc/lib

# Unavailable dep on dnsjava, smack, irclib
%pom_disable_module releng/features/org.eclipse.ecf.discovery.dnssd.feature
%pom_disable_module providers/bundles/org.eclipse.ecf.provider.dnssd
%pom_xpath_remove "feature/includes[@id='org.eclipse.ecf.discovery.dnssd.feature']" releng/features/org.eclipse.ecf.remoteservice.sdk.feature/feature.xml
%pom_disable_module protocols/bundles/org.jivesoftware.smack
%pom_disable_module providers/bundles/org.eclipse.ecf.provider.xmpp.datashare
%pom_disable_module providers/bundles/org.eclipse.ecf.provider.xmpp
%pom_disable_module providers/bundles/org.eclipse.ecf.provider.xmpp.remoteservice
%pom_disable_module providers/bundles/org.eclipse.ecf.provider.xmpp.ui
%pom_disable_module releng/features/org.eclipse.ecf.xmpp.feature
%pom_xpath_remove "feature/plugin[@id='org.eclipse.ecf.provider.xmpp.ui']" releng/features/org.eclipse.ecf.core/feature.xml
%pom_xpath_remove "feature/includes[@id='org.eclipse.ecf.xmpp.feature']" releng/features/org.eclipse.ecf.remoteservice.sdk.feature/feature.xml
%pom_disable_module providers/bundles/org.eclipse.ecf.provider.irc
%pom_disable_module providers/bundles/org.eclipse.ecf.provider.irc.ui
%pom_xpath_remove "feature/plugin[@id='org.eclipse.ecf.provider.irc']" releng/features/org.eclipse.ecf.core/feature.xml
%pom_xpath_remove "feature/plugin[@id='org.eclipse.ecf.provider.irc.ui']" releng/features/org.eclipse.ecf.core/feature.xml

%mvn_package "::{pom,target}::" __noinstall
%mvn_package "::jar:{sources,sources-feature}:" sdk
%mvn_package ":org.eclipse.ecf.{core,sdk}" sdk
%mvn_package ":org.eclipse.ecf.docshare*" sdk
for p in $(grep '<plugin' releng/features/org.eclipse.ecf.core/feature.xml | sed -e 's/.*id="\(.*\)" d.*/\1/') ; do
%mvn_package ":$p" sdk
done
%mvn_package ":org.eclipse.ecf.remoteservice.sdk.*" sdk
%mvn_package ":org.eclipse.ecf.core.{,ssl.}feature" core
%mvn_package ":org.eclipse.ecf.filetransfer.{,httpclient4.}{,ssl.}feature" core
%mvn_package ":org.eclipse.ecf{,.identity,.ssl,.filetransfer}" core
%mvn_package ":org.eclipse.ecf.provider.filetransfer*" core
%mvn_package ":" runtime
%{?scl:EOF}


%build
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
# Qualifier generated from last modification time of source tarball
QUALIFIER=$(date -u -d"$(stat --format=%y %{SOURCE0})" +v%Y%m%d-%H%M)
%mvn_build -j -- -DforceContextQualifier=$QUALIFIER
%{?scl:EOF}


%install
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
%mvn_install

# Move to libdir due to being part of core platform
install -d -m 755 %{buildroot}%{_libdir}/eclipse
mv %{buildroot}%{_datadir}/eclipse/droplets/ecf-core/eclipse/{plugins,features} %{buildroot}%{_libdir}/eclipse
rm -r %{buildroot}%{_datadir}/eclipse/droplets/ecf-core

# Fixup metadata
sed -i -e 's|%{_datadir}/eclipse/droplets/ecf-core/eclipse|%{_libdir}/eclipse|' %{buildroot}%{_datadir}/maven-metadata/eclipse-ecf-core.xml
sed -i -e 's|%{_datadir}/eclipse/droplets/ecf-core/eclipse/features/|%{_libdir}/eclipse/features/|' \
       -e 's|%{_datadir}/eclipse/droplets/ecf-core/eclipse/plugins/|%{_libdir}/eclipse/plugins/|' .mfiles-core
sed -i -e '/droplets/d' .mfiles-core

# Symlink jars into javadir
install -d -m 755 %{buildroot}%{_javadir}/eclipse
location=%{_libdir}/eclipse/plugins
while [ "$location" != "/" ] ; do
    location=$(dirname $location)
    updir="$updir../"
done
pushd %{buildroot}%{_javadir}/eclipse
for J in ecf{,.identity,.ssl,.filetransfer,.provider.filetransfer{,.ssl,.httpclient4{,.ssl}}}  ; do
    DIR=$updir%{_libdir}/eclipse/plugins
    [ -e "`ls $DIR/org.eclipse.${J}_*.jar`" ] && ln -s $DIR/org.eclipse.${J}_*.jar ${J}.jar
done
popd
%{?scl:EOF}


%files core -f .mfiles-core
%{_javadir}/eclipse/*

%files runtime -f .mfiles-runtime

%files sdk -f .mfiles-sdk

%changelog
* Mon Jan 16 2017 Mat Booth <mat.booth@redhat.com> - 3.13.3-1.2
- Drop unavailable deps

* Mon Jan 16 2017 Mat Booth <mat.booth@redhat.com> - 3.13.3-1.1
- Auto SCL-ise package for rh-eclipse46 collection

* Tue Jan 03 2017 Mat Booth <mat.booth@redhat.com> - 3.13.3-1
- Update to latest release

* Wed Sep 14 2016 Mat Booth <mat.booth@redhat.com> - 3.13.2-1
- Update to latest release
- Set qualifiers to source-modification-time instead of build-time, to
  eliminate descrepancies between architectures
- Add SDK package for sources

* Fri Apr 15 2016 Mat Booth <mat.booth@redhat.com> - 3.13.1-1
- Update to latest release
- Add a new subpackage to ship additional ECF bundles

* Tue Mar 15 2016 Mat Booth <mat.booth@redhat.com> - 3.12.2-2
- Avoid embedding versions of external deps in features. This avoids the need to
  rebuild when a dependency changes version.

* Mon Feb 29 2016 Mat Booth <mat.booth@redhat.com> - 3.12.2-1
- Update to Mars.2 release

* Mon Feb 29 2016 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.12.0-3
- Rebuild for httpcomponents-client 4.5.2

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 3.12.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Dec 07 2015 Mat Booth <mat.booth@redhat.com> - 3.12.0-1
- Update to latest release

* Mon Nov  2 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.11.0-2
- Rebuild for httpcomponents-core-4.4.4 update

* Mon Sep 28 2015 Mat Booth <mat.booth@redhat.com> - 3.11.0-1
- Update to latest upstream release

* Wed Sep 16 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.10.1-5
- Rebuild for httpcomponents-client-4.5.1 update

* Wed Sep  9 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.10.1-4
- Rebuild for httpcomponents-core-4.4.3 update

* Mon Sep 07 2015 Michael Simacek <msimacek@redhat.com> - 3.10.1-3
- Rebuild for httpcomponents-core-4.4.2

* Mon Aug 31 2015 Roland Grunberg <rgrunber@redhat.com> - 3.10.1-2
- Minor changes to build as a droplet.

* Tue Aug 25 2015 Mat Booth <mat.booth@redhat.com> - 3.10.1-1
- Update to latest upstream version
- Use XZ compressed tarball
- Make symlink generation more dynamic

* Wed Aug 05 2015 Mat Booth <mat.booth@redhat.com> - 3.10.0-5
- Rebuilt using xmvn/tycho

* Mon Jun 29 2015 Mat Booth <mat.booth@redhat.com> - 3.10.0-4
- Drop incomplete and forbidden SCL macros

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.10.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu Jun 04 2015 Michael Simacek <msimacek@redhat.com> - 3.10.0-2
- Rebuild against httpcomponents-client-4.5

* Wed May 13 2015 Mat Booth <mat.booth@redhat.com> - 3.10.0-1
- Update to 3.10.0 release

* Tue Mar 31 2015 Mat Booth <mat.booth@redhat.com> - 3.9.3-2
- Add requires on httpcompnents-* >= 4.4.1

* Tue Mar 31 2015 Mat Booth <mat.booth@redhat.com> - 3.9.3-1
- Update to latest upstream release

* Tue Mar 31 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.9.2-4
- Rebuild for httpcomponents-client-4.4.1 update

* Thu Mar 19 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.9.2-3
- Rebuild for httpcomponents-core-4.4.1 update

* Thu Feb 19 2015 Mat Booth <mat.booth@redhat.com> - 3.9.2-2
- Rebuild for latest httpcomponents

* Mon Jan 19 2015 Mat Booth <mat.booth@redhat.com> - 3.9.2-1
- Update to latest upstream release

* Mon Jan 19 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.9.1-3
- Rebuild for httpcomponents 4.4 update

* Tue Dec 09 2014 Roland Grunberg <rgrunber@redhat.com> - 3.9.1-2
- Symlink ECF bundles into javadir.

* Thu Nov 27 2014 Mat Booth <mat.booth@redhat.com> - 3.9.1-1
- Update to latest upstream release

* Thu Nov 27 2014 Mat Booth <mat.booth@redhat.com> - 3.9.0-3
- Make core package archful so it can be installed into libdir
  where eclipse-platform expects it to be

* Tue Nov 18 2014 Mat Booth <mat.booth@redhat.com> - 3.9.0-2
- Rebuild for new commons-codec

* Tue Aug 19 2014 Mat Booth <mat.booth@redhat.com> - 3.9.0-1
- Update to latest upstream release
- Drop unneeded patch

* Wed Aug 6 2014 Alexander Kurtakov <akurtako@redhat.com> 3.8.1-3
- Rebuild against latest httpcomponents.

* Mon Jul 21 2014 Alexander Kurtakov <akurtako@redhat.com> 3.8.1-2
- Rebuild for apache-commons-logging 1.2.

* Wed Jun 25 2014 Mat Booth <mat.booth@redhat.com> - 3.8.1-1
- Update to latest upstream release

* Wed Jun 11 2014 Roland Grunberg <rgrunber@redhat.com> - 3.8.0-4
- Remove problematic manifest alterations from specfile.

* Fri Jun 06 2014 Mat Booth <mat.booth@redhat.com> - 3.8.0-3
- Rebuild against latest httpcomponents.

* Mon May 12 2014 Alexander Kurtakov <akurtako@redhat.com> 3.8.0-2
- Rebuild against latest httpcomponents.

* Wed Mar 19 2014 Mat Booth <fedora@matbooth.co.uk> - 3.8.0-1
- Update to latest upstream.
- Now necessary to explicitly build more fine-grained features.
- Drop unneeded dep on jakarta-commons-httpclient.
- Fixed mixed use of tabs and spaces.
- Switch core package to R: java-headless, rhbz #1068037

* Tue Sep 3 2013 Krzysztof Daniel <kdaniel@redhat.com> 3.6.1-1
- Update to latest upstream.

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.6.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri Jun 21 2013 Krzysztof Daniel <kdaniel@redhat.com> 3.6.0-2
- 974112: Remove versions and timestamps from ECF.

* Wed May 1 2013 Krzysztof Daniel <kdaniel@redhat.com> 3.6.0-1
- Update to latest upstream.

* Mon Apr 8 2013 Krzysztof Daniel <kdaniel@redhat.com> 3.5.7-0.6
- Rebuild with old commons logging.

* Mon Apr 8 2013 Krzysztof Daniel <kdaniel@redhat.com> 3.5.7-0.5
- Drop v3 httpclient.
- Make dependency to commons loggigng less strict.

* Wed Mar 20 2013 Krzysztof Daniel <kdaniel@redhat.com> 3.5.7-0.4
- Add direct dependency to jakarta-commons-httpclient.

* Wed Mar 20 2013 Krzysztof Daniel <kdaniel@redhat.com> 3.5.7-0.3
- Symlink deps against /usr/share/java/.

* Fri Mar 15 2013 Krzysztof Daniel <kdaniel@redhat.com> 3.5.7-0.2
- Explicitly build httpclient4 feature.

* Thu Mar 14 2013 Krzysztof Daniel <kdaniel@redhat.com> 3.5.7-0.1
- Update to latest upstream.
- Initial SCLization.

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.5.6-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Mon Oct 8 2012 Krzysztof Daniel <kdaniel@redhat.com> 3.5.6-7
- Use __requires_exclude instead of __provides_exclude.

* Mon Oct 8 2012 Krzysztof Daniel <kdaniel@redhat.com> 3.5.6-6
- Try out __provides_exclude

* Mon Oct 8 2012 Krzysztof Daniel <kdaniel@redhat.com> 3.5.6-5
- Use new way of changing auto required dependencies.

* Fri Oct 5 2012 Krzysztof Daniel <kdaniel@redhat.com> 3.5.6-4
- Don't generate autorreuquire.

* Mon Aug 27 2012 Krzysztof Daniel <kdaniel@redhat.com> 3.5.6-3
- Don't duplicate org.apache* plugins
- Use context qualifier to avoid constant feature version changes.

* Wed Aug 8 2012 Krzysztof Daniel <kdaniel@redhat.com> 3.5.6-2
- Review issues fixed.

* Wed Aug 8 2012 Krzysztof Daniel <kdaniel@redhat.com> 3.5.6-1
- Initial packaging.
