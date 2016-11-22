# jmdwebsites_source.github.io

Create a site directory and add this README.md to it. Then initialize the git repository.

	git init

Get a .gitignore file suitable for a python project

	curl -o .gitignore https://raw.githubusercontent.com/github/gitignore/master/Python.gitignore

Set the user name and email just for this repository

	git config user.name "jmdwebsites"
	git config user.email me@example.com

Check that .gitignore and README.ms are detected by git

	git status

Now,do the first commit

	git add README.md
	git commit -m "First commit"

	git remote add origin https://github.com/jmdwebsites/jmdwebsites.git
	git push -u origin master

To see if any changes have been made, use

	git status
	
	
