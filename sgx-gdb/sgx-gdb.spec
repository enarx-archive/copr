%global debug_package %{nil}

Name:           sgx-gdb
Version:        2.8
Release:        1%{?dist}
Summary:        Debugger for Intel SGX

License:        BSD
URL:            https://github.com/intel/linux-sgx
Source0:        https://github.com/intel/linux-sgx/archive/sgx_%{version}.tar.gz
Source1:        sgx-gdb
Patch0:         python-fixes.patch

ExclusiveArch:  x86_64

BuildRequires:  gcc
Requires:       python3

%description
Debugger for Intel SGX


%prep
%autosetup -p1 -n linux-sgx-sgx_%{version}
sed -i 's|^#!/usr/bin/env python$|#!/usr/bin/python3|' sdk/debugger_interface/linux/gdb-sgx-plugin/*.py


%build
make -C sdk/debugger_interface/linux


%install
rm -rf $RPM_BUILD_ROOT
make -C sdk/debugger_interface/linux BUILD_DIR=%{buildroot}%{_libdir}/%{name} install
rm %{buildroot}%{_libdir}/%{name}/gdb-sgx-plugin/sgx-gdb

mkdir -p %{buildroot}%{_datadir}/
mv %{buildroot}%{_libdir}/%{name}/gdb-sgx-plugin %{buildroot}%{_datadir}/%{name}

mkdir -p %{buildroot}%{_bindir}/
install -p -m 755 %{SOURCE1} %{buildroot}%{_bindir}/%{name}


%files
%{_bindir}/%{name}
%{_libdir}/%{name}/libsgx_ptrace.so
%{_datadir}/%{name}/gdb_sgx_cmd
%{_datadir}/%{name}/gdb_sgx_plugin.py
%{_datadir}/%{name}/load_symbol_cmd.py
%{_datadir}/%{name}/readelf.py
%{_datadir}/%{name}/sgx_emmt.py


%changelog
* Fri Feb 28 2020 Nathaniel McCallum <npmccallum@redhat.com> - 2.8-1
- Initial build
