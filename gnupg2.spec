
# Keep an eye on http://bugzilla.redhat.com/175744, in case these dirs go away or change
%if "%{?fedora}" > "3"
%define kde_scriptdir %{_sysconfdir}/kde
%else
%define kde_scriptdir %{_prefix}
%endif

# define _enable_gpg to build/include gnupg2 binary, currently disabled because:
# * currently doesn't build
# * has security issue (CVE-2006-3082)
# * upstream devs say "You shall not build the gpg part.  There is a reason why it is not
#   enabled by default"
#define _enable_gpg --enable-gpg

Summary: Utility for secure communication and data storage
Name:    gnupg2
Version: 1.9.22
Release: 2%{?dist}

License: GPL
Group:   Applications/System
#Source0: ftp://ftp.gnupg.org/gcrypt/alpha/gnupg/gnupg-%{version}.tar.bz2
#Source1: ftp://ftp.gnupg.org/gcrypt/alpha/gnupg/gnupg-%{version}.tar.bz2.sig
#use mirror(s), since the primary site hardly ever works anymore
Source0: http://mirrors.rootmode.com/ftp.gnupg.org/alpha/gnupg/gnupg-%{version}.tar.bz2
Source1: http://mirrors.rootmode.com/ftp.gnupg.org/alpha/gnupg/gnupg-%{version}.tar.bz2.sig
URL:     http://www.gnupg.org/
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
# omit broken x86_64 build 
# ExcludeArch: x86_64 

# enable auto-startup/shutdown of gpg-agent
Source10: gpg-agent-startup.sh
Source11: gpg-agent-shutdown.sh

Patch2: gnupg-1.9.16-testverbose.patch

Obsoletes: newpg < 0.9.5

Requires(post): /sbin/install-info
Requires(postun): /sbin/install-info

BuildRequires: libassuan-devel >= 0.6.10
BuildRequires: libgcrypt-devel => 1.2.0
BuildRequires: libgpg-error-devel => 1.0
BuildRequires: libksba-devel >= 0.9.15

BuildRequires: gettext
BuildRequires: openldap-devel
BuildRequires: libusb-devel
BuildRequires: pth-devel
BuildRequires: zlib-devel
BuildRequires: bzip2-devel
Buildrequires: libusb-devel
BuildRequires: docbook-utils
%if "%{?fedora}" > "3"
BuildRequires: pcsc-lite-libs
%endif

Requires: pinentry >= 0.7.1

%if "%{?_enable_gpg:1}" == "1"
Provides: gpg
Provides: openpgp
%endif

%description
GnuPG 1.9 is the future version of GnuPG; it is based on some gnupg-1.3
code and the previous newpg package.  It will eventually lead to a
GnuPG 2.0 release.  Note that GnuPG 1.4 and 1.9 are not always in sync
and thus features and bug fixes done in 1.4 are not necessarily
available in 1.9.

You should use this GnuPG version if you want to use the gpg-agent or
gpgsm (the S/MIME variant of gpg).  Note that the gpg-agent is also
helpful when using the standard gpg versions (1.4.x as well as some of
the old 1.2.x).  There are no problems installing 1.4 and 1.9
alongside; in act we suggest to do this.



%prep
%setup -q -n gnupg-%{version}

%patch2 -p1 -b .testverbose

# pcsc-lite library major: 0 in 1.2.0, 1 in 1.2.9+ (dlopen()'d in pcsc-wrapper)
# Note: this is just the name of the default shared lib to load in scdaemon,
# it can use other implementations too (including non-pcsc ones).
%if "%{?fedora}" > "3"
%global pcsclib %(basename $(ls -1 %{_libdir}/libpcsclite.so.? 2>/dev/null ) 2>/dev/null )
%else
%define pcsclib libpcsclite.so.0
%endif

sed -i -e 's/"libpcsclite\.so"/"%{pcsclib}"/' scd/{scdaemon,pcsc-wrapper}.c


%build

%configure \
  --disable-rpath \
  --disable-dependency-tracking \
  %{?_enable_gpg}

make %{?_smp_mflags}

%check ||:
## Allows for better debugability (doesn't work, fixme)
# echo "debug-allow-core-dumps" >> tests/gpgsm.conf
# (sometimes?) expect one failure (reported upstream)
make check ||:


%install
rm -rf $RPM_BUILD_ROOT

make install DESTDIR=$RPM_BUILD_ROOT

# enable auto-startup/shutdown of gpg-agent 
mkdir -p $RPM_BUILD_ROOT%{kde_scriptdir}/{env,shutdown}
install -p -m0755 %{SOURCE10} $RPM_BUILD_ROOT%{kde_scriptdir}/env/
install -p -m0755 %{SOURCE11} $RPM_BUILD_ROOT%{kde_scriptdir}/shutdown/

