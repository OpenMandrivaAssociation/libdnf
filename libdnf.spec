# Warning: This package is synced from Mageia and Fedora!

%define libsolv_version 0.7.21
%define libmodulemd_version 2.13.0
%define swig_version 3.0.12

# Keep valgrind tests switched off for now
%bcond_with valgrind

%define major 2
%define oldlibname %mklibname dnf 2
%define libname %mklibname dnf
%define oldgirname %mklibname dnf-gir 1.0
%define devname %mklibname dnf -d

Summary:	Library providing simplified C and Python API to libsolv
Name:		libdnf
Version:	0.75.0
Release:	2
Group:		System/Libraries
License:	LGPLv2+
URL:		https://github.com/rpm-software-management/libdnf
Source0:	https://github.com/rpm-software-management/libdnf/archive/%{version}/%{name}-%{version}.tar.gz
# From upstream
# [currently nothing required]

# OpenMandriva specific changes
# Add znver1 architecture support
Patch1004:	libdnf-0.15.1-znver1.patch

BuildRequires:	cmake >= 3.12.1
BuildRequires:	ninja
BuildRequires:	pkgconfig(libsolv) >= %{libsolv_version}
BuildRequires:	pkgconfig(librepo) >= 1.16.0
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
BuildRequires:	pkgconfig(zck) >= 0.9.11
BuildConflicts:	pkgconfig(rpm) >= 5
BuildRequires:	gettext

# Bad Things(tm) happen if libdnf with armv8 detection is used
# in conjunction with a build of dnf that doesn't know about
# armv8
Conflicts:	dnf < 4.3.0

%description
A library providing simplified C and Python API to libsolv.

%package -n %{libname}
Summary:	Package library providing simplified interface to libsolv
Group:		System/Libraries
Obsoletes:	%{oldgirname} < %{EVRD}
%rename %{oldlibname}

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
Provides:	python3-hawkey = %{version}-%{release}
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
Provides:	python3-libdnf = %{version}-%{release}

%description -n python-libdnf
Python 3 bindings for libdnf.

%prep
%autosetup -p1
%if %{cross_compiling}
# FIXME this should be fixed properly, but for now, this
# is the fastest way to limit the damage of an added
# -I/usr/include
sed -i -e 's/include_directories(\${GLIB/#&/g' CMakeLists.txt
sed -i -e 's/include_directories(\${JSONC/#&/g' CMakeLists.txt
sed -i -e 's/include_directories(\${REPO/#&/g' CMakeLists.txt
%global optflags %{optflags} -I%{_prefix}/%{_target_platform}/include/glib-2.0 -I%{_prefix}/%{_target_platform}/include/gio-unix-2.0 -I%{_prefix}/%{_target_platform}/%{_lib}/glib-2.0/include -I%{_prefix}/%{_target_platform}/include/libxml2 -I%{_prefix}/%{_target_platform}/include/json-c
%endif

export CMAKE_MODULE_PATH=%{_prefix}/%{_target_platform}/share/cmake/Modules
%cmake \
	-DPYTHON_DESIRED:FILEPATH=%{__python3} \
	-DWITH_MAN=0 \
	-DWITH_GTKDOC=0 \
	%{!?with_valgrind:-DDISABLE_VALGRIND=1} \
	-DWITH_ZCHUNK=ON \
%if %{cross_compiling}
	-DWITH_TESTS:BOOL=OFF \
	-DPKG_CONFIG_EXECUTABLE=%{_bindir}/pkg-config \
%endif
	-G Ninja

%build
%ninja_build -C build

%if ! %{cross_compiling}
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

ninja test -C build || :
%endif

%install
%ninja_install -C build

%find_lang %{name}

# if python2 bindings exist, purge them
rm -rf %{buildroot}%{_libdir}/python2.7

%files -n %{libname}
%{_libdir}/%{name}.so.%{major}
%dir %{_libdir}/libdnf
%dir %{_libdir}/libdnf/plugins
%doc %{_libdir}/libdnf/plugins/README

%files -n %{devname} -f %{name}.lang
%license COPYING
%doc README.md AUTHORS
%{_libdir}/%{name}.so
%{_libdir}/pkgconfig/%{name}.pc
%{_includedir}/%{name}/

%files -n python-hawkey
%{python3_sitearch}/hawkey/

%files -n python-libdnf
%{python3_sitearch}/libdnf/
%{python3_sitearch}/%{name}-*.dist-info

