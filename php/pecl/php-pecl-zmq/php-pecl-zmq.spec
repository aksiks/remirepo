# spec file for php-pecl-zmq
#
# Copyright (c) 2013-2015 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/3.0/
#
# Please, preserve the changelog entries
#
%{?scl:          %scl_package        php-pecl-zmq}
%{!?php_inidir:  %global php_inidir  %{_sysconfdir}/php.d}
%{!?__pecl:      %global __pecl      %{_bindir}/pecl}
%{!?__php:       %global __php       %{_bindir}/php}

%global with_zts   0%{?__ztsphp:1}
%global pecl_name  zmq
%global with_tests %{?_without_tests:0}%{!?_without_tests:1}
%if "%{php_version}" < "5.6"
%global ini_name   %{pecl_name}.ini
%else
%global ini_name   40-%{pecl_name}.ini
%endif

Summary:        ZeroMQ messaging
Name:           %{?scl_prefix}php-pecl-%{pecl_name}
Version:        1.1.2
Release:        4%{?dist}%{!?nophptag:%(%{__php} -r 'echo ".".PHP_MAJOR_VERSION.".".PHP_MINOR_VERSION;')}.1
License:        BSD
Group:          Development/Languages
URL:            http://pecl.php.net/package/%{pecl_name}
Source0:        http://pecl.php.net/get/%{pecl_name}-%{version}.tgz

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  %{?scl_prefix}php-devel > 5.2
BuildRequires:  %{?scl_prefix}php-pear
%if 0%{?fedora} >= 17 || 0%{?rhel} >= 6
BuildRequires:  zeromq3-devel
%else
BuildRequires:  zeromq-devel >= 2.0.7
%endif
# needed on EL-5
BuildRequires: pkgconfig

Requires(post): %{__pecl}
Requires(postun): %{__pecl}
Requires:       %{?scl_prefix}php(zend-abi) = %{php_zend_api}
Requires:       %{?scl_prefix}php(api) = %{php_core_api}
%{?_sclreq:Requires: %{?scl_prefix}runtime%{?_sclreq}%{?_isa}}

# Version 1.0.7 is the first pecl release
# Fedora/EPEL still provides php-zmq, not php-pecl-zmq
Obsoletes:      %{?scl_prefix}php-%{pecl_name} < %{version}
Provides:       %{?scl_prefix}php-%{pecl_name} = %{version}
Provides:       %{?scl_prefix}php-%{pecl_name}%{?_isa} = %{version}
Provides:       %{?scl_prefix}php-pecl(%{pecl_name}) = %{version}
Provides:       %{?scl_prefix}php-pecl(%{pecl_name})%{?_isa} = %{version}

%if "%{?vendor}" == "Remi Collet" && 0%{!?scl:1}
# Other third party repo stuff
Obsoletes:     php53-pecl-%{pecl_name}
Obsoletes:     php53u-pecl-%{pecl_name}
Obsoletes:     php54-pecl-%{pecl_name}
Obsoletes:     php54w-pecl-%{pecl_name}
%if "%{php_version}" > "5.5"
Obsoletes:     php55u-pecl-%{pecl_name}
Obsoletes:     php55w-pecl-%{pecl_name}
%endif
%if "%{php_version}" > "5.6"
Obsoletes:     php56u-pecl-%{pecl_name}
Obsoletes:     php56w-pecl-%{pecl_name}
%endif
%endif

%if 0%{?fedora} < 20 && 0%{?rhel} < 7
# Filter shared private
%{?filter_provides_in: %filter_provides_in %{_libdir}/.*\.so$}
%{?filter_setup}
%endif


%description
ZeroMQ is a software library that lets you quickly design and implement
a fast message-based applications.


%prep
%setup -q -c

mv %{pecl_name}-%{version} NTS

%if %{with_zts}
# Duplicate source tree for NTS / ZTS build
cp -pr NTS ZTS
%endif

# Create configuration file
cat << 'EOF' | tee %{ini_name}
; Enable %{summary} extension module
extension=%{pecl_name}.so
EOF


