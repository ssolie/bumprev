#!/usr/bin/python
#
# This script performs revision bumping using Amiga-style version strings.
# It is designed to be identical to the original bumprev tool in functionality
# but not all of the features are implemented.
#
# Compatible with Python 2.5 and higher.
# 
#
# bumprev.py - Amiga-style revision bumping tool
# Copyright (C) 2021 Steven Solie
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>

import sys
import getopt
import datetime
import os.path

# Embedded version string.
verstag = '$VER: bumprev.py 54.1 (31.1.2021)'

# Default command line arguments.
args = {
	'q': False,
	'i': "his",
	'n': None,
	'vernum': 1,
	'basename': None
}

def print_usage():
	print("Usage: bumprev.py [option] vernum basename")
	print("-q       : Only print error messages")
	print("-i       : File name suffixes to include")
	print("-n       : Name of the program")
	print("vernum   : Version number")
	print("basename : Base file name")

def parse_args():
	""" Parse command line arguments
	Returns True if successful or False on error.
	"""
	try:
		opts, files = getopt.getopt(sys.argv[1:], "qi:n:")
	except getopt.GetoptError:
		return False

	for opt, val in opts:
		if opt == '-q':
			args['q'] = True

		if opt == '-i':
			args['i'] = val

		if opt == '-n':
			args['n'] = val

	if (len(files)) != 2:
		return False
	else:
		args['vernum']   = int(files[0])
		args['basename'] = files[1]

	return True


class RevisionFile:
	""" Manipulates the revision file.
	"""
	def __init__(self, base_file_name):
		self.rev_path = base_file_name + '_rev.rev'

	def bump_revision(self):
		# Default is error.
		revision = -1

		if os.path.isfile(self.rev_path):
			try:
				file = open(self.rev_path, 'r+')
				revision = int(file.readline())
				file.seek(0)
				file.write(str(revision + 1) + '\n')
				revision += 1
			except IOError:
				print('Failed to bump ' + self.rev_path)
			finally:
				file.close()
		else:
			try:
				if not args['q']:
					print('Creating new file "' + self.rev_path + '".')

				file = open(self.rev_path, 'w')
				file.write('1\n')
				revision = 1
			except IOError:
				print('Failed to bump ' + self.rev_path)
			finally:
				file.close()

		return revision


class HFile:
	""" Generates C header revision file.
	"""
	def __init__(self, name, version, revision):
		self.name = name
		self.ver  = str(version)
		self.rev  = str(revision)
		self.out_file = None

	def putln(self, line=''):
		self.out_file.write(line + '\n')

	def codegen(self, base_file_name):
		h_path = base_file_name + '_rev.h'

		try:
			self.out_file = open(h_path, "w+")
		except IOError:
			print('Failed to open ' + h_path)
			return False

		name_ver_rev = self.name + ' ' + self.ver + '.' + self.rev
		now = datetime.date.today()
		date = str(now.day) + '.' + str(now.month) + '.' + str(now.year)

		self.putln('#define VERSION   ' + self.ver)
		self.putln('#define REVISION  ' + self.rev)
		self.putln('#define DATE      "' + date + '"')
		self.putln('#define VERS      "' + name_ver_rev + '"')
		self.putln('#define VSTRING   "' + name_ver_rev + ' (' + date + ')\\r\\n"')
		self.putln('#define VERSTAG   "\\0$VER: ' + name_ver_rev + ' (' + date + ')"')

		self.out_file.close()

		return True


class IFile:
	""" Generates 'i' assembler revision file.
	"""
	def __init__(self, name, version, revision):
		self.name = name
		self.ver  = str(version)
		self.rev  = str(revision)
		self.out_file = None

	def putln(self, line=''):
		self.out_file.write(line + '\n')

	def codegen(self, base_file_name):
		i_path = base_file_name + '_rev.i'

		try:
			self.out_file = open(i_path, "w+")
		except IOError:
			print('Failed to open ' + i_path)
			return False

		name_ver_rev = self.name + ' ' + self.ver + '.' + self.rev
		now = datetime.date.today()
		date = str(now.day) + '.' + str(now.month) + '.' + str(now.year)

		self.putln('VERSION	\tEQU ' + self.ver)
		self.putln('REVISION\tEQU ' + self.rev)
		self.putln()
		self.putln('DATE\tMACRO')
		self.putln("\t\tdc.b '" + date + "'")
		self.putln('\t\tENDM')
		self.putln()
		self.putln('VERS\tMACRO')
		self.putln("\t\tdc.b '" + name_ver_rev + "'")
		self.putln('\t\tENDM')
		self.putln()
		self.putln('VSTRING\tMACRO')
		self.putln("\t\tdc.b '" + name_ver_rev + " (" + date + ")',13,10,0")
		self.putln('\t\tENDM')
		self.putln()
		self.putln('VERSTAG\tMACRO')
		self.putln("\t\tdc.b 0,'$VER: " + name_ver_rev + " (" + date + "',0")
		self.putln('\t\tENDM')

		self.out_file.close()

		return True


class SFile:
	""" Generates 's' assembly revision file.
	"""
	def __init__(self, name, version, revision):
		self.name = name
		self.ver  = str(version)
		self.rev  = str(revision)
		self.out_file = None

	def putln(self, line=''):
		self.out_file.write(line + '\n')

	def codegen(self, base_file_name):
		s_path = base_file_name + '_rev.s'

		try:
			self.out_file = open(s_path, "w+")
		except IOError:
			print('Failed to open ' + s_path)
			return False

		name_ver_rev = self.name + ' ' + self.ver + '.' + self.rev
		now = datetime.date.today()
		date = str(now.day) + '.' + str(now.month) + '.' + str(now.year)

		self.putln('VERSION = ' + self.ver)
		self.putln('REVISION = ' + self.rev)
		self.putln()
		self.putln('.macro DATE')
		self.putln('.ascii "' + date + '"')
		self.putln('.endm')
		self.putln()
		self.putln('.macro VERS')
		self.putln('.ascii "' + name_ver_rev + '"')
		self.putln('.endm')
		self.putln()
		self.putln('.macro VSTRING')
		self.putln('.ascii "' + name_ver_rev + ' (' + date + ')"')
		self.putln('.byte 13,10,0')
		self.putln('.endm')
		self.putln()
		self.putln('.macro VERSTAG')
		self.putln('.byte 0')
		self.putln('.ascii "$VER: ' + name_ver_rev + ' (' + date + ')"')
		self.putln('.byte 0')
		self.putln('.endm')

		self.out_file.close()

		return True


if __name__ == "__main__":
	if not parse_args():
		print_usage()
		exit(1)

	# Do nothing if there is no valid output file format.
	num_files_to_bump = 0
	num_files_to_bump += args['i'].count('h')
	num_files_to_bump += args['i'].count('i')
	num_files_to_bump += args['i'].count('s')
	if num_files_to_bump == 0:
		exit(1)

	version = args['vernum']
	basename = args['basename']

	rev_file = RevisionFile(basename)
	revision = rev_file.bump_revision()
	if revision == -1:
		exit(1)

	# If no program name is specified we use the path basename instead.
	name = args['n']
	if name == None:
		name = os.path.basename(basename)

	if not args['q']:
		print('Bumped "' + name + '" to version ' + str(version) + '.' + str(revision) + '.')

	if args['i'].count('h') == 1:
		h_file = HFile(name, version, revision)
		h_file.codegen(basename)

	if args['i'].count('i') == 1:
		i_file = IFile(name, version, revision)
		i_file.codegen(basename)

	if args['i'].count('s') == 1:
		s_file = SFile(name, version, revision)
		s_file.codegen(basename)
