import jinja2
from ...tool import *
from ...tool.Request import *


class Core(object):

    def __init__(self):
        self.request = Request()
        self.module = 'index'
        self.app = 'index'
        self.act = 'index'
        path = self.request.path().strip('/')
        if len(path) > 0:
            paths = path.split('/')
            self.module = paths[0].lower()
            if len(paths) > 1 and len(paths[1]) > 0:
                self.app = paths[1].lower()
                if len(paths) > 2 and len(paths[2]) > 0:
                    self.act = paths[2].lower()

    def render(self, data, template=''):
        if len(template) == 0:
            template = '%s/%s/%s.html' % (self.module, self.app, self.act)
        else:
            template = template.strip('/').rstrip('.html')
            if '/' not in template:
                template = '%s/%s/%s.html' % (self.module, self.app, template)
            elif template.count('/') == 1:
                template = '%s/%s.html' % (self.module, template)
        try:
            return render_template(template, **data)
        except jinja2.exceptions.TemplateSyntaxError as e:
            print(str(e))
        except jinja2.exceptions.TemplateNotFound:
            return None
        return None
