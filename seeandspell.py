# -*- coding: UTF-8 -*-

# # # # # # # # # # # # # # # # 
#
#
#			<コ:彡
#	
# 		see and spell
# 		04-08-2014
# 		n@nabilk.com
#		MIT license
# 		utility script to rename unamed files according to parent directory 
# 		+ guesses the mimetype and adds the extension to file name if there's mimetype	
#		+ extracts text from text based documents
#		
# # # # # # # # # # # # # # # # 

import os
import subprocess
import magic
import mimetypes

# _______________________________ default arguments

defaults = {
	'rootDir': '.',
	'rename': 'y',
	'guessType': 'y',
	'logging': 'y',
	'extract': False,
	'compile': 'n',
	'flag': '-t',
	'catch': 'Attachment',
	'confirm': None,
	'tikaDir': '/Applications/tika-app-1.5.jar',
	'compilefile': 'extracts.txt',
	'logfile': 'log.txt'
	}

# _______________________________ functions

# sets either default parameters or ones supplied by user and passes them to directory walk
def set_arguments(dict):

	params = [
		'rootDir',
		'rename',
		'guessType',
		'logging',
		'extract',
		'compile',
		'flag'
		]

	prompts = [
		'root directory to walk: ',
		'rename files? (y/n): ',
		'guess file type and add extension? (y/n): ',
		'create log file? (y/n): ',
		'extract plaintext and write to file? (y/n): '
		'compiled or separate plaintext extracts? (y/n): '
		'plaintext (-t) or xhtml (-x)? [-t or -x]: '
		]

	i = 0
	args = dict

	defaultcheck = input('use default parameters? (y/n): ')

	if(defaultcheck == 'n'):

		for p in params:
			args[p] = input(prompts[i])
			i+=1

	return args

# main directory walk function that calls other functions based on parameters passed to it
def see_and_spell(dict):

	i = 0
	start = os.getcwd()
	print(start)

	if dict['logging'] == 'y': fh_log = open(dict['logfile'], 'a')
	if dict['compile'] == 'y': fh_extract = open(dict['compilefile'], 'w')

	for dirpath, dirnames, filenames in os.walk(dict['rootDir']):

		print(dirpath)
		if dirpath == './_extracts': continue
		if dict['confirm'] is None:

			i+= 1
			print('folder #' + str(i) + ': ' + dirpath[1:])

		os.chdir(os.getcwd() + dirpath[1:])

		# the main event -- calls the other functions
		j = 1
		for fname in filenames:

			if fname[0] == '.' or fname == 'extracts.txt' or fname == 'log.txt' : continue

			if dict['extract'] is False:
				if dict['guessType'] == 'y':
					ext = guess_type(fname, dirpath, fh_log, dict)
					ext = '' if ext is None else ext
				else: ext = ''
				
				if dict['rename'] == 'y': rename(fname, ext, dirpath, fh_log, dict)
			
			if dict['extract'] == True:
	
				if dict['compile'] == 'n':			
					f = dirpath[2:] + '_' + str(j)
					f = f + '.html' if dict['flag'] == '-x' else f + '.txt'
					fh_extract = open(f, 'w')
				
				try: extract_text(fname, fh_extract, dict)
				except TypeError: print('whoops!')
				j+=1

		if os.getcwd() != start: os.chdir('..')

		print('\t')

	if dict['extract'] == 'y' and dict['compile'] == 'y' and dict['confirm']: fh_extract.close()

# generates a new name based on parent folder and renames if confirm boolean
def rename(filename, extension, directorypath, logfile, args):		
	# for the files that were originally called Attachment_XX
	# renames them according to parent directory	

	catch = args['catch']
	if filename[:len(catch)] == catch:
		newName = directorypath[2:] + filename[10:] + extension	
	else: 
		newName = filename + extension

	if args['confirm']: 
		logfile.write('renaming : ' + filename + '--->' + newName + '\n')
		os.rename(filename, newName)
	elif args['confirm'] is None:
		print(newName)

# guesses the mime type / returns extension
def guess_type(filename, directorypath, logfile, boolean):

	# if filename doesn't have an extension, try to guess one based on the
	# mimetype (as guessed by magic) 
	if mimetypes.guess_type(filename) == (None, None): 
		try:
			mime = magic.from_file(filename, mime=True)
			mime = str(mime)[2:-1]
			ext = str(mimetypes.guess_extension(mime, None))
			return ext

		# if it throws an error (for wrong permissions, or messed up files)
		# write it to a log
		except:
			if boolean:
				print('writing to log ...')
				logfile.write('no filetype found : ' + directorypath + '/' + filename + '\n')
			elif boolean is None:
				print('no filetype found : ' + directorypath + '/' + filename)
			return ''

# extracts plaintext and writes it to a file (if confirm boolean)
def extract_text(filename_in, extract_fileout, dict):

	b = subprocess.check_output(['java', '-jar', dict['tikaDir'], dict['flag'], '-r', filename_in])
	text_extract = b.decode('utf-8')

	prefix = filename_in if dict['flag'] == '-t' else ''

	extract_fileout.write(prefix + '\n' + text_extract)
	
	if dict['compile'] == 'n':
		extract_fileout.close()
		os.renames(extract_fileout.name, '../_extracts/' + extract_fileout.name)

# _______________________________ main


if __name__ == '__main__':
	
	args = set_arguments(defaults)

	see_and_spell(args)

	confirm = input('confirm rename? (y/n) : ')
	args['confirm'] = True if confirm == 'y' else False  

	see_and_spell(args)

	extract = input('extract text? (y/n) : ')
	args['extract'] = True if confirm == 'y' else False

	see_and_spell(args)

