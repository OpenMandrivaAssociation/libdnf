# Warning: This package is synced from Mageia and Fedora!

%define libsolv_version 0.6.30-1
%define dnf_conflict 2.0.0

# Keep valgrind tests switched off for now
%bcond_with valgrind

%define major 1
%define girapi %{major}.0
%define libname %mklibname dnf %{major}
%define girname %mklibname dnf-gir %{girapi}
%define devname %mklibname dnf -d

Summary:	Library providing simplified C and Python API to libsolv
Name:		libdnf
Version:	0.11.1
Release:	1
Group:		System/Libraries
License:	LGPLv2+
URL:		https://github.com/rpm-software-management/%{name}
Source0:	%{url}/archive/%{version}/%{name}-%{version}.tar.gz

# Backports from upstream
Patch0001:	0001-DnfContext-DnfRepo-Add-Clean-up-for-cache-directorie.patch
Patch0002:	0002-Effectively-transform-query-into-pkgset-RhBug-150036.patch
Patch0003:	0003-Not-require-spaces-in-provides-RhBug-1480176.patch
Patch0004:	0004-fixup-Not-require-spaces-in-provides-RhBug-1480176.patch

# OpenMandriva specific changes
Patch1001:	1001-Use-the-correct-sphinx-build-binary-for-Python-2-and.patch

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
BuildRequires:	pkgconfig(rpm) >= 4.11.0
BuildConflicts:	pkgconfig(rpm) >= 5

%description
A library providing simplified C and Python API to libsolv.

%package -n %{libname}
Summary:	Package library providing simplified interface to libsolv
Group:		System/Libraries
Requires:	%{mklibname solv 0}%{?_isa} >= %{libsolv_version}

%description -n %{libname}
This library provides a simple interface to libsolv and is currently
used by PackageKit and rpm-ostree.

%package -n %{girname}
Summary:	GObject Introspection interface description for libhif
Group:		System/Libraries
Requires:	%{libname}%{?_isa} = %{version}-%{release}

%description -n %{girname}
GObject Introspection interface description for libhif.

%package -n %{devname}
Summary:	Development files for %{name}
Group:		Development/C
Provides:	%{name}-devel%{?_isa} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Requires:	%{girname}%{?_isa} = %{version}-%{release}
Requires:	%{libname}%{?_isa} = %{version}-%{release}

%description -n %{devname}
Development files for %{name}.

%package -n hawkey-man
Summary:	Documentation for the hawkey Python bindings
Group:		Development/Python
BuildRequires:	python-nose
BuildRequires:	python-sphinx
# hawkey-devel prior to 0.6.4-3 had the man page
Obsoletes:	hawkey-devel < 0.6.4-3
BuildArch:	noarch

%description -n hawkey-man
Documentation for the hawkey Python bindings.

%package -n python-hawkey
Summary:	Python 3 bindings for the hawkey interface
Group:		Development/Python
BuildRequires:	pkgconfig(python)
BuildRequires:	python-nose
Requires:	%{libname}%{?_isa} = %{version}-%{release}
Requires:	hawkey-man = %{version}-%{release}
# Fix problem with hawkey - dnf version incompatibility
# Can be deleted for distros where only python3-dnf >= 2.0.0
Conflicts:	python3-dnf < %{dnf_conflict}
Conflicts:	python-dnf < %{dnf_conflict}

%description -n python-hawkey
Python 3 bindings for libdnf through the hawkey interface.

%prep
%autosetup -p1


%build
%cmake -DPYTHON_DESIRED:str=3 %{!?with_valgrind:-DDISABLE_VALGRIND=1} -DENABLE_SOLV_URPMREORDER=1
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


%files -n %{libname}
%{_libdir}/%{name}.so.%{major}

%files -n %{girname}
%{_libdir}/girepository-1.0/Dnf-%{girapi}.typelib

%files -n %{devname}
%license COPYING
%doc README.md AUTHORS NEWS
%{_libdir}/%{name}.so
%{_libdir}/pkgconfig/%{name}.pc
%{_includedir}/%{name}/
%doc %{_datadir}/gtk-doc/html/%{name}/
%{_datadir}/gir-1.0/Dnf-*.gir

%files -n hawkey-man
%{_mandir}/man3/hawkey.3*

%files -n python-hawkey
%{python3_sitearch}/hawkey/
