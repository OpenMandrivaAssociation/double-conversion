%global optflags %{optflags} -O3

%define major 3
%define libname %mklibname %{name} %{major}
%define develname %mklibname %{name} -d
%define staticname %mklibname %{name} -d -s
%bcond_without static_libs # don't build static libraries

Summary:	Library providing binary-decimal and decimal-binary routines for IEEE doubles
Name:		double-conversion
Version:	3.3.0
Release:	1
License:	BSD
Group:		System/Libraries
URL:		https://github.com/google/double-conversion/
# git archive --format=tar --prefix double-conversion-2.0.1-$(date +%Y%m%d)/ HEAD | xz -vf > double-conversion-2.0.1-$(date +%Y%m%d).tar.xz
#Source0:	https://github.com/google/double-conversion/archive/%{name}-%{version}-%{gitdate}.tar.gz
Source0:	https://github.com/google/double-conversion/archive/%{name}-%{version}.tar.gz
BuildRequires:	cmake
BuildRequires:	ninja
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

# (tpg) strip LTO from "LLVM IR bitcode" files
check_convert_bitcode() {
    printf '%s\n' "Checking for LLVM IR bitcode"
    llvm_file_name=$(realpath ${1})
    llvm_file_type=$(file ${llvm_file_name})

    if printf '%s\n' "${llvm_file_type}" | grep -q "LLVM IR bitcode"; then
# recompile without LTO
    clang %{optflags} -fno-lto -Wno-unused-command-line-argument -x ir ${llvm_file_name} -c -o ${llvm_file_name}
    elif printf '%s\n' "${llvm_file_type}" | grep -q "current ar archive"; then
    printf '%s\n' "Unpacking ar archive ${llvm_file_name} to check for LLVM bitcode components."
# create archive stage for objects
    archive_stage=$(mktemp -d)
    archive=${llvm_file_name}
    cd ${archive_stage}
    ar x ${archive}
    for archived_file in $(find -not -type d); do
        check_convert_bitcode ${archived_file}
        printf '%s\n' "Repacking ${archived_file} into ${archive}."
        ar r ${archive} ${archived_file}
    done
    ranlib ${archive}
    cd ..
    fi
}

for i in $(find %{buildroot} -type f -name "*.[ao]"); do
    check_convert_bitcode ${i}
done

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
