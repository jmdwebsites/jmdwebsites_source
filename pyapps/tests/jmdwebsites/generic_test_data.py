'''\
Changing this file may impact multiple tests! Be careful.
'''

from jmdwebsites.orderedyaml import CommentedMap


vars = CommentedMap([
    ('lang', 'en'), 
    ('charset', 'utf-8'), 
    ('robots', 'noindex'), 
    ('stylesheet', '/page.css')])


data = CommentedMap([
    ('website', 'My Web Site'), 
    ('author', 'jmdwebsites')])


content = CommentedMap([
    ('title', 'Home Page'), 
    ('article', 'This is some article text ...')])


spec = CommentedMap([
    ('vars', vars), 
    ('content', content), 
    ('data', data)]) 
