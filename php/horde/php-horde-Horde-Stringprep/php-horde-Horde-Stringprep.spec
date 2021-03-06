# spec file for php-horde-Horde-Stringprep
#
# Copyright (c) 2014-2015 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/3.0/
#
# Please, preserve the changelog entries
#
%{!?pear_metadir: %global pear_metadir %{pear_phpdir}}
%{!?__pear:       %global __pear       %{_bindir}/pear}
%global pear_name    Horde_Stringprep
%global pear_channel pear.horde.org

Name:           php-horde-Horde-Stringprep
Version:        1.0.1
Release:        1%{?dist}
Summary:        Preparation of Internationalized Strings ("stringprep")

Group:          Development/Libraries
License:        LGPLv3
URL:            http://www.horde.org/
Source0:        http://%{pear_channel}/get/%{pear_name}-%{version}.tgz

# use system library instead of bundled copy
Patch0:         %{pear_name}-syslib.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  php(language) >= 5.3.0
BuildRequires:  php-pear(PEAR) >= 1.7.0
BuildRequires:  php-channel(%{pear_channel})

Requires(post): %{__pear}
Requires(postun): %{__pear}
Requires:       php(language) >= 5.3.0
Requires:       php-pear(PEAR) >= 1.7.0
Requires:       php-channel(%{pear_channel})
# Unbundled library
Requires:       php-composer(znerol/php-stringprep)

Provides:       php-pear(%{pear_channel}/%{pear_name}) = %{version}


%description
Horde wrapper around the znerol/php-stringprep package.


%prep
%setup -q -c
cd %{pear_name}-%{version}

%patch0 -p1 -b .syslib

sed -e '/bundle/d' \
    -e '/Stringprep.php/s/md5sum=.*name=/name=/' \
    ../package.xml >%{name}.xml
touch -r ../package.xml %{name}.xml


%build
cd %{pear_name}-%{version}
# Empty build section, most likely nothing required.


%install
cd %{pear_name}-%{version}
rm -rf %{buildroot}
%{__pear} install --nodeps --packagingroot %{buildroot} %{name}.xml

# Clean up unnecessary files
rm -rf %{buildroot}%{pear_metadir}/.??*

# Install XML package description
mkdir -p %{buildroot}%{pear_xmldir}
install -pm 644 %{name}.xml %{buildroot}%{pear_xmldir}


%clean
rm -rf %{buildroot}


%post
%{__pear} install --nodeps --soft --force --register-only \
    %{pear_xmldir}/%{name}.xml >/dev/null || :

%postun
if [ $1 -eq 0 ] ; then
    %{__pear} uninstall --nodeps --ignore-errors --register-only \
        %{pear_channel}/%{pear_name} >/dev/null || :
fi


%files
%defattr(-,root,root,-)
%doc %{pear_docdir}/%{pear_name}
%{pear_xmldir}/%{name}.xml
%dir %{pear_phpdir}/Horde
%{pear_phpdir}/Horde/Stringprep.php


%changelog
* Tue Nov 18 2014 Remi Collet <remi@fedoraproject.org> - 1.0.1-1
- Update to 1.0.1

* Sun Nov  9 2014 Remi Collet <remi@fedoraproject.org> - 1.0.0-1
- Initial package, version 1.0.0