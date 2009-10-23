# -*- coding: utf-8 -*-

"""
Dump files containing input, expected output and the shell script running diff.
"""

import shutil, os, subprocess
from django.conf import settings 

from django.db import models
from django.utils.translation import ugettext_lazy as _
from praktomat.checker.models import Checker, CheckerResult

class DiffChecker(Checker):
	
	upload_dir = "AdminFiles/DiffChecker/%Y%m%d%H%M%S/"
	shell_script = models.FileField(upload_to=upload_dir, help_text=_("The shell script whose output for the given input file is compared to the given output file."))
	input_file = models.FileField(upload_to=upload_dir, blank=True, help_text=_("The file containing the input for the program."))
	output_file = models.FileField(upload_to=upload_dir, blank=True, help_text=_("The file containing the output for the program."))
	
	def title(self):
		""" Returns the title for this checker category. """
		return u"Ausgaben mit 'diff' prüfen."
	
	def description(self):
		""" Returns a description for this Checker. """
		return u"""Diese Prüfung wird bestanden, wenn erwartete
		und tatsächliche Ausgabe übereinstimmen."""
	

		
	def run(self, env):
		""" Runs tests in a special environment. Here's the actual work. 
		This runs the check in the environment ENV, returning a CheckerResult. """

		# Setup
		test_dir	 = env.tmpdir()
		user_name	 = env.user().get_full_name()
		program_name = env.program()
		
		if self.input_file: shutil.copy (self.input_file.path, test_dir)
		if self.output_file: shutil.copy (self.output_file.path, test_dir)
		shutil.copy (self.shell_script.path, test_dir)
		
		# old praktomat replaced stuff and used m4:
		# if program_name:
		#	  content = string.replace(content, "PROGRAM", program_name)
		
		# Run the tests -- execute dumped shell script 'script.sh'
		args = ["sh",  os.path.basename(self.shell_script.name)]
		environ = os.environ # needs testing
		environ['USER'] = user_name
		environ['HOME'] = test_dir
		# needs timeout!
		#assert False
		(output, error) = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=test_dir, env=environ).communicate()
		
		result = CheckerResult(checker=self)
	
		#
		# FIXME: Wasn't There suposed to be a diff in a diffchecker?
		#
		result.set_log(output)
		result.set_passed(not error)
		
		return result
	
from praktomat.checker.admin import	CheckerInline

class DiffCheckerCheckerInline(CheckerInline):
	model = DiffChecker
