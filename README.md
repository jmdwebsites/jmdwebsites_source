# jmdwebsites_source.github.io

## 1. Set up

Create a site directory and add this README.md to it. Then initialize the git repository.

	$ git init

Get a .gitignore file suitable for a python project

	$ curl -o .gitignore https://raw.githubusercontent.com/github/gitignore/master/Python.gitignore

Add the following lines to .gitignore so that autosaved files are ignored
	# Other
	*(Autosaved)

Create a LICENSE.md base on BSD license

Set the user name and email just for this repository

	$ git config user.name "jmdwebsites"
	$ git config user.email me@example.com

Check that .gitignore, README.md and LICENSE.md are detected by git

	$ git status

Now,do the first commit

	$ git add .
	$ git commit -m "First commit"

And push to the master copy on github

	$ git remote add origin https://github.com/jmdwebsites/jmdwebsites_source.git
	$ git push -u origin master

Create the folder *pyapps* to store python code.

	$ mkdir pyapps
	$ cd pyapps

Setup a virtual environment locally in the project.

	$ virtualenv venv
	$ source venv/bin/activate
	$ pip install --upgrade pip

Create a pyapps directory, a setup.py, and a jmdwebsites/cli.py file with a main() function to be used as the entry point. From the pyapps directory, install the project.

	$ pip install -e .


## 2. Now create some skeleton code and website files

	Create directoryies *content* and *presentation*. Add some initial test code too. Run the skeleton app.

	$ jmdwebsites clean build
	Clean up the build.
	Build the project.

Run the test code from pyapps

	$ pytest pyapps/tests -v

The output without the preamble is

	pyapps/tests/jmdwebsites_tests/test_website.py::test_clobber_then_build PASSED
	pyapps/tests/jmdwebsites_tests/test_website.py::test_other PASSED

Or to see the stdout

	$ pytest pyapps/tests -v -s

The output without the preamble is
	
	pyapps/tests/jmdwebsites_tests/test_website.py::test_clobber_then_build
	Clobber the build removing everything.
	Build the project.
	PASSED
	pyapps/tests/jmdwebsites_tests/test_website.py::test_other
	Test other stuff!
	PASSED

Check this into git.

