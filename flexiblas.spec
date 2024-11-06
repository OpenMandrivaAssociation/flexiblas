%define libnname  %mklibname %{name}-netlib
%define libaname  %mklibname %{name}-atlas
%define libbsname %mklibname %{name}-blis-serial
%define libbpname %mklibname %{name}-blis-threads
%define libboname %mklibname %{name}-blis-openmp
%define libosname %mklibname %{name}-openblas-serial
%define libopname %mklibname %{name}-openblas-threads
%define libooname %mklibname %{name}-openblas-openmp

%bcond system_lapack	1
%bcond blis		0
%bcond openblas		1

%bcond blas_auto	1
%bcond cblas		1
%bcond examples		1
%bcond openmp		1
%bcond lapack		1

%bcond lto		1
%bcond tests		1

%if %{with openblas}
%global default_backend openblas-openmp
%else
%global default_backend netlib
%endif
%global default_backend64 %{default_backend}64

%if %{with system_lapack}
%global lapack_system_version %(dnf info %{_lib}lapack-devel |sed -nr "s,Version.*: (.*),\\1,p")
%endif

%define major %(echo %{version} |sed -nr "s,^([^.][[:digit:]]*)\..*,\\1,p")


%if %{?__isa_bits:%{__isa_bits}}%{!?__isa_bits:32} == 64
%global arch64 1
%else
%global arch64 0
%endif

%global _description %{expand:
FlexiBLAS is a wrapper library that enables the exchange of the BLAS (Basic
Linear Algebra System) and LAPACK (Linear Algebra PACKage) implementation
used in an executable without recompiling or re-linking it.
}

Summary:	A BLAS/LAPACK wrapper library with runtime exchangeable backends
Name:		flexiblas
Version:	3.4.4
Release:	2
Group:		Sciences/Mathematics
# GPLv3 with an exception for the BLAS/LAPACK interface
# https://www.gnu.org/licenses/gpl-faq.en.html#LinkingOverControlledInterface
# libcscutils/ is LGPLv2+
# contributed/ and test/ are BSD
License:	GPLv3 with exceptions and LGPLv2+ and BSD
URL:		https://www.mpi-magdeburg.mpg.de/projects/%{name}
Source0:	https://github.com/mpimd-csc/flexiblas/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:	cmake ninja
BuildRequires:	gcc-gfortran
BuildRequires:	gomp-devel
%if %{with system_lapack}
BuildRequires:	pkgconfig(blas)
BuildRequires:	pkgconfig(lapack)
%endif
%if %{with atlas}
BuildRequires:	pkgconfig(atlas)
%endif
%if %{with blis}
BuildRequires:	blis-devel
%endif
%if %{with openblas}
BuildRequires:	pkgconfig(openblas)
%endif
BuildRequires:	util-linux

Requires:	%{name}-netlib = %{version}-%{release}

%description %_description

%files
%license COPYING COPYING.NETLIB
%doc ISSUES.md README.md CHANGELOG

#-------------------------------------------------------------------------

%package -n %{libnname}
Summary:	FlexiBLAS wrapper library
Requires:	%{name} = %{EVRD}
Requires:	%{name}-%{default_backend} = %{EVRD}
Provides:	%{name}-netlib

%description -n %{libnname} %_description
This package contains the wrapper library for the NETLIB project.

%files -n %{libnname}
%config(noreplace) %{_sysconfdir}/%{name}rc
%dir %{_sysconfdir}/%{name}rc.d
%{_sysconfdir}/%{name}rc.d/netlib.conf
%{_bindir}/%{name}
%{_libdir}/lib%{name}.so.%{major}*
%{_libdir}/lib%{name}_api.so.%{major}*
%{_libdir}/lib%{name}_mgmt.so.%{major}*
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/lib%{name}_fallback_lapack.so
%{_libdir}/%{name}/lib%{name}_netlib.so
%{_mandir}/man1/%{name}.1*
%if 0%{?arch64}
%config(noreplace) %{_sysconfdir}/%{name}64rc
%dir %{_sysconfdir}/%{name}64rc.d
%{_sysconfdir}/%{name}64rc.d/netlib.conf
%{_bindir}/%{name}64
%{_libdir}/lib%{name}64.so.%{major}*
%{_libdir}/lib%{name}64_api.so.%{major}*
%{_libdir}/lib%{name}64_mgmt.so.%{major}*
%dir %{_libdir}/%{name}64
%{_libdir}/%{name}64/lib%{name}_fallback_lapack.so
%{_libdir}/%{name}64/lib%{name}_netlib.so
%{_mandir}/man1/%{name}64.1*
%endif

