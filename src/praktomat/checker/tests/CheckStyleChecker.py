# -*- coding: utf-8 -*-

import shutil, os, re, subprocess
from django.conf import settings 

from django.db import models
from django.utils.translation import ugettext_lazy as _
from praktomat.checker.models import Checker, CheckerResult, execute
from praktomat.utilities.file_operations import *

class CheckStyleChecker(Checker):

	name = models.CharField(max_length=100, default="CheckStyle", help_text=_("Name to be displayed on the solution detail page."))
	configuration = models.TextField(help_text=_("XML configuration of CheckStyle. See http://checkstyle.sourceforge.net/"))
	
	def title(self):
		""" Returns the title for this checker category. """
		return self.name
	
	def description(self):
		""" Returns a description for this Checker. """
		return u"Runs checkstyle (http://checkstyle.sourceforge.net/)."
	

	def run(self, env):

		# Save save check configuration
		config_path = os.path.join(env.tmpdir(), "checks.xml")
		create_file(config_path, self.configuration)
		
		# Run the tests
		args = [settings.JVM, "-cp", settings.CHECKSTYLEALLJAR, "-Dbasedir=.", "com.puppycrawl.tools.checkstyle.Main", "-c", "checks.xml"] + [name for (name,content) in env.sources()]
		(output, error) = execute(args, env.tmpdir())
		
		result = CheckerResult(checker=self)
		result.set_log('<pre>' + output + '</pre>')
		
		result.set_passed(not error and not re.match('Starting audit...\nAudit done.', output) == None)
		
		return result
	
from praktomat.checker.admin import	CheckerInline

class CheckStyleCheckerInline(CheckerInline):
	model = CheckStyleChecker