%find_lang %{name}

## Unpackaged files
rm -f $RPM_BUILD_ROOT%{_infodir}/dir


%post
/sbin/install-info %{_infodir}/gnupg.info %{_infodir}/dir ||:

%preun
if [ $1 -eq 0 ]; then
  /sbin/install-info --delete %{_infodir}/gnupg.info %{_infodir}/dir ||:
fi


%files -f %{name}.lang
%defattr(-,root,root,-)
%doc AUTHORS COPYING ChangeLog NEWS README THANKS TODO
%if "%{?_enable_gpg:1}" == "1"
#docs say to install suid root, but we won't, for now.
#attr(4755,root,root) %{_bindir}/gpg2
%{_bindir}/gpg2
%{_bindir}/gpgv2
%endif
%{_bindir}/gpg-connect-agent
%{_bindir}/gpg-agent
%{_bindir}/gpgconf
%{_bindir}/gpgkey2ssh
%{_bindir}/gpgparsemail
%{_bindir}/gpgsm*
%{_bindir}/kbxutil
%{_bindir}/scdaemon
%{_bindir}/watchgnupg
%{_sbindir}/*
%{_datadir}/gnupg/
%{_libdir}/gnupg/
%{_libexecdir}/*
%{_infodir}/*
%{kde_scriptdir}/env/*.sh
%{kde_scriptdir}/shutdown/*.sh


%clean
rm -rf $RPM_BUILD_ROOT


%changelog
* Tue Aug 29 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.22-2
- fc6 respin

* Fri Jul 28 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.22-1
- 1.9.22

* Thu Jun 22 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.21-3
- fix "gpg-agent not restarted after kde session crash/killed (#196327)

* Thu Jun 22 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.21-2
- 1.9.21
- omit gpg2 binary to address CVS-2006-3082 (#196190)

* Mon Mar  6 2006 Ville Skyttä <ville.skytta at iki.fi>> 1.9.20-3
- Don't hardcode pcsc-lite lib name (#184123)

* Thu Feb 16 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.20-2
- fc4+: use /etc/kde/(env|shutdown) for scripts (#175744)

* Fri Feb 10 2006 Rex Dieter <rexdieter[AT]users.sf.net>
- fc5: gcc/glibc respin

* Tue Dec 20 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.20-1
- 1.9.20

* Thu Dec 01 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.19-8
- include gpg-agent-(startup|shutdown) scripts (#136533)
- BR: libksba-devel >= 1.9.12 
- %%check: be permissive about failures (for now)

* Wed Nov 30 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.19-3
- BR: libksba-devel >= 1.9.13

* Tue Oct 11 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.19-2
- back to BR: libksba-devel = 1.9.11

* Tue Oct 11 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.19-1
- 1.9.19

* Fri Aug 26 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.18-9
- configure: NEED_KSBA_VERSION=0.9.12 -> 0.9.11

* Fri Aug 26 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.18-7
- re-enable 'make check', rebuild against (older) libksba-0.9.11

* Tue Aug  9 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.18-6
- don't 'make check' by default (regular builds pass, but FC4/5+plague fails)

* Mon Aug  8 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.18-5
- 1.9.18
- drop pth patch (--enable-gpg build fixed)
- update description (from README)

* Fri Jul  1 2005 Ville Skyttä <ville.skytta at iki.fi> - 1.9.17-1
- 1.9.17, signal info patch applied upstream (#162264).
- Patch to fix lvalue build error with gcc4 (upstream #485).
- Patch scdaemon and pcsc-wrapper to load the versioned (non-devel)
  pcsc-lite lib by default.

* Fri May 13 2005 Michael Schwendt <mschwendt[AT]users.sf.net> - 1.9.16-3
- Include upstream's patch for signal.c.

* Tue May 10 2005 Michael Schwendt <mschwendt[AT]users.sf.net> - 1.9.16-1
- Merge changes from Rex's 1.9.16-1 (Thu Apr 21):
-   opensc support unconditional
-   remove hard-coded .gz from %%post/%%postun
-   add %%check section
-   add pth patch
- Put back patch modified from 1.9.15-4 to make tests verbose
  and change signal.c to describe received signals better.

* Sun May  8 2005 Michael Schwendt <mschwendt[AT]users.sf.net>
- Drop patch0 again.

* Sun May  8 2005 Michael Schwendt <mschwendt[AT]users.sf.net> - 1.9.15-4
- Add patch0 temporarily to get some output from failing test.

* Sat May  7 2005 David Woodhouse <dwmw2@infradead.org> 1.9.15-3
- Rebuild.

* Fri Apr  7 2005 Michael Schwendt <mschwendt[AT]users.sf.net>
- rebuilt

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

