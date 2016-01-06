%{?scl:%scl_package eclipse-ecf}
%{!?scl:%global pkg_name %{name}}
%{?java_common_find_provides_and_requires}

# The core sub-package must be archful because it is required to be in
# libdir by the platform, but we have no natives, so suppress debuginfo
%global debug_package %{nil}

# This exclude breaks the cyclic dependency on the platform to aide in
# bootstrapping
%global __requires_exclude osgi*

%global git_tag R-Release_HEAD-sdk_feature-144_2014-11-16_21-26-19

Name:           %{?scl_prefix}eclipse-ecf
Version:        3.9.1
Release:        2.5.bootstrap1%{?dist}
Summary:        Eclipse Communication Framework (ECF) Eclipse plug-in

License:        EPL
URL:            http://www.eclipse.org/ecf/
Source0:        http://git.eclipse.org/c/ecf/org.eclipse.ecf.git/snapshot/org.eclipse.ecf-%{git_tag}.tar.bz2

BuildRequires:  java-devel
BuildRequires:  %{?scl_prefix}eclipse-pde >= 1:4.3.0
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
Requires:  java
Requires:  %{?scl_prefix}eclipse-filesystem
Obsoletes: %{name}-core < %{version}-%{release}

%description core
ECF bundles required by eclipse-platform.

%prep
%setup -q -n org.eclipse.ecf-%{git_tag}

find . -type f -name "*.jar" -exec rm {} \;
find . -type f -name "*.class" -exec rm {} \;

#get just the bits we need
mkdir -p ecf/plugins
mkdir -p ecf/features

cp -r releng/features/org.eclipse.ecf.core.{,ssl.}feature \
    ecf/features
cp -r releng/features/org.eclipse.ecf.filetransfer.httpclient4.{,ssl.}feature \
    ecf/features
cp -r releng/features/org.eclipse.ecf.filetransfer.{,ssl.}feature \
    ecf/features

cp -r framework/bundles/org.eclipse.ecf ecf/plugins
cp -r framework/bundles/org.eclipse.ecf.identity ecf/plugins
cp -r framework/bundles/org.eclipse.ecf.ssl ecf/plugins
cp -r framework/bundles/org.eclipse.ecf.filetransfer ecf/plugins
cp -r providers/bundles/org.eclipse.ecf.provider.filetransfer ecf/plugins
cp -r providers/bundles/org.eclipse.ecf.provider.filetransfer.ssl ecf/plugins
cp -r providers/bundles/org.eclipse.ecf.provider.filetransfer.httpclient4 ecf/plugins
cp -r providers/bundles/org.eclipse.ecf.provider.filetransfer.httpclient4.ssl ecf/plugins

rm -rf `ls | grep -v "ecf"`

# Orbit deps for PDE build
%{?scl:scl enable %{scl_java_common} %{scl_maven} %{scl_maven} %{scl} - <<EOF}
mkdir -p deps
build-jar-repository -s -p deps \
  httpcomponents/httpclient httpcomponents/httpcore commons-codec commons-logging
%{?scl:EOF}

# Allow building on java > 1.4
sed -i -e 's#(Object) ((URIID) o)#((URIID) o)#g' ecf/plugins/org.eclipse.ecf.identity/src/org/eclipse/ecf/core/identity/URIID.java

%build
OPTIONS="-DforceContextQualifier=$(date +v%Y%m%d-%H00)"

%{?scl:scl enable %{scl_java_common} %{scl_maven} %{scl_maven} %{scl} - <<EOF}
eclipse-pdebuild -f org.eclipse.ecf.core.feature -j "$OPTIONS" -o `pwd`/deps
eclipse-pdebuild -f org.eclipse.ecf.core.ssl.feature -j "$OPTIONS" -o `pwd`/deps
eclipse-pdebuild -f org.eclipse.ecf.filetransfer.feature -j "$OPTIONS" -o `pwd`/deps
eclipse-pdebuild -f org.eclipse.ecf.filetransfer.ssl.feature -j "$OPTIONS" -o `pwd`/deps
eclipse-pdebuild -f org.eclipse.ecf.filetransfer.httpclient4.feature -j "$OPTIONS" -o `pwd`/deps
eclipse-pdebuild -f org.eclipse.ecf.filetransfer.httpclient4.ssl.feature -j "$OPTIONS" -o `pwd`/deps
%{?scl:EOF}

%install
install -d -m 755 %{buildroot}%{_libdir}/eclipse/{features,plugins}

unzip -q -n -d %{buildroot}%{_libdir} build/rpmBuild/org.eclipse.ecf.core.feature.zip
unzip -q -n -d %{buildroot}%{_libdir} build/rpmBuild/org.eclipse.ecf.core.ssl.feature.zip
unzip -q -n -d %{buildroot}%{_libdir} build/rpmBuild/org.eclipse.ecf.filetransfer.feature.zip
unzip -q -n -d %{buildroot}%{_libdir} build/rpmBuild/org.eclipse.ecf.filetransfer.ssl.feature.zip
unzip -q -n -d %{buildroot}%{_libdir} build/rpmBuild/org.eclipse.ecf.filetransfer.httpclient4.feature.zip
unzip -q -n -d %{buildroot}%{_libdir} build/rpmBuild/org.eclipse.ecf.filetransfer.httpclient4.ssl.feature.zip

mkdir -p %{buildroot}%{_javadir}/eclipse

# Symlink jars into javadir
pushd %{buildroot}%{_javadir}/eclipse
for J in ecf{,.identity,.ssl,.filetransfer,.provider.filetransfer{,.ssl,.httpclient4{,.ssl}}}  ; do
    DIR=%{?scl:../../../../}../../../..%{_libdir}/eclipse
    [ -e "`ls $DIR/plugins/org.eclipse.${J}_*.jar`" ] && ln -s $DIR/plugins/org.eclipse.${J}_*.jar ${J}.jar
done
popd

# Remove stuff that will be symlinked by the platform
rm %{buildroot}%{_libdir}/eclipse/plugins/org.apache*

%files core
%{_libdir}/eclipse/features/*
%{_libdir}/eclipse/plugins/*
%{_javadir}/eclipse/*
%doc ecf/features/org.eclipse.ecf.core.feature/*.html

%changelog
* Tue Apr 07 2015 Mat Booth <mat.booth@redhat.com> - 3.9.1-2.5
- Resolves: rhbz#1208867 - Fix upgrade path from DTS30

* Tue Jan 13 2015 Mat Booth <mat.booth@redhat.com> - 3.9.1-2.4
- Related: rhbz#1175105 - Rebuild for latest httpcomponents
- Also remove temp versions fix, fix disttag

* Mon Jan 12 2015 Mat Booth <mat.booth@redhat.com> - 3.9.1-2.3
- Related: rhbz#1175105 - Temporarily fix dep versions so we can use
  java-common collection deps in the future

* Fri Jan 09 2015 Mat Booth <mat.booth@redhat.com> - 3.9.1-2.2
- Related: rhbz#1175105 - Don't use java-headless

* Wed Jan 07 2015 Mat Booth <mat.booth@redhat.com> - 3.9.1-2.1
- Resolves: rhbz#1175105 - Import into DTS 3.1

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
