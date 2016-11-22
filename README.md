# jmdwebsites_source.github.io

Create a site directory and add this README.md to it. Then initialize the git repository.

	git init

Get a .gitignore file suitable for a python project

	curl -o .gitignore https://raw.githubusercontent.com/github/gitignore/master/Python.gitignore

Add the following lines to .gitignore so that autosaved files are ignored
	# Other
	*(Autosaved)


Set the user name and email just for this repository

	git config user.name "jmdwebsites"
	git config user.email me@example.com

Check that .gitignore and README.ms are detected by git

	git status

Now,do the first commit

	git add .
	git commit -m "First commit"

	git remote add origin https://github.com/jmdwebsites/jmdwebsites.git
	git push -u origin master


	
	
