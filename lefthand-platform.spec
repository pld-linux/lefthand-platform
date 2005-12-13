# TODO:
# - better patch to find postgresql version by configure
# - group
# - move some files from /etc/httpd

%define		arname		mod_coffice
%define		mod_name	coffice
%define		apxs		/usr/sbin/apxs
%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR)
%define		_sysconfdir	/etc/httpd

Summary:	LeftHand 1.1 Platform
Summary(pl):	Platforma LeftHand 1.1
Name:		lefthand-platform
Version:	1.1
Release:	0.3
License:	GPL
Group:		Applications/WWW
# extracted from
# http://www.lefthand.com.pl/download/firma/lefthand-1.1-all.tar.gz
Source0:	lefthand-%{version}.tar.gz
# Source0-md5:	cba23742c2fdde1a77288ff524516450
Patch0:		%{name}-dont_chown.patch
Patch1:		%{name}-DESTDIR.patch
Patch2:		%{name}-comments.patch
Patch3:		%{name}-install.patch
Patch4:		%{name}-ac_fix_postgres.patch
#Patch5:		%{name}-mod_coffice.patch
Patch6:		%{name}-postgresql.patch
URL:		http://www.lefthand.com.pl/
BuildRequires:	apache(EAPI)-devel >= 1.3.12
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	js-devel
BuildRequires:	postgresql-backend-devel
BuildRequires:	postgresql-devel
BuildRequires:	texinfo
Requires(post,preun):	%{apxs}
Requires(post,preun):	grep
Requires(preun):	fileutils
Requires:	apache(EAPI) >= 1.3.12
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
LeftHand Platform 1.1 is a set of libraries, utilities and
metodologies designed for creating applications like Firma. The
platform provides features like database access, Internet
communication layer, users and roles system and security control
mechanisms.

%description -l pl
Platforma LeftHand 1.1 - zestaw bibliotek, narzêdzi i metodologii do
tworzenia w³a¶ciwych aplikacji, typu aplikacja Firma. Platforma
zapewnia takie elementy jak, na przyk³ad, dostêp do bazy danych,
warstwê komunikacji przez Internet, system u¿ytkowników i ról, czy
mechanizmy kontroli bezpieczeñstwa.

%prep
%setup -q -n co
%patch0	-p1
%patch1	-p1
%patch2	-p1
%patch3	-p1
%patch4	-p1
#%patch5	-p1
%patch6	-p1

%build
%{__aclocal}
%{__autoconf}
LDFLAGS=' '; export LDFLAGS
%configure \
	--with-libs="%{_libdir}" \
	--with-includes="%{_includedir}/js %{_includedir} %{_includedir}/postgresql/server %{_includedir}/postgresql/internal" \
	--with-postgresql="%{_prefix}" \
	--with-postgresql-inc="%{_includedir}/postgresql" \
	--with-apachectl="%{_sbindir}/httpd " \
	--with-apachectl="/etc/rc.d/init.d/httpd" \
	--with-apache-libexecdir="%{_pkglibdir}" \
	--with-database="http"

#%{__make} -C comodules clean
#%{__make} -C coffice clean

%install
rm -rf $RPM_BUILD_ROOT
%{__make} -C comodules install DESTDIR="$RPM_BUILD_ROOT"
%{__make} -C coffice install DESTDIR="$RPM_BUILD_ROOT"

install -d $RPM_BUILD_ROOT{%{_pkglibdir},%{_includedir}/co,/opt/co/html,/opt/co/datafiles/sys/attachment,/opt/co/datafiles/sys/text_document}
install coffice/mod_coffice.so $RPM_BUILD_ROOT%{_pkglibdir}
install config/co.conf $RPM_BUILD_ROOT%{_sysconfdir}/%{arname}.conf
install include/*.h $RPM_BUILD_ROOT%{_includedir}/co
cp -a http_root/* $RPM_BUILD_ROOT/opt/co/html
cd $RPM_BUILD_ROOT%{_sysconfdir}
ln -sf ../../opt/co/html co_root
ln -sf ../../opt/co/datafiles co_data

%clean
rm -rf $RPM_BUILD_ROOT

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

%files
%defattr(644,root,root,755)
#%doc sql
%dir %{_libdir}/co
%attr(755,postgres,postgres) %{_libdir}/co/fsql_catalog.so
%dir %{_sysconfdir}/co_javascript
%{_sysconfdir}/co_javascript/*.js
%dir %{_sysconfdir}/co_modules
%{_sysconfdir}/co_modules/*.so
%{_sysconfdir}/co_root
%{_sysconfdir}/co_data
%{_pkglibdir}/*.so
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{arname}.conf
# FIXME: FHS
#/sql
%{_includedir}/co
%dir /opt/co
%dir /opt/co/datafiles
%dir /opt/co/datafiles/sys
%attr(755,http,http) /opt/co/datafiles/sys/attachment
%attr(755,http,http) /opt/co/datafiles/sys/text_document
/opt/co/html
