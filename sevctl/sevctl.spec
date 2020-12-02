%global debug_package %{nil}


Name:          sevctl
Version:       0.1.0
Release:       1%{?dist}
Summary:       Administrative utility for AMD SEV
License:       Apache-2.0
URL:           https://github.com/enarx/%{name}
ExclusiveArch: x86_64
BuildRequires: cargo, openssl-devel
# FIXME:
# Source0: https://github.com/enarx/sevctl/archive/v%{version}.tar.gz
Source0: %{name}-%{version}.tar.gz


%description
Administrative utility for AMD SEV


%prep
%setup -q


%build
cargo build --release


%install
mkdir -p %{buildroot}/usr/bin/
install -m 0755 target/release/sevctl %{buildroot}/usr/bin/sevctl


%files
/usr/bin/sevctl


%changelog
* Wed Dec 02 2020 Connor Kuehl <ckuehl@redhat.com> - 0.1.0-1
  - Initial sevctl package

