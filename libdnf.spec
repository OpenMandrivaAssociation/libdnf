# Warning: This package is synced from Mageia and Fedora!

%define libsolv_version 0.7.7
%define libmodulemd_version 2.8.3
%define swig_version 3.0.12

# Keep valgrind tests switched off for now
%bcond_with valgrind

%define major 2
%define libname %mklibname dnf %{major}
%define oldgirname %mklibname dnf-gir 1.0
%define devname %mklibname dnf -d

Summary:	Library providing simplified C and Python API to libsolv
Name:		libdnf
Version:	0.45.0
Release:	1
Group:		System/Libraries
License:	LGPLv2+
URL:		https://github.com/rpm-software-management/%{name}
Source0:	%{url}/archive/%{version}/%{name}-%{version}.tar.gz
# From upstream

# OpenMandriva specific changes
Patch1002:	libdnf-0.22.0-libdl-linkage.patch
# Add znver1 architecture support
Patch1004:	libdnf-0.15.1-znver1.patch
BuildRequires:	cmake >= 3.12.1
BuildRequires:	make
BuildRequires:	pkgconfig(libsolv) >= %{libsolv_version}
BuildRequires:	pkgconfig(librepo) >= 1.11.0
BuildRequires:	pkgconfig(check)
%if %{with valgrind}
BuildRequires:	valgrind
%endif
BuildRequires:	pkgconfig(gio-unix-2.0) >= 2.46.0
BuildRequires:	pkgconfig(modulemd-2.0) >= %{libmodulemd_version}
BuildRequires:	pkgconfig(sqlite3)
BuildRequires:	pkgconfig(json-c)
BuildRequires:	pkgconfig(cppunit)
BuildRequires:	swig >= %{swig_version}
BuildRequires:	python3dist(sphinx)
BuildRequires:	pkgconfig(rpm) >= 4.11.0
BuildRequires:	pkgconfig(popt)
BuildRequires:	pkgconfig(smartcols)
BuildRequires:	pkgconfig(gpgme)
BuildRequires:	pkgconfig(zck)
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
Requires:	%{mklibname solv 1}%{?_isa} >= %{libsolv_version}
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
Requires:	pkgconfig(libsolv)
Requires:	pkgconfig(libsolvext)
Obsoletes:	hawkey-devel < 0.6.4-3

%description -n %{devname}
Development files for %{name}.

%package -n python-hawkey
Summary:	Python 3 bindings for the hawkey interface
Group:		Development/Python
BuildRequires:	pkgconfig(python3)
BuildRequires:	python-nose
Requires:	%{libname}%{?_isa} = %{version}-%{release}
# hawkey module now uses libdnf module
Requires:	python-libdnf%{?_isa} = %{version}-%{release}
# hawkey man pages are no longer built
Obsoletes:	hawkey-man < 0.22.0

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
%cmake -DPYTHON_DESIRED:FILEPATH=%{__python3} -DWITH_MAN=0 -DWITH_GTKDOC=0 %{!?with_valgrind:-DDISABLE_VALGRIND=1} -DWITH_ZCHUNK=ON
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
%dir %{_libdir}/libdnf/plugins
%doc %{_libdir}/libdnf/plugins/README

%files -n python-hawkey
%{python3_sitearch}/hawkey/

%files -n python-libdnf
%{python3_sitearch}/libdnf/
