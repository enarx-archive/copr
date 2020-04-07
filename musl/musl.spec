# annobin bloats static libs significantly, disable it.
#global alt_cflags %(echo "%{optflags}" | sed 's/[^ ]*annobin[^ ]* //; s/-O. /-Os /')
%undefine _annotated_build
%global alt_cflags %(echo "%{optflags}" | sed 's/-O. /-Os /')

# Use as system libc
%bcond_with system_libc

# Fedora uses multilib with /usr/lib64
# This switch changes it to multiarch, with /usr/lib/[arch]-linux-musl
# This switch only has effect if system_libc is disabled.
%bcond_with multiarch

# Fedora uses glibc as the standard libc.
# This means any packages that would use musl would be treated
# as a cross-compilation target. Cross-mode sets it up for this application.
# In cross-mode, a prefix root is created with a new child FHS area.
# This switch only has effect if system_libc is disabled.
# This switch is enabled by default.
%bcond_without crossmode


# Ensure the value is set correctly
%ifarch %{ix86}
%global _musl_target_cpu i386
%endif

%ifarch %{arm}
%global _musl_target_cpu arm
%global _musl_platform_suffix eabi
%endif

%ifarch %{mips64}
%global _musl_target_cpu mips64
%endif

%ifarch %{mips32}
%global _musl_target_cpu mips
%endif

%ifarch ppc
%global _musl_target_cpu powerpc
%endif

%ifarch %{power64}
%global _musl_target_cpu powerpc64
%endif

%ifnarch %{ix86} %{arm} %{mips} %{power64} ppc
%global _musl_target_cpu %{_target_cpu}
%endif

# Define the platform name
%global _musl_platform %{_musl_target_cpu}-linux-musl%{?_musl_platform_suffix}

# Paths to use when not set up in cross-mode
%if %{without crossmode}
# Set up alternate paths when not using as system libc
%if %{without system_libc}
# Set up libdir path for when using multilib
%if %{without multiarch}
%global _libdir %{_prefix}/%{_lib}/%{_musl_platform}
%else
# Set up libdir path for when using multiarch
%global _libdir %{_prefix}/lib/%{_musl_platform}
%endif
%global _includedir %{_prefix}/include/%{_musl_platform}
%endif
%else
# Cross-mode paths
%global _libdir %{_prefix}/%{_musl_platform}/%{_lib}
%global _includedir %{_prefix}/%{_musl_platform}/include
%endif

%if %{without multiarch}
# We need to be multilib aware
%global _syslibdir /%{_lib}
%else
%global _syslibdir /lib
%endif

Name:		musl
Version:	1.2.0
Release:	1%{?dist}
Summary:	Fully featured lightweight standard C library for Linux
License:	MIT
URL:		https://www.musl-libc.org
Source0:	%{url}/releases/%{name}-%{version}.tar.gz

BuildRequires:	gcc, make

# Fix Makefile to not use INSTALL variable so make_install macro works
Patch0:         musl-1.1.18-Makefile-rename-INSTALL-var.patch
Patch1:         musl-static-pie.patch

# musl is only for Linux
ExclusiveOS:	linux

%if %{without system_libc}
# Prevent RPM from reading non-standard paths for Provides
%global __provides_exclude_from ^%{_libdir}/.*\\.so$
%endif

%description
musl is a new C standard library to power a new generation
of Linux-based devices. It is lightweight, fast, simple,
free, and strives to be correct in the sense of standards
conformance and safety.

%package libc
Summary:	Fully featured lightweight standard C library for Linux

# This package provides musl dynamic libs too
Provides:	%{name}-libs%{?_isa} = %{version}-%{release}

%description libc
musl is a new C standard library to power a new generation
of Linux-based devices. It is lightweight, fast, simple,
free, and strives to be correct in the sense of standards
conformance and safety.

This package provides the system dynamic linker library.
It also provides the dynamic libraries for linking
programs and libraries against musl.

%package devel
Summary:	Development files for %{name}

