# ZFS_Snapshots

ZFS_Snapshot is a simple program that `CREATE`, `LIST`, and `DELETE`  ZFS  snapshots in a specific Zfs storage filesystem


### Features
- `CREATE` a snapshot into a given Filesystem from a pool
- `DELETE` a snapshot into a given Filesystem from a pool
- Get the `LIST` of Snapshots
- Create a CSV and JSON file output containing all the snapshots
- Helpful CLI

### Requirements
- Python 3.6 or higher
- ZFS 0.8.1 or higher (untested on earlier versions)
- Install docopt

Check [install docopt](https://pypi.org/project/docopt/) for more information


### Usage Example
## Run the program


1. Creating a snapshot

```bash
ZFS_snapshots.py -s [STORAGE] -fs [FILESYSTEM] -sp [SNAPSHOT] --create
```

2. Remove a snapshot
```bash
ZFS_snapshots.py -s [STORAGE] -fs [FILESYSTEM] -sp [SNAPSHOT] --remove
```

3. GET a list of all snapshots
```bash
ZFS_snapshots.py -s [STORAGE] -fs [FILESYSTEM] --list
```
    		

4. HELP
```
ZFS_snapshots.py -h | --help
```

- [STORAGE] => name of your storage
- [FILESYSTEM] => name of your filesystem
- [SNAPSHOT] => name of the snapshot


## Release Instructions
1. Update `CHANGELOG.md` with new version

