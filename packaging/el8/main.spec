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
* Mon Nov 04 2024 Jordan Keough <jkeough@45drives.com> 1.0.0-1
- Stable Release
* Mon Oct 21 2024 Jordan Keough <jkeough@45drives.com> 0.1.3-1
- Adds trim status tracking as originally intended
* Thu Jul 11 2024 Jordan Keough <jkeough@45drives.com> 0.1.2-1
- Updating version number
* Thu Jul 11 2024 Jordan Keough <jkeough@45drives.com> 0.1.1-2
- Adds ubuntu-focal support
* Thu Jul 11 2024 Jordan Keough <jkeough@45drives.com> 0.1.1-1
- Packaging for focal
* Fri May 24 2024 Jordan Keough <jkeough@45drives.com> 0.1.0-2
- updating for jammy
* Fri Mar 08 2024 Jordan Keough <jkeough@45drives.com> 0.1.0-1
- initial release