# This package also provides the headers for using musl
Provides:	%{name}-headers%{?_isa} = %{version}-%{release}
Requires:	%{name}-libc%{?_isa} = %{version}-%{release}
%if 0%{?fedora} >= 21 || 0%{?rhel} >= 8
Suggests:	%{name}-libc-static%{?_isa} = %{version}-%{release}
%endif

%description devel
musl is a new C standard library to power a new generation
of Linux-based devices. It is lightweight, fast, simple,
free, and strives to be correct in the sense of standards
conformance and safety.

This package provides the development files for using
musl with programs and libraries.

%package libc-static
Summary:	Static link library for %{name}
Provides:	%{name}-static%{?_isa} = %{version}-%{release}
Requires:	%{name}-devel%{?_isa} = %{version}-%{release}

%description libc-static
musl is a new C standard library to power a new generation
of Linux-based devices. It is lightweight, fast, simple,
free, and strives to be correct in the sense of standards
conformance and safety.

This package provides the additional development files for
statically linking musl into programs and libraries.

%package gcc
Summary:        Wrapper for using gcc with musl
Requires:	%{name}-devel = %{version}-%{release}
Requires:	gcc

%description gcc
musl is a new C standard library to power a new generation
of Linux-based devices. It is lightweight, fast, simple,
free, and strives to be correct in the sense of standards
conformance and safety.

This package provides a wrapper around gcc to compile
programs and libraries with musl easily.

%package clang
Summary:        Wrapper for using clang with musl
Requires:	%{name}-devel = %{version}-%{release}
Requires:	clang

%description clang
musl is a new C standard library to power a new generation
of Linux-based devices. It is lightweight, fast, simple,
free, and strives to be correct in the sense of standards
conformance and safety.

This package provides a wrapper around clang to compile
programs and libraries with musl easily.


%prep
%autosetup -p1


%build
# use modified cflags defined earlier
export CFLAGS="%{alt_cflags}"

%configure --enable-debug --enable-wrapper=all
%make_build


%install
%make_install

# Write search path for dynamic linker
mkdir -p %{buildroot}%{_sysconfdir}
touch %{buildroot}%{_sysconfdir}/ld-musl-%{_musl_target_cpu}.path
cat > %{buildroot}%{_sysconfdir}/ld-musl-%{_musl_target_cpu}.path <<EOF
%{_libdir}
EOF

%if %{without multiarch}
# Write symlink for syslib to /lib64 for compatibility with Fedora standards, where applicable
mkdir -p %{buildroot}%{_syslibdir}
%if "%{_lib}" == "lib64"
ln -s /lib/ld-musl-%{_musl_target_cpu}.so.1 %{buildroot}%{_syslibdir}/ld-musl-%{_musl_target_cpu}.so.1
%endif
%endif

mkdir -p %{buildroot}%{_rpmconfigdir}/macros.d
touch %{buildroot}%{_rpmconfigdir}/macros.d/macros.musl <<EOF
%%_musl_libdir %{_libdir}
%%_musl_includedir %{_includedir}
EOF

%files libc
%license COPYRIGHT
/lib/ld-musl-%{_musl_target_cpu}.so.1
%if %{without multiarch}
%if "%{_lib}" == "lib64"
%{_syslibdir}/ld-musl-%{_musl_target_cpu}.so.1
%endif
%endif
%config(noreplace) %{_sysconfdir}/ld-musl-%{_musl_target_cpu}.path
%{_libdir}/*.so

%files devel
%license COPYRIGHT
%doc README WHATSNEW
%{_includedir}/*
%{_libdir}/*.o
%{_libdir}/*.a
%exclude %{_libdir}/libc.a
%{_rpmconfigdir}/macros.d/macros.musl

%files libc-static
%license COPYRIGHT
%{_libdir}/libc.a

%files gcc
%license COPYRIGHT
%{_bindir}/musl-gcc
%{_libdir}/musl-gcc.specs

%files clang
%license COPYRIGHT
%{_bindir}/musl-clang
%{_bindir}/ld.musl-clang


%changelog
* Tue Apr 07 2020 Nathaniel McCallum <npmccallum@redhat.com> - 1.2.0-1
- Update to 1.2.0
- Added static-pie patch
