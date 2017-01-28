#!/usr/bin/env python
#Customer Configuration Cleaner

from shutil import copyfile
import sys

#Define any() function since we're running ancient Python that doesn't have it included

try:
    any
except NameError:
    def any(s):
        for v in s:
            if v:
                return True
        return False

stores = []

def menu(): # Determine the customer, set a variable to the appropriate directory
	rancidpath = ''
	global stores
	option = 0

	print '''\n\nWhich customer needs redacted configurations?
	1. List1
	2. List2
	3. List3
	4. List4'''
	option = int(raw_input("Type a number and press Enter: "))

	if int(option) == 1:
		rancidpath = '/absolute/path/to/list1/files'
	elif int(option) == 2:
		rancidpath = '/absolute/path/to/list2/files'
	elif int(option) == 3:
		rancidpath = '/absolute/path/to/list3/files'
	elif int(option) == 4:
		rancidpath = '/absolute/path/to/list4/files'
	else:
	        print ("Invalid choice")

	#Prompt user for list of store IDs, convert to lower case

	while True:
		store = str(raw_input('Enter store ID ' + str(len(stores) + 1) + ': ').lower())
		if store == '':
			break
		stores.append(store)
        
	# Copy config files to working directory

        print '''
------------------
  Copying files
------------------
        '''

	for store in stores:
		source_path = "%s/%s" % (rancidpath, store)
		dest_path = "/some/temp/directory/%s" % store
		try:
			copyfile(source_path, dest_path)
                        print "[+] Found %s, copying" % store
		except:
			print "[-] Did not find %s" % store
	return stores

def cleanup(stores):

	print '''
------------------	
  Cleaning files
------------------
	'''

	# Define start & end points, for removing RANCID header & ending EEM scripts

	start_marker = 'config-register'
	end_marker = 'event manager session'

	# Define start & end points of certificates displayed in the configuration

	cert_start = 'certificate'
	key_start = 'key-string'
	cert_end = 'quit'

	# Define identifying marks for sensitive items we want to remove later

	sensitive_items = ['enable secret',
	'server-private',
	'password 7',
	'fingerprint',
	'license 7',
	'username admin privilege 15',
	'dnsgw.wanzilla.net',
	'snmp-server community',
	'crypto isakmp key',
	'admin secret 5',
	'tacacs-server key 7',
	'tunnel destination',
	'ip nhrp network-id',
	'ip nhrp authentication',
	'tunnel key',
	'ntp authentication-key',
	'ip host mvec',
	'enrollment url']

	for store in stores:
		try:
			infile = file('/some/temp/directory/%s' % store) # this is referenced in menu(), make it a variable?
			cleanfile = open('/some/temp/directory/%s.clean' % store, 'w') # another reference to the same working directory
		
			# Remove RANCID header, certificates/pre-shared keys, and ending EEM scripts
			# by toggling a sentinel and not printing ("erasing") when ignore = True
			for line in infile:
				ignoreLines = True
				for line in infile:
					if start_marker in line:
						ignoreLines = False
					if cert_start in line:
						ignoreLines = True
					if cert_end in line:
						ignoreLines = False
					if key_start in line:
						ignoreLines = True
					if cert_end in line:
						ignoreLines = False
					if end_marker in line:
						ignoreLines = True
					
			# Redact sensitive config statements
					if not ignoreLines:
						if any(sensitive_item in line for sensitive_item in sensitive_items):
							cleanfile.write("<removed>\n")
						if not any(sensitive_item in line for sensitive_item in sensitive_items):
							cleanfile.write(line)
			print "[+] File %s redacted" % store
		except IOError:
			print "[-] No backup configuration found for %s" % store

menu()
cleanup(stores)
