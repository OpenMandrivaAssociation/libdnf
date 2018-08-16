# (ngompa) disable rpmlint to avoid terrible cyclic dependency problem in rpm5->rpm4 + python2->python3 transition
# remove after rpm5->rpm4 transition is complete
%undefine _build_pkgcheck_set
%undefine _build_pkgcheck_srpm
%undefine _nonzero_exit_pkgcheck_terminate_build
###

# Warning: This package is synced from Mageia and Fedora!

%define libsolv_version 0.6.30-1
%define dnf_conflict 2.0.0

# Keep valgrind tests switched off for now
%bcond_with valgrind

%define major 2
%define libname %mklibname dnf %{major}
%define oldgirname %mklibname dnf-gir 1.0
%define devname %mklibname dnf -d

Summary:	Library providing simplified C and Python API to libsolv
Name:		libdnf
Version:	0.17.2
Release:	1
Group:		System/Libraries
License:	LGPLv2+
URL:		https://github.com/rpm-software-management/%{name}
Source0:	%{url}/archive/%{version}/%{name}-%{version}.tar.gz
# Fixes for upstream
Patch0:		libdnf-0.15.2-buildfix.patch

# OpenMandriva specific changes
Patch1001:	1001-Use-the-correct-sphinx-build-binary-for-Python-2-and.patch
# https://github.com/rpm-software-management/libdnf/pull/442
Patch1003:	libdnf-armdetection.patch
# Add znver1 architecture support
Patch1004:	libdnf-0.15.1-znver1.patch

BuildRequires:	cmake
BuildRequires:	libsolv-devel >= %{libsolv_version}
BuildRequires:	pkgconfig(librepo)
BuildRequires:	pkgconfig(check)
%if %{with valgrind}
BuildRequires:	valgrind
%endif
BuildRequires:	pkgconfig(gio-unix-2.0) >= 2.46.0
BuildRequires:	pkgconfig(gtk-doc)
BuildRequires:	pkgconfig(gobject-introspection-1.0)
BuildRequires:	pkgconfig(modulemd)
BuildRequires:	pkgconfig(sqlite3)
BuildRequires:	pkgconfig(json-c)
BuildRequires:	pkgconfig(cppunit)
BuildRequires:	swig
BuildRequires:	pkgconfig(rpm) >= 4.11.0
BuildRequires:	pkgconfig(popt)
BuildRequires:	pkgconfig(smartcols)
BuildConflicts:	pkgconfig(rpm) >= 5

# Bad Things(tm) happen if libdnf with armv8 detection is used
# in conjunction with a build of dnf that doesn't know about
# armv8
Conflicts:	dnf < 2.7.5-2

%description
A library providing simplified C and Python API to libsolv.

%package -n %{libname}
Summary:	Package library providing simplified interface to libsolv
Group:		System/Libraries
Requires:	%{mklibname solv 0}%{?_isa} >= %{libsolv_version}
Obsoletes:	%{oldgirname} < %{EVRD}

%description -n %{libname}
This library provides a simple interface to libsolv and is currently
used by PackageKit and rpm-ostree.

%package -n %{devname}
Summary:	Development files for %{name}
Group:		Development/C
Provides:	%{name}-devel%{?_isa} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Requires:	%{libname}%{?_isa} = %{version}-%{release}

%description -n %{devname}
Development files for %{name}.

%package -n hawkey-man
Summary:	Documentation for the hawkey Python bindings
Group:		Development/Python
BuildRequires:	python-nose
BuildRequires:	python-sphinx
BuildRequires:	python-requests
BuildRequires:	python-setuptools
# hawkey-devel prior to 0.6.4-3 had the man page
Obsoletes:	hawkey-devel < 0.6.4-3
BuildArch:	noarch

%description -n hawkey-man
Documentation for the hawkey Python bindings.

%package -n python-hawkey
Summary:	Python 3 bindings for the hawkey interface
Group:		Development/Python
BuildRequires:	pkgconfig(python3)
BuildRequires:	python-nose
Requires:	%{libname}%{?_isa} = %{version}-%{release}
Recommends:	hawkey-man = %{version}-%{release}
# Fix problem with hawkey - dnf version incompatibility
# Can be deleted for distros where only python3-dnf >= 2.0.0
Conflicts:	python3-dnf < %{dnf_conflict}
Conflicts:	python-dnf < %{dnf_conflict}

%description -n python-hawkey
Python 3 bindings for libdnf through the hawkey interface.

%package -n python-libdnf
Summary:	Python 3 bindings for libdnf
Group:		Development/Python
BuildRequires:	pkgconfig(python3)
Requires:	%{libname}%{?_isa} = %{version}-%{release}

%description -n python-libdnf
Python 3 bindings for libdnf.

%prep
%autosetup -p1

%build
%cmake -DPYTHON_DESIRED:str=3 %{!?with_valgrind:-DDISABLE_VALGRIND=1}
%make_build

%check
# The test suite doesn't automatically know to look at the "built"
# library, so we force it by creating an LD_LIBRARY_PATH
export LD_LIBRARY_PATH=%{buildroot}%{_libdir}

if [ "$(id -u)" = '0' ]; then
        cat <<ERROR 1>&2
Package tests cannot be run under superuser account.
Please build the package as non-root user.
ERROR
    exit 1
fi

make ARGS="-V" test -C build

%install
%make_install -C build

%find_lang %{name}

# if python2 bindings exist, purge them
rm -rf %{buildroot}%{_libdir}/python2.7

%files -n %{libname}
%{_libdir}/%{name}.so.%{major}

%files -n %{devname} -f %{name}.lang
%license COPYING
%doc README.md AUTHORS
%{_libdir}/%{name}.so
%{_libdir}/pkgconfig/%{name}.pc
%{_includedir}/%{name}/
%doc %{_datadir}/gtk-doc/html/%{name}/

%files -n hawkey-man
%{_mandir}/man3/hawkey.3*

%files -n python-hawkey
%{python3_sitearch}/hawkey/

%files -n python-libdnf
%{python3_sitearch}/libdnf/