#-------------------------------------------------------------------------

%package hook-profile
Summary:	FlexiBLAS profile hook plugin
Requires:	%{name} = %{EVRD}
Requires:	%{name}-netlib = %{EVRD}

%description hook-profile %_description
This package contains a plugin that enables profiling support.

%files hook-profile
%{_libdir}/%{name}/lib%{name}_hook_profile.so
%if 0%{?arch64}
%{_libdir}/%{name}64/lib%{name}_hook_profile.so
%endif

#-------------------------------------------------------------------------

%package devel
Summary:	Development headers and libraries for FlexiBLAS
Requires:	%{name} = %{EVRD}
Requires:	%{name}-netlib = %{EVRD}

%description devel %_description
This package contains the development headers and libraries.

%files devel
%license COPYING COPYING.NETLIB
%doc ISSUES.md README.md CHANGELOG
%{_includedir}/%{name}
%{_bindir}/%{name}-config
%{_libdir}/lib%{name}.so
%{_libdir}/lib%{name}_api.so
%{_libdir}/lib%{name}_mgmt.so
%{_libdir}/pkgconfig/%{name}.pc
%{_libdir}/pkgconfig/%{name}_api.pc
%if 0%{?arch64}
%{_includedir}/%{name}64
%{_bindir}/%{name}64-config
%{_libdir}/lib%{name}64.so
%{_libdir}/lib%{name}64_api.so
%{_libdir}/lib%{name}64_mgmt.so
%{_libdir}/pkgconfig/%{name}64.pc
%{_libdir}/pkgconfig/%{name}64_api.pc
%endif
%{_mandir}/man3/%{name}_*
%{_mandir}/man7/%{name}-api.7*

#-------------------------------------------------------------------------

%if %{with atlas}
%package -n %{libaname}
Summary:	FlexiBLAS wrappers for ATLAS
Requires:	%{name} = %{EVRD}
Requires:       %{name}-netlib = %{EVRD}
Provides:	%{name}-atlas

%description -n %{libaname} %_description
This package contains FlexiBLAS wrappers for the ATLAS project.

%files -n %{libaname}
%{_sysconfdir}/%{name}rc.d/atlas.conf
%{_libdir}/%{name}/lib%{name}_atlas.so
%endif

#-------------------------------------------------------------------------

%if %{with blis}
%package -n %{libbsname}
Summary:	FlexiBLAS wrappers for BLIS
Requires:	%{name} = %{EVRD}
Requires:       %{name}-netlib = %{EVRD}
Provides:	%{name}-blis-serial

%description -n %{libbsname} %_description
This package contains FlexiBLAS wrappers for the sequential library.

%files -n %{libbsname}
%{_sysconfdir}/%{name}rc.d/blis-serial.conf
%{_libdir}/%{name}/lib%{name}_blis-serial.so

#-------------------------------------------------------------------------

%package -n %{libbpname}
Summary:	FlexiBLAS wrappers for BLIS
Requires:	%{name} = %{EVRD}
Requires:       %{name}-netlib = %{EVRD}
Provides:	%{name}-blis-threads

%description -n %{libbpname} %_description
This package contains FlexiBLAS wrappers for the library.

%files -n %{libbpname}
%{_sysconfdir}/%{name}rc.d/blis-threads.conf
%{_libdir}/%{name}/lib%{name}_blis-threads.so

