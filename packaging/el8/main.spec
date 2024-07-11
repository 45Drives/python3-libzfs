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
echo "Starting build process..."
pip3 install Cython==0.29.35
./configure --prefix=/usr
make

%install
echo "Starting install process..."
python3 setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES

%changelog
* Thu Jul 11 2024 Jordan Keough <jkeough@45drives.com> 0.1.1-1
- Packaging for focal
* Fri May 24 2024 Jordan Keough <jkeough@45drives.com> 0.1.0-2
- updating for jammy
* Fri Mar 08 2024 Jordan Keough <jkeough@45drives.com> 0.1.0-1
- initial release