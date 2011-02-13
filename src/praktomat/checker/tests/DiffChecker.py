# -*- coding: utf-8 -*-

"""
Dump files containing input, expected output and the shell script running diff.
"""

import os

from django.db import models
from django.utils.translation import ugettext_lazy as _
from praktomat.checker.models import Checker, CheckerResult, execute
from praktomat.utilities.file_operations import *

class DiffChecker(Checker):

	shell_script = models.FileField(upload_to=Checker.get_storage_path, help_text=_("The shell script whose output for the given input file is compared to the given output file."))
	input_file = models.FileField(upload_to=Checker.get_storage_path, blank=True, help_text=_("The file containing the input for the program."))
	output_file = models.FileField(upload_to=Checker.get_storage_path, blank=True, help_text=_("The file containing the output for the program."))
	
	def title(self):
		""" Returns the title for this checker category. """
		return u"Ausgaben mit 'diff' prüfen."
	
	def description(self):
		""" Returns a description for this Checker. """
		return u"""Diese Prüfung wird bestanden, wenn erwartete und tatsächliche Ausgabe übereinstimmen."""
	
	def run(self, env):
		""" Runs tests in a special environment. Here's the actual work. 
		This runs the check in the environment ENV, returning a CheckerResult. """

		# Setup
		test_dir	 = env.tmpdir()
		if self.input_file: copy_file(self.input_file.path, test_dir)
		if self.output_file: copy_file(self.output_file.path, test_dir)
		copy_file_to_directory(self.shell_script.path, test_dir, replace=[(u'PROGRAM',env.program())])
		args = ["sh",  os.path.basename(self.shell_script.name)]
		environ = {}
		environ['USER'] = env.user().get_full_name()
		environ['HOME'] = test_dir
		
		(output, error) = execute(args, working_directory=test_dir, environment_variables=environ)
		
		result = CheckerResult(checker=self)
	
		result.set_log(output)
		result.set_passed(not error)
		
		return result
	

from praktomat.checker.admin import	CheckerInline

class DiffCheckerInline(CheckerInline):
	model = DiffChecker