%build
cd NTS
%{_bindir}/phpize
%configure \
    --with-zmq \
    --with-libdir=%{_lib} \
    --with-php-config=%{_bindir}/php-config
make %{?_smp_mflags}

%if %{with_zts}
cd ../ZTS
%{_bindir}/zts-phpize
%configure \
    --with-zmq \
    --with-libdir=%{_lib} \
    --with-php-config=%{_bindir}/zts-php-config
make %{?_smp_mflags}
%endif


%install
rm -rf %{buildroot}

make -C NTS \
     install INSTALL_ROOT=%{buildroot}

# install config file
install -D -m 644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}

# Install XML package description
install -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml

%if %{with_zts}
make -C ZTS \
     install INSTALL_ROOT=%{buildroot}

install -D -m 644 %{ini_name} %{buildroot}%{php_ztsinidir}/%{ini_name}
%endif

# Test & Documentation
for i in $(grep 'role="test"' package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 NTS/$i %{buildroot}%{pecl_testdir}/%{pecl_name}/$i
done
for i in $(grep 'role="doc"' package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 NTS/$i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done


%post
%{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :


%postun
if [ $1 -eq 0 ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi


%check
cd NTS
: Minimal load test for NTS extension
%{__php} --no-php-ini \
    --define extension=%{buildroot}/%{php_extdir}/%{pecl_name}.so \
    --modules | grep %{pecl_name}

%if %{with_tests}
: upstream test suite for NTS extension
export TEST_PHP_ARGS="-n -d extension_dir=$PWD/modules -d extension=%{pecl_name}.so"
export REPORT_EXIT_STATUS=1
export NO_INTERACTION=1
export TEST_PHP_EXECUTABLE=%{__php}
%{__php} -n run-tests.php
%endif

%if %{with_zts}
cd ../ZTS
: Minimal load test for ZTS extension
%{__ztsphp} --no-php-ini \
    --define extension=%{buildroot}/%{php_ztsextdir}/%{pecl_name}.so \
    --modules | grep %{pecl_name}

%if %{with_tests}
: upstream test suite for ZTS extension
export TEST_PHP_ARGS="-n -d extension_dir=$PWD/modules -d extension=%{pecl_name}.so"
export TEST_PHP_EXECUTABLE=%{__ztsphp}
%{__ztsphp} -n run-tests.php
%endif
%endif


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc %{pecl_docdir}/%{pecl_name}
%doc %{pecl_testdir}/%{pecl_name}
%{pecl_xmldir}/%{name}.xml

%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{pecl_name}.so

%if %{with_zts}
%config(noreplace) %{php_ztsinidir}/%{ini_name}
%{php_ztsextdir}/%{pecl_name}.so
%endif


%changelog
* Wed Dec 24 2014 Remi Collet <remi@fedoraproject.org> - 1.1.2-4.1
- Fedora 21 SCL mass rebuild

* Mon Aug 25 2014 Remi Collet <rcollet@redhat.com> - 1.1.2-4
- improve SCL build

* Thu Apr 17 2014 Remi Collet <remi@fedoraproject.org> - 1.1.2-3
- add numerical prefix to extension configuration file (php 5.6)

* Wed Mar 19 2014 Remi Collet <rcollet@redhat.com> - 1.1.2-2
- allow SCL build

* Mon Nov 25 2013 Remi Collet <remi@fedoraproject.org> - 1.1.2-1
- Update to 1.1.2 (beta)

* Sat Nov 02 2013 Remi Collet <remi@fedoraproject.org> - 1.1.1-1
- Update to 1.1.1 (beta)

* Fri Oct 25 2013 Remi Collet <remi@fedoraproject.org> - 1.0.9-1
- Update to 1.0.9 (beta)

* Thu Oct 24 2013 Remi Collet <remi@fedoraproject.org> - 1.0.8-1
- Update to 1.0.8 (beta)
- run upstream test suite during build
- install tests in pecl test_dir

* Thu Oct 24 2013 Remi Collet <remi@fedoraproject.org> - 1.0.7-1
- initial package, version 1.0.7 (beta)
- open https://github.com/mkoppanen/php-zmq/pull/108
  to fix build warnings and include tests
