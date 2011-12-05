%define provider_dir %{_libdir}/cmpi
%define tog_pegasus_version 2:2.5.1

Name:           sblim-cmpi-network
Version:        1.4.0
Release:        1%{?dist}
Summary:        SBLIM Network Instrumentation

Group:          Applications/System
License:        EPL
URL:            http://sblim.wiki.sourceforge.net/
Source0:        http://downloads.sourceforge.net/sblim/%{name}-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Patch0:         sblim-cmpi-network-1.3.8-i18n_env.patch

BuildRequires:  tog-pegasus-devel >= %{tog_pegasus_version}
BuildRequires:  sblim-cmpi-base-devel >= 1.5
Requires:       tog-pegasus >= %{tog_pegasus_version}
Requires:       sblim-cmpi-base >= 1.5

%description
Standards Based Linux Instrumentation Network Providers

%package        devel
Summary:        SBLIM Network Instrumentation Header Development Files
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}

%description    devel
SBLIM Base Network Development Package

%package        test
Summary:        SBLIM Network Instrumentation Testcases
Group:          Applications/System
Requires:       sblim-cmpi-network = %{version}-%{release}
Requires:       %{name}

%description    test
SBLIM Base Network Testcase Files for SBLIM Testsuite

%prep
%setup -q
%patch0 -p2 -b .i18n_env

%build
%ifarch s390 s390x ppc ppc64
export CFLAGS="$RPM_OPT_FLAGS -fsigned-char"
%else
export CFLAGS="$RPM_OPT_FLAGS"
%endif
%configure \
        TESTSUITEDIR=%{_datadir}/sblim-testsuite \
        CIMSERVER=pegasus \
        PROVIDERDIR=%{provider_dir}
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
make

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
# remove unused libtool files
rm -f $RPM_BUILD_ROOT/%{_libdir}/*a
rm -f $RPM_BUILD_ROOT/%{provider_dir}/*a
# shared libraries
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/ld.so.conf.d
echo "%{_libdir}/cmpi" > $RPM_BUILD_ROOT/%{_sysconfdir}/ld.so.conf.d/%{name}-%{_arch}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%docdir %{_datadir}/doc/%{name}-%{version}
%{_datadir}/%{name}
%{_datadir}/doc/%{name}-%{version}
%{_libdir}/*.so.*
%{provider_dir}/*.so
%config(noreplace) %{_sysconfdir}/ld.so.conf.d/%{name}-%{_arch}.conf

%files devel
%defattr(-,root,root,-)
%{_includedir}/*
%{_libdir}/*.so
%{_datadir}/doc/%{name}-%{version}

%files test
%defattr(-,root,root,-)
%{_datadir}/sblim-testsuite
%{_datadir}/doc/%{name}-%{version}

%pre
if [ "$1" -gt 1 ]; then
# If upgrading, deregister old version
    %{_datadir}/%{name}/provider-register.sh \
        -d -t pegasus \
        -m %{_datadir}/%{name}/Linux_Network.mof \
        -r %{_datadir}/%{name}/Linux_Network.registration \
        > /dev/null 2>&1 || :;
fi

%post
/sbin/ldconfig
if [ "$1" -ge 1 ]; then
# Register Schema and Provider
    %{_datadir}/%{name}/provider-register.sh \
        -t pegasus \
        -m %{_datadir}/%{name}/Linux_Network.mof \
        -r %{_datadir}/%{name}/Linux_Network.registration \
        > /dev/null 2>&1 || :;
fi

%preun
if [ "$1" -eq 0 ]; then
# Deregister only if not upgrading
    %{_datadir}/%{name}/provider-register.sh \
        -d -t pegasus \
        -m %{_datadir}/%{name}/Linux_Network.mof \
        -r %{_datadir}/%{name}/Linux_Network.registration \
        > /dev/null 2>&1 || :;
fi

%postun -p /sbin/ldconfig

%changelog
* Wed Jun 30 2010 Vitezslav Crhonek <vcrhonek@redhat.com> - 1.4.0-1
- Update to sblim-cmpi-network-1.4.0
- Fix sblim-cmpi-network result depends on locale settings

* Thu Aug 13 2009 Srinivas Ramanatha <srinivas_ramanatha@dell.com> - 1.3.8-2
- Modified the spec file to fix some rpmlint warnings

* Tue May 26 2009 Vitezslav Crhonek <vcrhonek@redhat.com> - 1.3.8-1
- Initial support
