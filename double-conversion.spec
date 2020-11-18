%define major 3
%define libname %mklibname %{name} %{major}
%define develname %mklibname %{name} -d
%define staticname %mklibname %{name} -d -s
%bcond_without static_libs # don't build static libraries

Summary:	Library providing binary-decimal and decimal-binary routines for IEEE doubles
Name:		double-conversion
Version:	3.1.5
Release:	2
License:	BSD
Group:          System/Libraries
URL:            https://github.com/google/double-conversion/
# git archive --format=tar --prefix double-conversion-2.0.1-$(date +%Y%m%d)/ HEAD | xz -vf > double-conversion-2.0.1-$(date +%Y%m%d).tar.xz
#Source0:	https://github.com/google/double-conversion/archive/%{name}-%{version}-%{gitdate}.tar.gz
Source0:	https://github.com/google/double-conversion/archive/%{name}-%{version}.tar.gz
BuildRequires:  cmake
BuildRequires:	ninja
# Patches from upstream git
Patch0:		0001-Use-standard-min-max.-102.patch
Patch1:		0002-Consistent-macro-prefix.-101.patch
Patch2:		0003-Fix-naming.-103.patch
Patch3:		0004-Split-double-conversion.-104.patch
Patch4:		0005-Split-Strtod-106.patch
Patch5:		0006-Optimise-Bignum-layout.-107.patch
Patch6:		0007-Remove-redundant-parenthesis.patch
Patch7:		0008-More-Bignum-fiddling.-108.patch
Patch8:		0009-Remove-reference-to-diy-fp.cc.patch
Patch9:		0010-Add-min-exponent-width-option-in-double-to-string-co.patch
Patch10:	0011-Add-support-for-e2k-architecture.-118.patch
Patch11:	0012-Add-support-for-microblaze.patch
Patch12:	0013-Pseiderer-add-nios2-and-xtensa-001-119.patch
Patch13:	0014-Add-wasm32-as-supported-platform-120.patch
Patch14:	0015-Add-full-license-to-test-.cc-files-missing-it.-121.patch
Patch15:	0016-Fix-strtod.cc-undefined-constants-123.patch
Patch16:	0017-Move-buffer-and-buffer_pos-down-125.patch
Patch17:	0018-Add-support-for-quiet-and-signaling-NaNs-to-the-ieee.patch
Patch18:	0019-Fix-broken-MSVC-builds.-130.patch
Patch19:	0020-Add-DOUBLE_CONVERSION_HAS_ATTRIBUTE-to-fix-warnings-.patch
Patch20:	0021-Fixes-bazel-build-for-downstream-projects.-133.patch
Patch21:	0022-test-cctest-CMakeLists.txt-Added-bigobj-for-MSVC-tes.patch
Patch22:	0023-CMakeLists.txt-Export-all-symbols-136.patch
Patch23:	0024-Fix-141-142.patch
# OpenMandriva specific
Patch100:	double-conversion-3.1.5-no-assert-on-DoubleToAscii-on-special.patch

%description
Provides binary-decimal and decimal-binary routines for IEEE doubles.
The library consists of efficient conversion routines that have been
extracted from the V8 JavaScript engine. The code has been re-factored
and improved so that it can be used more easily in other projects.

%package -n %{libname}
Summary:	Library providing binary-decimal and decimal-binary routines for IEEE doubles
Group:		System/Libraries

%description -n %{libname}
Provides binary-decimal and decimal-binary routines for IEEE doubles.
The library consists of efficient conversion routines that have been
extracted from the V8 JavaScript engine. The code has been re-factored
and improved so that it can be used more easily in other projects.

%package -n %{develname}
Summary:	Development files and headers for %{name}
Group:		Development/Other
Provides:	%{name}-devel = %{EVRD}
Requires:	%{libname} = %{EVRD}

%description -n %{develname}
Contains header files for developing applications that 
use the %{name} library.

There is extensive documentation in src/double-conversion.h.
Other examples can be found in test/cctest/test-conversions.cc.

%package -n %{staticname}
Summary:	Static library for %{name}
Group:		Development/Other
Requires:	%{develname} = %{EVRD}
Provides:	%{name}-static-devel = %{EVRD}

%description -n %{staticname}
Static %{name} library.

%prep
%autosetup -p1 -n %{name}-%{version}
# Fix up install locations
# https://github.com/floitsch/double-conversion/issues/8
sed -i -e 's,lib/,%{_lib}/,g;s,"lib","%{_lib}",g' CMakeLists.txt

%build
mkdir -p build-shared
cd build-shared
  %cmake -DBUILD_TESTING=ON ../.. -G Ninja
  %ninja_build
cd ../..

%if %{with static_libs}
mkdir  -p build-static
cd build-static
  CXXFLAGS="%{optflags} -fPIC" %cmake -DBUILD_SHARED_LIBS=NO ../.. -G Ninja
  %ninja_build
cd ../..
%endif

%install
%if %{with static_libs}
cd build-static
  %ninja_install -C build
cd -
%endif

cd build-shared
  %ninja_install -C build
cd -

%check
cd build-shared
  ctest -V
cd -

%files -n %{libname}
%{_libdir}/lib%{name}.so.%{major}*

%files -n %{develname}
%doc LICENSE README.md AUTHORS Changelog
%{_libdir}/lib%{name}.so
%{_libdir}/cmake/%{name}
%{_includedir}/%{name}

%if %{with static_libs}
%files -n %{staticname}
%{_libdir}/lib%{name}.a
%endif
