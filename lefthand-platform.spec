# TODO:
# - desc and group
# - patch mod_coffice to work properly with our apache (auth)

%define         arname          mod_coffice
%define         mod_name        coffice
%define         apxs            /usr/sbin/apxs
%define         _pkglibdir      %(%{apxs} -q LIBEXECDIR)
%define         _sysconfdir     /etc/httpd

Summary:	LeftHand 1.0 Platform
Summary(pl):	Platforma LeftHand 1.0
Name:		lefthand-platform
Version:	1.0.2
Release:	0.6
License:	GPL
Group:		niewiem
Source0:	lefthand-%{version}.tar.gz
Patch0:		%{name}-dont_chown.patch
Patch1:		%{name}-DESTDIR.patch
Patch2:		%{name}-comments.patch
Patch3:		%{name}-install.patch
URL:		http://www.lefthand.com.pl/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	texinfo
BuildRequires:	js-devel
BuildRequires:	apache(EAPI)-devel >= 1.3.12
BuildRequires:	postgresql-devel
BuildRequires:	postgresql-backend-devel
PreReq:		apache(EAPI) >= 1.3.12
Requires(post,preun):	%{apxs}
Requires(post,preun):	grep
Requires(preun):	fileutils
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
ble

%description -l pl
Platforma LeftHand 1.0 - zestaw bibliotek, narz�dzi i metodologii do
tworzenia w�a�ciwych aplikacji, typu aplikacja Firma. Platforma
zapewnia takie elementy jak, na przyk�ad, dost�p do bazy danych,
warstw� komunikacji przez Internet, system u�ytkownik�w i r�l, czy
mechanizmy kontroli bezpiecze�stwa.

%prep
%setup -q -n co
%patch0	-p1
%patch1	-p1
%patch2	-p1
%patch3	-p1

%build
LDFLAGS=' '; export LDFLAGS
%configure2_13 \
	--with-libs="%{_libdir}" \
	--with-includes="%{_includedir}/js %{_includedir} %{_includedir}/postgresql/server %{_includedir}/postgresql/internal" \
	--with-postgresql="%{_prefix}" \
	--with-postgresql-inc="%{_includedir}/postgresql" \
	--with-apachectl="%{_sbindir}/httpd " \
	--with-apachectl="/etc/rc.d/init.d/httpd" \
	--with-apache-libexecdir="%{_pkglibdir}"

%{__make} -C comodules clean
%{__make} -C coffice clean

%install
rm -rf $RPM_BUILD_ROOT
%{__make} -C comodules install DESTDIR=$RPM_BUILD_ROOT
%{__make} -C coffice install DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{_pkglibdir}
install coffice/mod_coffice.so $RPM_BUILD_ROOT%{_pkglibdir}
install config/co.conf $RPM_BUILD_ROOT%{_sysconfdir}/%{arname}.conf

%post
%{apxs} -e -a -n %{mod_name} %{_pkglibdir}/mod_%{mod_name}.so 1>&2
if [ -f %{_sysconfdir}/httpd.conf ] && \
        ! grep -q "^Include.*/%{arname}.conf" %{_sysconfdir}/httpd.conf; then
                echo "Include %{_sysconfdir}/%{arname}.conf" >>%{_sysconfdir}/httpd.conf
fi
if [ -f /var/lock/subsys/httpd ]; then
        /etc/rc.d/init.d/httpd restart 1>&2
fi

%preun
if [ "$1" = "0" ]; then
        %{apxs} -e -A -n %{mod_name} %{_pkglibdir}/mod_%{mod_name}.so 1>&2
        umask 027
        grep -E -v "^Include.*%{arname}.conf" %{_sysconfdir}/httpd.conf > \
                %{_sysconfdir}/httpd.conf.tmp
        mv -f %{_sysconfdir}/httpd.conf.tmp %{_sysconfdir}/httpd.conf
        if [ -f /var/lock/subsys/httpd ]; then
                /etc/rc.d/init.d/httpd restart 1>&2
        fi
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
#%doc ChangeLog README
%attr(755,postgres,postgres) %{_libdir}/co/fsql_catalog.so
%{_sysconfdir}/co_javascript/*.js
%{_sysconfdir}/co_modules/*.so
%{_pkglibdir}/*.so
%{_sysconfdir}/%{arname}.conf
