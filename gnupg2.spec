# $Id: gnupg.spec,v 1.7 2003/12/11 14:17:11 rexdieter Exp $

Summary: GNU utility for secure communication and data storage
Name:	 gnupg2 
Epoch:	 0 
Version: 1.9.15
Release: 1%{?dist_tag}
License: GPL
Group: 	 Applications/System
Source0: ftp://ftp.gnupg.org/gcrypt/alpha/gnupg/gnupg-%{version}.tar.bz2
Source1: ftp://ftp.gnupg.org/gcrypt/alpha/gnupg/gnupg-%{version}.tar.bz2.sig
URL:	 http://www.gnupg.org/
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

Obsoletes: newpg < 0:0.9.5

Requires(post): /sbin/install-info
Requires(postun): /sbin/install-info

## gcc version in use?
BuildRequires: gcc
%define gcc_ver %(rpm -q --qf '%%{version}' gcc )
%if "%{gcc_ver}" >= "3.2.3"
%define pie 1
%endif

BuildRequires: libgcrypt-devel => 0:1.2.0
BuildRequires: libgpg-error-devel => 1.0
Requires: libgpg-error >= 1.0
BuildRequires: libassuan-devel >= 0.6.9
BuildRequires: libksba-devel >= 0:0.9.7
# to build without opensc support: --without opensc
%{!?_without_opensc:BuildRequires: opensc-devel >= 0.9}
%{!?_without_opensc:BuildRequires: pcsc-lite-devel }
%{?_without_opensc:BuildConflicts: opensc-devel }

BuildRequires: gettext
BuildRequires: openldap-devel
BuildRequires: libusb-devel
BuildRequires: pth-devel
BuildRequires: zlib-devel
BuildRequires: bzip2-devel
Buildrequires: libusb-devel
BuildRequires: docbook-utils

Requires: pinentry >= 0:0.7.1

# Should these be versioned?  -- Rex
Provides: gpg 
Provides: openpgp 

%description
GnuPG 1.9 is the future version of GnuPG; it is based on the gnupg-1.3
code and the previous newpg package.  It will eventually lead to a
GnuPG 2.0 release.  Note that GnuPG 1.3 and 1.9 are not always in sync
and thus features and bug fixes done in 1.3 are not necessary
available in 1.9.

You should use this GnuPG version if you want to use the gpg-agent or
gpgsm (the S/MIME variant of gpg).  Note that the gpg-agent is also
helpful when using the standard gpg versions (1.2.x or 1.3.x).


%prep
%setup -q -n gnupg-%{version}


%build

%{?pie:CFLAGS="$RPM_OPT_FLAGS -fPIE" ; export CFLAGS}
%{?pie:LDFLAGS="$RPM_OPT_FLAGS -pie" ; export LDFLAG}

%configure \
  --program-prefix="%{?_program_prefix}" \
  --disable-rpath 

make %{?_smp_mflags}

make check


%clean
rm -rf $RPM_BUILD_ROOT


%install
rm -rf $RPM_BUILD_ROOT

make install DESTDIR=$RPM_BUILD_ROOT

%find_lang %{name}

rm -f $RPM_BUILD_ROOT%{_infodir}/dir


%post
/sbin/install-info %{_infodir}/gnupg.info.gz %{_infodir}/dir 2>/dev/null ||:

%preun
if [ $1 -eq 0 ]; then
  /sbin/install-info --delete %{_infodir}/gnupg.info.gz %{_infodir}/dir \
    2>/dev/null ||:
fi


%files -f %{name}.lang
%defattr(-,root,root)
%doc AUTHORS COPYING ChangeLog NEWS README THANKS TODO
#attr(4755,root,root) %{_bindir}/gpg2
%{_bindir}/gpg2
%{_bindir}/gpg-agent
%{_bindir}/gpgconf
%{_bindir}/gpgsm*
%{_bindir}/gpgv2
%{_bindir}/kbxutil
%{_bindir}/sc-copykeys
%{_bindir}/scdaemon
%{_bindir}/watchgnupg
%{_sbindir}/*
%{_datadir}/gnupg
%{_libdir}/gnupg
%{_libexecdir}/*
%{_infodir}/*


%changelog
* Tue Feb  1 2005 Michael Schwendt <mschwendt[AT]users.sf.net> - 0:1.9.15-1
- Make install-info in scriptlets less noisy.

* Tue Jan 18 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.15-0.fdr.1
- 1.9.15

* Fri Jan 07 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.14-0.fdr.2
- note patch/hack to build against older ( <1.0) libgpg-error-devel

* Thu Jan 06 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.14-0.fdr.1
- 1.9.14
- enable opensc support
- BR: libassuan-devel >= 0.6.9

* Thu Oct 21 2004 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.11-0.fdr.4
- remove suid. 

* Thu Oct 21 2004 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.11-0.fdr.3
- remove Provides: newpg

* Wed Oct 20 2004 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.11-0.fdr.2
- Requires: pinentry
- gpg2 suid
- update description

* Tue Oct 19 2004 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.11-0.fdr.1
- first try 
- leave out opensc support (for now), enable --with-opensc

