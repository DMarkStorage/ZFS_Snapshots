import requests
import json
import os
from docopt import docopt
import traceback
import csv

requests.packages.urllib3.disable_warnings()

__version__ = '1.0'
__revision__ = '20190626'
__deprecated__ = False

data = {}

def get_headers():
    """Returns the headers and the authentication for the API."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Auth-User": 'root',
        "X-Auth-Key": 'password'
    }
    return headers

def get_args():
    """Parse and return command-line arguments."""
    usage = """
    Usage:
        ZFS_snapshots.py -s <STORAGE> -fs <FILESYSTEM> -sp <SNAPSHOT> --create
        ZFS_snapshots.py -s <STORAGE> -fs <FILESYSTEM> -sp <SNAPSHOT> --remove    
        ZFS_snapshots.py -s <STORAGE> -fs <FILESYSTEM> --list        
        ZFS_snapshots.py --version
        ZFS_snapshots.py -h | --help

    Options:
        -h --help          Show this message and exit
        -s <STORAGE>       ZFS appliance/storage name
    """
    return docopt(usage)

def get_projects(args, storage, filesys, snap_name):
    """Retrieve projects and handle snapshot creation, removal, listing, and checks."""
    try:
        header = get_headers()
        base_url = f'https://{storage}:215'
        url = f'{base_url}/api/storage/v1/filesystems'

        resp = requests.get(url=url, verify=False, headers=header)
        resp.raise_for_status()
        
        data.update(resp.json())
        filesystems = [fs['name'] for fs in data['filesystems']]

        if filesys in filesystems:
            for fs in data['filesystems']:
                if fs['name'] == filesys:
                    pool = fs['pool']
                    project = fs['project']

                    if args['--create']:
                        newsnap(storage, pool, project, filesys, snap_name)
                    elif args['--remove']:
                        remove(storage, pool, project, filesys, snap_name)
                    elif args['--list']:
                        list_snapshots(storage, pool, project, filesys)
                    elif args.get('--xcp'):
                        find_xcp(storage, pool, project, filesys, snap_name)
                    elif args.get('--xcpfind'):
                        find(storage, pool, project, filesys)
        else:
            print("Filesystem not found!")

    except requests.exceptions.HTTPError:
        print('Cannot connect to the storage!')
    except Exception as e:
        traceback.print_exc()

def list_snapshots(storage, pool, project, filesys):
    """List snapshots for a given filesystem and save them to CSV and JSON."""
    try:
        header = get_headers()
        base_url = f'https://{storage}:215'
        url = f'{base_url}/api/storage/v1/pools/{pool}/projects/{project}/filesystems/{filesys}/snapshots'

        resp = requests.get(url=url, verify=False, headers=header)
        data = resp.json()

        snapshots = data.get('snapshots', [])
        if snapshots:
            print("\n" + "~" * 10 + " List of Snapshots " + "~" * 10 + "\n")
            print(json.dumps(data, indent=2))

            with open('datafile.csv', 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(snapshots[0].keys())
                for snap in snapshots:
                    csv_writer.writerow(snap.values())

            with open('datafile.json', 'w') as jsonfile:
                json.dump(snapshots, jsonfile, indent=2)
        else:
            print("No snapshots found!")
    except Exception as e:
        traceback.print_exc()

def newsnap(storage, pool, project, filesys, snap_name):
    """Create a new snapshot."""
    try:
        header = get_headers()
        base_url = f'https://{storage}:215'
        url = f'{base_url}/api/storage/v1/pools/{pool}/projects/{project}/filesystems/{filesys}/snapshots'
        data = {"name": snap_name}

        resp = requests.post(url=url, data=json.dumps(data), verify=False, headers=header)

        if resp.status_code == 201:
            print(f"Snapshot {snap_name} created on pool {pool} and filesystem {filesys}.")
            list_snapshots(storage, pool, project, filesys)
        elif resp.status_code == 409:
            print(f"Snapshot {snap_name} already exists on pool {pool} and filesystem {filesys}.")
            list_snapshots(storage, pool, project, filesys)
        else:
            print(f"Error creating snapshot: {resp.status_code}")
    except Exception as e:
        traceback.print_exc()

def remove(storage, pool, project, filesys, snap_name):
    """Remove a snapshot."""
    try:
        header = get_headers()
        base_url = f'https://{storage}:215'
        url = f'{base_url}/api/storage/v1/pools/{pool}/projects/{project}/filesystems/{filesys}/snapshots/{snap_name}?confirm=true'

        resp = requests.delete(url=url, verify=False, headers=header)

        if resp.status_code == 204:
            print(f"Snapshot {snap_name} removed from pool {pool} and filesystem {filesys}.")
            list_snapshots(storage, pool, project, filesys)
        else:
            print(f"Error removing snapshot: {resp.status_code}")
    except Exception as e:
        traceback.print_exc()

def main(args):
    """Main function to manage snapshots."""
    storage = args['<STORAGE>']
    filesys = args['<FILESYSTEM>']
    snap_name = args.get('<SNAPSHOT>', '')

    try:
        get_projects(args, storage, filesys, snap_name)
    except Exception as e:
        traceback.print_exc()

if __name__ == '__main__':
    try:
        args = get_args()
        main(args)
    except KeyboardInterrupt:
        print("\nReceived Ctrl^C. Exiting...")
    except Exception as e:
        traceback.print_exc()