#-------------------------------------------------------------------------

%package -n %{libboname}
Summary:	FlexiBLAS wrappers for BLIS
Requires:	%{name} = %{EVRD}
Provides:	%{name}-netlib
Provides:	%{name}-blis-openmp

%description -n %{libboname} %_description
This package contains FlexiBLAS wrappers for the library.

%files -n %{libboname}
%{_sysconfdir}/%{name}rc.d/blis-openmp.conf
%{_libdir}/%{name}/lib%{name}_blis-openmp.so
%endif

#-------------------------------------------------------------------------

%if %{with openblas}
%package -n %{libosname}
Summary:	FlexiBLAS wrappers for OpenBLAS
Requires:	%{name} = %{EVRD}
Requires:       %{name}-netlib = %{EVRD}
Provides:	%{name}-openblas-serial

%description -n %{libosname} %_description
This package contains FlexiBLAS wrappers for the sequential library compiled
with a 32-integer interface.

%files -n %{libosname}
%{_sysconfdir}/%{name}rc.d/openblas-serial.conf
%{_libdir}/%{name}/lib%{name}_openblas-serial.so
%if 0%{?arch64}
%{_sysconfdir}/%{name}64rc.d/openblas-serial64.conf
%{_libdir}/%{name}64/lib%{name}_openblas-serial64.so
%endif

#-------------------------------------------------------------------------

%package -n %{libopname}
Summary:	FlexiBLAS wrappers for OpenBLAS
Requires:	%{name} = %{EVRD}
Requires:       %{name}-netlib = %{EVRD}
Provides:	%{name}-openblas-threads

%description -n %{libopname} %_description
This package contains FlexiBLAS wrappers for the library compiled with
threading support with a 32-integer interface.

%files -n %{libopname}
%{_sysconfdir}/%{name}rc.d/openblas-threads.conf
%{_libdir}/%{name}/lib%{name}_openblas-threads.so
%if 0%{?arch64}
%{_sysconfdir}/%{name}64rc.d/openblas-threads64.conf
%{_libdir}/%{name}64/lib%{name}_openblas-threads64.so
%endif

#-------------------------------------------------------------------------

%package -n %{libooname}
Summary:	FlexiBLAS wrappers for OpenBLAS
Requires:	%{name} = %{EVRD}
Requires:       %{name}-netlib = %{EVRD}
Provides:	%{name}-openblas-openmp

%description -n %{libooname} %_description
This package contains FlexiBLAS wrappers for the library compiled with
OpenMP support with a 32-integer interface.

%files -n %{libooname}
%{_sysconfdir}/%{name}rc.d/openblas-openmp.conf
%{_libdir}/%{name}/lib%{name}_openblas-openmp.so
%if 0%{?arch64}
%{_sysconfdir}/%{name}64rc.d/openblas-openmp64.conf
%{_libdir}/%{name}64/lib%{name}_openblas-openmp64.so
%endif
%endif

#-------------------------------------------------------------------------

%prep
%autosetup -p1

%build
#global optflags %{optflags} -fPIC -fopenmp
export CC=gcc
export CXX=g++
export FC=gfortran

%if %{with system_lapack}
rm -rf contributed
%endif

for d in build%{?arch64:{,64}}
do

	if [[ "$d" =~ "64_" ]]; then
		INTEGER8=ON
		SYS_BLAS_LIBRARY="%{_libdir}/libblas64_.so"
		SYS_LAPACK_LIBRARY="%{_libdir}/liblapack64_.so"
	elif [[ "$d" =~ "64" ]]; then
		INTEGER8=ON
		SYS_BLAS_LIBRARY="%{_libdir}/libblas64.so"
		SYS_LAPACK_LIBRARY="%{_libdir}/liblapack64.so"
	else
		INTEGER8=OFF
		SYS_BLAS_LIBRARY="%{_libdir}/libblas.so"
		SYS_LAPACK_LIBRARY="%{_libdir}/liblapack.so"
	fi

	%cmake \
		-DCMAKE_Fortran_FLAGS:STRING="$FFLAGS -frecursive" \
