Name: ::package_name::
Version: ::package_version::
Release: ::package_build_version::%{?dist}
Summary: ::package_description_short::
License: ::package_licence::
URL: ::package_url::
Source0: %{name}-%{version}.tar.gz
BuildArch: ::package_architecture_el::
Requires: ::package_dependencies_el_el8::

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

%description
::package_title::
::package_description_long::

%prep
%setup -q

%build
pip3 install Cython==0.29.37
./configure --prefix=/usr
make

%install
make PREFIX=%{buildroot} install
mkdir -p %{buildroot}/usr/share/py-libzfs
install -m 644 libzfs.c %{buildroot}/usr/share/py-libzfs/libzfs.c

%changelog
* Fri Mar 08 2024 Jordan Keough <jkeough@45drives.com> 0.1.0-1
- initial release