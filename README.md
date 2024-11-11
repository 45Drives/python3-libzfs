py-libzfs
======

**Python bindings for libzfs**

py-libzfs is a fairly straight-forward set of Python bindings for libzfs for ZFS on Linux and FreeBSD.


**VERSIONING**

The main branch of this repo follows the latest zfs release

Each branch is named for the zfs release that it is compatible with.
ex) branch zfs-2.2 is for zfs version 2.2.X, it will not compile for zfs-version 2.1.X and below.

This package will be versioned to match the major zfs version it is compatible with. 
ex) If running zfs-2.2.X a compatible python3-libzfs package will be called python3-libzfs-2.2.Y 


**INSTALLATION**

`./configure --prefix=/usr && make install`

**FEATURES:**
- Access to pools, datasets, snapshots, properties, pool disks
- Many others!

**QUICK HOWTO:**

`import libzfs`

Get a list of pools:

`pools = list(libzfs.ZFS().pools)`

Get help:

`help(libzfs)`


