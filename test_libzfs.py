#!/usr/bin/env python3
"""
Smoke test for python3-libzfs.
Run on both ZFS 2.2 (Bookworm) and ZFS 2.3 (Trixie) to verify compatibility.

Usage:
    python3 test_libzfs.py          # basic import + property tests (no pool needed)
    python3 test_libzfs.py --pool POOLNAME   # full tests against a real pool
"""

import sys
import argparse
import traceback

PASS = 0
FAIL = 0


def test(name):
    """Decorator to register and run a test."""
    def decorator(func):
        func._test_name = name
        return func
    return decorator


def run_test(func, **kwargs):
    global PASS, FAIL
    try:
        func(**kwargs)
        print(f"  ✓ {func._test_name}")
        PASS += 1
    except Exception as e:
        print(f"  ✗ {func._test_name}: {e}")
        traceback.print_exc(limit=2)
        FAIL += 1


# ====================
# Import & Basic Tests
# ====================

@test("import libzfs")
def test_import(**kwargs):
    import libzfs
    assert hasattr(libzfs, 'ZFS'), "Missing ZFS class"
    assert hasattr(libzfs, 'ZFSPool'), "Missing ZFSPool class"
    assert hasattr(libzfs, 'ZFSDataset'), "Missing ZFSDataset class"
    assert hasattr(libzfs, 'ZFSException'), "Missing ZFSException class"


@test("enum classes exist")
def test_enums(**kwargs):
    import libzfs
    # These should all be importable
    assert libzfs.DatasetType.FILESYSTEM is not None
    assert libzfs.DatasetType.VOLUME is not None
    assert libzfs.DatasetType.SNAPSHOT is not None
    assert libzfs.Error.SUCCESS is not None
    assert libzfs.PropertySource.LOCAL is not None
    assert libzfs.VDevState.HEALTHY is not None
    assert libzfs.PoolState.ACTIVE is not None
    assert libzfs.ScanFunction.SCRUB is not None


@test("ZFS context manager opens/closes")
def test_context_manager(**kwargs):
    import libzfs
    with libzfs.ZFS() as zfs:
        assert zfs is not None


@test("ZFS proptypes populated")
def test_proptypes(**kwargs):
    import libzfs
    with libzfs.ZFS() as zfs:
        # proptypes should be populated for at least FILESYSTEM
        assert libzfs.DatasetType.FILESYSTEM in zfs.proptypes, "FILESYSTEM not in proptypes"
        props = zfs.proptypes[libzfs.DatasetType.FILESYSTEM]
        assert len(props) > 0, f"No properties for FILESYSTEM (got {len(props)})"
        print(f"    ({len(props)} filesystem properties detected)")


@test("validate_dataset_name works")
def test_validate_names(**kwargs):
    import libzfs
    # Valid names
    assert libzfs.validate_dataset_name("tank/data") == True
    assert libzfs.validate_dataset_name("pool/child/grandchild") == True
    # Invalid names
    assert libzfs.validate_dataset_name("") == False
    assert libzfs.validate_dataset_name("pool//double") == False


@test("validate_pool_name works")
def test_validate_pool_name(**kwargs):
    import libzfs
    assert libzfs.validate_pool_name("tank") == True
    assert libzfs.validate_pool_name("mypool") == True
    assert libzfs.validate_pool_name("mirror") == False  # reserved word


@test("ZFSException picklable (reduce)")
def test_exception_pickle(**kwargs):
    import libzfs
    import pickle
    exc = libzfs.ZFSException(libzfs.Error.NOENT, "test error")
    restored = pickle.loads(pickle.dumps(exc))
    assert str(restored) == "test error"
    assert restored.code == libzfs.Error.NOENT


# ====================
# Pool-Dependent Tests
# ====================

@test("list pools")
def test_list_pools(pool_name=None, **kwargs):
    import libzfs
    with libzfs.ZFS() as zfs:
        pools = list(zfs.pools)
        print(f"    (found {len(pools)} pools: {[p.name for p in pools]})")
        assert len(pools) >= 1, "No pools found - need at least one pool for this test"


@test("get specific pool")
def test_get_pool(pool_name=None, **kwargs):
    import libzfs
    with libzfs.ZFS() as zfs:
        pool = zfs.get(pool_name)
        assert pool.name == pool_name
        print(f"    pool={pool.name}, guid={pool.guid}")


@test("pool properties readable")
def test_pool_properties(pool_name=None, **kwargs):
    import libzfs
    with libzfs.ZFS() as zfs:
        pool = zfs.get(pool_name)
        props = pool.properties
        assert 'size' in props, "'size' not in pool properties"
        assert 'health' in props, "'health' not in pool properties"
        print(f"    size={props['size'].value}, health={props['health'].value}")
        print(f"    ({len(props)} pool properties readable)")


@test("pool status and health")
def test_pool_status(pool_name=None, **kwargs):
    import libzfs
    with libzfs.ZFS() as zfs:
        pool = zfs.get(pool_name)
        status = pool.status
        healthy = pool.healthy
        print(f"    status={status}, healthy={healthy}")
        assert status in ('ONLINE', 'DEGRADED', 'FAULTED', 'OFFLINE', 'REMOVED', 'UNAVAIL')


@test("pool vdev tree")
def test_pool_vdevs(pool_name=None, **kwargs):
    import libzfs
    with libzfs.ZFS() as zfs:
        pool = zfs.get(pool_name)
        root_vdev = pool.root_vdev
        assert root_vdev is not None
        data_vdevs = list(pool.data_vdevs)
        print(f"    root_vdev type={root_vdev.type}, data_vdevs={len(data_vdevs)}")


