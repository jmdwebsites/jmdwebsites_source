import os

import sass

from .error import JmdwebsitesError, PathNotFoundError


class SassError(JmdwebsitesError): pass


def build_css(source_file, target_file, use_cmdline=False, use_string=False):
    if use_cmdline:
        sass_cmdline = "sass23 {0} {1}".format(source_file, target_file)
        error_code = os.system(sass_cmdline)
        if error_code:
            raise SassError('Error code: %s' % error_code)
        return
    if use_string:
        source_sass = source_file.read_text(encoding='utf-8') 
        compiled_css = sass.compile(string=source_sass, include_paths=(source_file.dirname,))
    else:
        compiled_css = sass.compile(filename=source_file.strpath)
    stylesheet_text = '@charset "UTF-8";\n' + compiled_css
    target_file.write_text(stylesheet_text, ensure=True, encoding='utf-8')