%if %{with atlas}
		-DEXTRA="ATLAS" \
		-DATLAS_LIBRARY="%{_libdir}/atlas/libtatlas.so;-lm;gfortran" \
%endif
		-DCBLAS:BOOL=%{?with_cblas:ON}%{?!with_cblas:OFF} \
		-DLAPACK:BOOL=%{?with_lapack:ON}%{?!with_lapack:OFF} \
%if %{with system_lapack}
		-DLAPACK_API_VERSION=%{lapack_system_version} \
		-DSYS_BLAS_LIBRARY=$SYS_BLAS_LIBRARY \
		-DSYS_LAPACK_LIBRARY=$SYS_LAPACK_LIBRARY \
%endif
		-DINTEGER8:BOOL=${INTEGER8} \
		-DLINK_OPENMP:BOOL=%{?with_openmp:ON}%{?!with_openmp:OFF} \
		-DLTO:BOOL=%{?with_lto:ON}%{?!with_lto:OFF} \
		-DEXAMPLES:BOOL=%{?with_examples:ON}%{?!with_examples:OFF} \
		-DTESTS:BOOL=%{?with_tests:ON}%{?!with_tests:OFF} \
		-GNinja
	%ninja_build
	cd ..
	mv %_vpath_builddir %_vpath_builddir-$d
done

%install
for d in build%{?arch64:{,64}}
do
	mv %_vpath_builddir-$d %_vpath_builddir
	%ninja_install -C build
	mv %_vpath_builddir %_vpath_builddir-$d

	# default backend
	if [[ "$d" =~ "64" ]]; then
		echo "default = %{default_backend64}" > %{buildroot}%{_sysconfdir}/%{name}64rc
	else
		echo "default = %{default_backend}" > %{buildroot}%{_sysconfdir}/%{name}rc
	fi
done

# remove dummy hook
rm -f %{buildroot}%{_libdir}/%{name}*/lib%{name}_hook_dummy.so

# set friendly names
rename -- serial -serial %{buildroot}%{_libdir}/%{name}*/* || true
rename -- openmp -openmp %{buildroot}%{_libdir}/%{name}*/* || true
rename -- pthread -threads %{buildroot}%{_libdir}/%{name}*/* || true
rename NETLIB netlib %{buildroot}%{_sysconfdir}/%{name}*.d/* || true
rename ATLAS atlas %{buildroot}%{_sysconfdir}/%{name}*.d/* || true
rename Blis blis %{buildroot}%{_sysconfdir}/%{name}*.d/* || true
rename OpenBLAS openblas %{buildroot}%{_sysconfdir}/%{name}*.d/* || true
rename -- Serial -serial %{buildroot}%{_sysconfdir}/%{name}*.d/* || true
rename -- OpenMP -openmp %{buildroot}%{_sysconfdir}/%{name}*.d/* || true
rename -- PThread -threads %{buildroot}%{_sysconfdir}/%{name}*.d/* || true
find %{buildroot}%{_sysconfdir}/%{name}*.d/* -type f \
	-exec sed -i 's NETLIB netlib gI' {} \;\
	-exec sed -i 's ATLAS atlas gI' {} \;\
	-exec sed -i 's Blis blis gI' {} \;\
	-exec sed -i 's OpenBLAS openblas gI' {} \;\
	-exec sed -i 's Serial -serial gI' {} \;\
	-exec sed -i 's OpenMP -openmp gI' {} \;\
	-exec sed -i 's PThread -threads gI' {} \;

%check
export CTEST_OUTPUT_ON_FAILURE=1
export FLEXIBLAS_TEST=%{buildroot}%{_libdir}/%{name}/lib%{name}_%{default_backend}.so
ctest  -C build-build test
%if 0%{?__isa_bits} == 64
export FLEXIBLAS64_TEST=%{buildroot}%{_libdir}/%{name}64/lib%{name}_%{default_backend64}.so
ctest  -C build-build64 test
%endif