@test("pool scrub stats")
def test_pool_scrub(pool_name=None, **kwargs):
    import libzfs
    with libzfs.ZFS() as zfs:
        pool = zfs.get(pool_name)
        scrub = pool.scrub
        assert scrub is not None
        print(f"    scrub state={scrub.state}, function={scrub.function}")


@test("root dataset accessible")
def test_root_dataset(pool_name=None, **kwargs):
    import libzfs
    with libzfs.ZFS() as zfs:
        pool = zfs.get(pool_name)
        ds = pool.root_dataset
        assert ds is not None
        assert ds.name == pool_name
        print(f"    root_dataset={ds.name}, type={ds.type}")


@test("dataset properties readable")
def test_dataset_properties(pool_name=None, **kwargs):
    import libzfs
    with libzfs.ZFS() as zfs:
        pool = zfs.get(pool_name)
        ds = pool.root_dataset
        props = ds.properties
        assert 'mountpoint' in props
        assert 'used' in props
        assert 'available' in props
        print(f"    mountpoint={props['mountpoint'].value}")
        print(f"    used={props['used'].value}, available={props['available'].value}")


@test("dataset children iteration")
def test_dataset_children(pool_name=None, **kwargs):
    import libzfs
    with libzfs.ZFS() as zfs:
        pool = zfs.get(pool_name)
        ds = pool.root_dataset
        children = list(ds.children)
        print(f"    {len(children)} child datasets")


@test("datasets_serialized works")
def test_datasets_serialized(pool_name=None, **kwargs):
    import libzfs
    with libzfs.ZFS() as zfs:
        results = list(zfs.datasets_serialized(
            props=['mountpoint', 'used', 'available'],
            datasets=[pool_name],
            retrieve_children=True
        ))
        assert len(results) >= 1
        first = results[0]
        assert 'properties' in first
        assert 'name' in first
        print(f"    serialized {len(results)} datasets, first={first['name']}")


@test("snapshots_serialized works")
def test_snapshots_serialized(pool_name=None, **kwargs):
    import libzfs
    with libzfs.ZFS() as zfs:
        snaps = zfs.snapshots_serialized(
            props=['name', 'creation'],
            datasets=[pool_name],
            recursive=True
        )
        print(f"    {len(snaps)} snapshots found")


@test("pool asdict serialization")
def test_pool_asdict(pool_name=None, **kwargs):
    import libzfs
    with libzfs.ZFS() as zfs:
        pool = zfs.get(pool_name)
        d = pool.asdict()
        assert isinstance(d, dict)
        assert 'name' in d
        assert 'guid' in d
        assert 'groups' in d
        assert 'properties' in d
        print(f"    asdict keys: {list(d.keys())[:8]}...")


@test("get_dataset works")
def test_get_dataset(pool_name=None, **kwargs):
    import libzfs
    with libzfs.ZFS() as zfs:
        ds = zfs.get_dataset(pool_name)
        assert ds.name == pool_name


@test("find_import (scan for importable pools)")
def test_find_import(pool_name=None, **kwargs):
    import libzfs
    with libzfs.ZFS() as zfs:
        # This shouldn't crash even if no importable pools exist
        importable = list(zfs.find_import())
        print(f"    {len(importable)} importable pools found")


def main():
    global PASS, FAIL

    parser = argparse.ArgumentParser(description="python3-libzfs smoke tests")
    parser.add_argument('--pool', '-p', help='Pool name for pool-dependent tests')
    args = parser.parse_args()

    # Print environment info
    print("=" * 60)
    print("python3-libzfs Smoke Test")
    print("=" * 60)
    print(f"Python: {sys.version}")

    try:
        import libzfs
        # Try to get ZFS version from module or zpool command
        print(f"libzfs: imported successfully")
    except ImportError as e:
        print(f"FATAL: Cannot import libzfs: {e}")
        sys.exit(1)

    import subprocess
    try:
        ver = subprocess.check_output(['zfs', '--version'], text=True).strip()
        print(f"ZFS: {ver}")
    except Exception:
        print("ZFS: (could not determine version)")

    import platform
    print(f"OS: {platform.platform()}")
    print("=" * 60)

    # Basic tests (no pool required)
    print("\n[Basic Tests - no pool required]")
    basic_tests = [
        test_import, test_enums, test_context_manager,
        test_proptypes, test_validate_names, test_validate_pool_name,
        test_exception_pickle,
    ]
    for t in basic_tests:
        run_test(t)

    # Pool-dependent tests
    if args.pool:
        print(f"\n[Pool Tests - using pool '{args.pool}']")
        pool_tests = [
            test_list_pools, test_get_pool, test_pool_properties,
            test_pool_status, test_pool_vdevs, test_pool_scrub,
            test_root_dataset, test_dataset_properties,
            test_dataset_children, test_datasets_serialized,
            test_snapshots_serialized, test_pool_asdict,
            test_get_dataset, test_find_import,
        ]
        for t in pool_tests:
            run_test(t, pool_name=args.pool)
    else:
        print("\n[Pool Tests - SKIPPED (use --pool POOLNAME to enable)]")

    # Summary
    print("\n" + "=" * 60)
    total = PASS + FAIL
    print(f"Results: {PASS}/{total} passed, {FAIL} failed")
    if FAIL == 0:
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 60)

    sys.exit(0 if FAIL == 0 else 1)


if __name__ == '__main__':
    main()
