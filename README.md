# icacls-human

Convert discretionary access control lists (DACLs) from `icacls` output into human readable language.

The current situation on a blank installation of Windows:
```cmd
C:\Windows> icacls .\system.ini
.\system.ini NT AUTHORITY\SYSTEM:(I)(F)
             BUILTIN\Administrators:(I)(F)
             BUILTIN\Users:(I)(RX)
             APPLICATION PACKAGE AUTHORITY\ALL APPLICATION PACKAGES:(I)(RX)
             APPLICATION PACKAGE AUTHORITY\ALL RESTRICTED APP PACKAGES:(I)(RX)

Successfully processed 1 files; Failed processing 0 files
```

**Nobody can read this output**, so this tool aims to clarify some of these so-called
discretionary access control lists (DACLs) of files or directories. For instance,
```console
$ python3 icacls2h.py '.\system.ini NT AUTHORITY\SYSTEM:(I)(F)'
[*] File: .\system.ini

[*] SID Name: NT AUTHORITY\SYSTEM
[*] DACL: '(I)(F)'
[*] Inheritance Rights:
        + (I): Inherit (dir-only: False)
[*] Permissions:
        + (F): Full access
```

## Installation

You can either clone this repository, copy the Python file or use the git installation
candidate via pip:
```
pip install git+https://github.com/MatrixEditor/icacls-human
```

or locally
```
pip install -ve .
```

## Usage

_icacls2h_ is a single Python file, aiming to be as small as possible and as compact as possible. There main mode of operation is to display the file and directory permissions of each user or group in human-friendly
format. Note that invalid input lines will be discarded without error notice.
```console
$ python3 icacls2h.py --help
usage: icacls2h.py [-h] [-timestamp] [-debug] [-list {basic,advanced,inheritance,all}] [-q] [-details] [DACL_STRING]

Converts icacls output to human-readable format

positional arguments:
  DACL_STRING           Input DACL string to process. If not specified, will read
                        from stdin. This string may contain multiple DACLs separated
                        by newlines.

options:
  -h, --help            show this help message and exit
  -timestamp            include timestamp in logging output
  -debug                enable debug logging
  -list {basic,advanced,inheritance,all}
                        Lists all permissions of the specified type together with their identifier.
  -q, -no-banner        disable banner / version info at startup
  -details              display more details about the converted DACLs
```

### Convert DACLs

#### From Simple String

Parses the given DACL string that optionally contains the file path and the target user or
group descriptor.
```
$ python3 icacls2h.py 'BUILTIN\Users:(I)(RX)'
[*] SID Name: BUILTIN\Users
[*] DACL: '(I)(RX)'
[*] Inheritance Rights:
        + (I): Inherit (dir-only: False)
[*] Permissions:
        + (RX): Read and execute access
```

> [!TIP]
> Hint: to get even *more* details, try using the `-details` flag.

#### From _STDIN_

Yes, this tool also supports reading DACLs from _stdin_, which means it can be used in pipes:
```
echo '.\system.ini NT AUTHORITY\SYSTEM:(I)(F)' | python3 icacls2h.py
[*] Target: .\system.ini

[*] SID Name: NT AUTHORITY\SYSTEM
[*] DACL: '(I)(F)'
[*] Inheritance Rights:
        + (I): Inherit (dir-only: False)
[*] Permissions:
        + (F): Full access
```

#### From File

Sometimes, it can be useful to display the permissions of all DACLs listed by `icacls`. Here, you can simply pipe the file contents into `icacls2h.py`:
```console
$ cat file_with_icacls_output.txt | python3 icacls2h.py
[*] File: C:\Program Files

[*] SID Name: NT SERVICE\TrustedInstaller
[*] DACL: '(F)'
[*] Permissions:
        + (F): Full access

[*] SID Name: NT AUTHORITY\SYSTEM
[*] DACL: '(OI)(CI)(IO)(F)'
[*] Inheritance Rights:
        + (OI): Object Inherit (dir-only: True)
        + (CI): Container Inherit (dir-only: True)
        + (IO): Inherit Only (dir-only: True)
[*] Permissions:
        + (F): Full access

[*] SID Name: BUILTIN\Administrators
[*] DACL: '(M)'
[*] Permissions:
        + (M): Modify access
```

### List defined Rights

Instead of decoding DACLs, you can also just print out all available rights either by category or simply all:
```console
$ python3 icalcs2h.py -list {all,basic,advanced,inheritance}
[*] Basic Rights:
ACE Name             Description
--------             -----------
F                    Full access
M                    Modify access
RX                   Read and execute access
R                    Read-only access
W                    Write-only access
```

## License

Distributed under the GNU General Public License (V3). See [License](LICENSE) for more information.