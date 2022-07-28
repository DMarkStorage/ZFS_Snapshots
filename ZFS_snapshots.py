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
	# Function that will return the headers and the Auth for the API
	headers = {
		"Content-Type":"application/json",
		"Accept": "application/json",
		"X-Auth-User": 'root',
		"X-Auth-Key": 'password'

	}
	return headers

def get_args():

	usage = """
	Usage:
		try.py -s <STORAGE> -fs <FILESYSTEM> -sp <SNAPSHOT> --create
		try.py -s <STORAGE> -fs <FILESYSTEM> -sp <SNAPSHOT> --remove	
		try.py -s <STORAGE> -fs <FILESYSTEM> --list		
		try.py --version
		try.py -h | --help

	Options:
		-h --help            Show this message and exit
		-s <STORAGE>         ZFS appliance/storage name

	"""
	# version = '{} VER: {} REV: {}'.format(__program__, __version__, __revision__)
	# args = docopt(usage, version=version)
	args = docopt(usage)
	return args	



def get_projects(args, storage, filesys, snap_name):
	try:
		fs = []
		header = get_headers()
		base_url = 'https://{}:215'.format(storage)
		

		url = '{}/api/storage/v1/filesystems'.format(base_url)

		resp = requests.get(url = url, verify=False, headers = header)

		json1 = resp.json()
		data.update(json1)

		for i in data['filesystems']:
			fs.append(i['name'])


		if filesys in fs:
			for i in data['filesystems']:

				if i['name'] == filesys:
		
					pool = i['pool']
					filesys = i['name']
					project = i['project']
					# returns TRue if snap is created in the filesystem
					if args['--create']:
						newsnap(storage, pool, project, filesys, snap_name)
					# returns TRue if specific snap deleted in the filesystem
					elif args['--remove']:
						remove(storage, pool, project, filesys, snap_name)
					# returns list of snap present in the filesystem
					elif args['--list']:
						list(storage, pool, project, filesys)
					# returns TRue if specific xcp snap present in the filesystem
					elif args['--xcp']:
						find_xcp(storage, pool, project, filesys, snap_name)
					# returns TRue if xcp snap present in the filesystem
					elif args['--xcpfind']:
						find(storage, pool, project, filesys)

		else:
			print("Filesystem not Found!")

	except requests.exceptions.HTTPError as err:
		print('Cant connect to the storage!')

	except requests.exceptions.RequestException as e:  
		print('Cant connect to the storage!')


	except Exception as e:
		raise e



def list(storage, pool, project, filesys):
	data={}
	header = get_headers()
	base_url = 'https://{}:215'.format(storage)
	
	url = '''{}/api/storage/v1/pools/{}/projects/{}/filesystems/{}/snapshots'''.format(
				base_url, 
				pool,
				project,
				filesys)

	
	resp = requests.get(url = url,verify=False, headers = header)
	json1 = resp.json()
	data.update(json1)

	snaps = len(data['snapshots'])
	if snaps != 0:
		print('\n')
		print("~"*10+"List of Snapshots"+"~"*10+ "\n\t")
		list = json.dumps(data, indent = 2)
		print(list)

		# Creating csv file 
		data_ = data['snapshots']
		data_file = open('datafile.csv', 'w')
		csv_ = csv.writer(data_file)

		c = 0
		for item in data_:
			if c == 0:
				header = item.keys()
				csv_.writerow(header)
				c +=1

			csv_.writerow(item.values())
		data_file.close()

		# Creating json file
		with open('datafile.json', 'w') as outfile:
			json.dump(data_, outfile, indent = 2)

	else:
		print("No SNAPSHOT found!")

def newsnap(storage, pool, project, filesys, snap_name):
	data={}
	header = get_headers()
	base_url = 'https://{}:215'.format(storage)
	
	data1 = {
		"name" : snap_name,

	}
	json_dump = json.dumps(data1)
	url = '''{}/api/storage/v1/pools/{}/projects/{}/filesystems/{}/snapshots'''.format(
				base_url, 
				pool,
				project,
				filesys)

	
	resp = requests.post(url = url,data = json_dump, verify=False, headers = header)
	newresp = requests.get(url = url,verify=False, headers = header)
	json1 = newresp.json()
	data.update(json1)

	if resp.status_code == 201:
		print("-"*30)
		print("Snapshot "+ snap_name + " Created! on pool ("+pool+") and filesystem ("+filesys+")")

		# Creating csv file 
		data_ = data['snapshots']
		data_file = open('datafile.csv', 'w')
		csv_ = csv.writer(data_file)

		c = 0
		for item in data_:
			if c == 0:
				header = item.keys()
				csv_.writerow(header)
				c +=1

			csv_.writerow(item.values())
		data_file.close()

		# Creating json file
		with open('datafile.json', 'w') as outfile:
			json.dump(data_, outfile, indent = 2)

	if resp.status_code == 409:

		print("-"*30)
		print("Snapshot "+ snap_name + " is already on pool ("+pool+") and filesystem ("+filesys+")")

		# Creating csv file 
		data_ = data['snapshots']
		data_file = open('datafile.csv', 'w')
		csv_ = csv.writer(data_file)

		c = 0
		for item in data_:
			if c == 0:
				header = item.keys()
				csv_.writerow(header)
				c +=1

			csv_.writerow(item.values())
		data_file.close()

		# Creating json file
		with open('datafile.json', 'w') as outfile:
			json.dump(data_, outfile, indent = 2)

	else:

		# print(bool(0))
		print("-"*30)
		print("Error Creating Snapshot: \n\t -->  "+ snap_name)
		print("ERROR CODE: \n\t -->  ",resp.status_code)


def remove(storage, pool, project, filesys, snap_name):
	data1 = {}
	header = get_headers()
	base_url = 'https://{}:215'.format(storage)
	
	url = '''{}/api/storage/v1/pools/{}/projects/{}/filesystems/{}/snapshots/{}?confirm=true'''.format(
				base_url, 
				pool,
				project,
				filesys,
				snap_name)

	url1 = '''{}/api/storage/v1/pools/{}/projects/{}/filesystems/{}/snapshots'''.format(
				base_url, 
				pool,
				project,
				filesys)

	resp = requests.delete(url = url, verify=False, headers = header)
	newresp = requests.get(url = url1,verify=False, headers = header)
	json1 = newresp.json()
	data1.update(json1)
	print(resp.status_code)
	



	if resp.status_code == 204:
		print("-"*30)
		print("Snapshot "+ snap_name + " REMOVED! on pool ("+pool+") and filesystem ("+filesys+")")

		# Creating csv file 
		data_ = data1['snapshots']
		data_file = open('datafile.csv', 'w')
		csv_ = csv.writer(data_file)

		c = 0
		for item in data_:
			if c == 0:
				header = item.keys()
				csv_.writerow(header)
				c +=1

			csv_.writerow(item.values())
		data_file.close()

		# Creating json file
		with open('datafile.json', 'w') as outfile:
			json.dump(data_, outfile, indent = 2)

	else:

		print("-"*30)
		print("Error removing Snapshot: \n\t -->  "+ snap_name)
		print("ERROR CODE: \n\t -->  ",resp.status_code)



def main(args):
	storage = args['<STORAGE>']
	filesys = args['<FILESYSTEM>']
	snap_name = args['<SNAPSHOT>']

	try:
		get_projects(args, storage, filesys, snap_name)

	except Exception as e:
		raise e



if __name__ == '__main__':
	try:
		ARGS = get_args()


		main(ARGS)
	except KeyboardInterrupt:
		print('\nReceived Ctrl^C. Exiting....')
	except Exception as e:
		raise e