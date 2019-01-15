import tornado.web
from models import User, Contact

class BaseHandler(tornado.web.RequestHandler):
    """A class to collect common handler methods - all other handlers should
    subclass this one.
    """
    
    @property
    def db(self):
        return self.application.db
    
    @property
    def root_path(self):
        return self.application.root_path
    
    def prepare(self):
        if 'http://' in self.request.full_url() or \
            ':8080' in self.request.headers['Host'] or \
            ('X-Forwarded-Proto' in self.request.headers and \
            self.request.headers['X-Forwarded-Proto'] != 'https'):
            
            req = re.sub(r'(?:\:\d{2,4}[/]?)+', ':8443/', self.request.full_url())
            self.redirect(re.sub(r'^([^:]+)', 'https', req))
            
        self.clear_header('Server')
        self.set_header('X-FRAME-OPTIONS', 'Deny')
        self.set_header('X-XSS-Protection', '1; mode=block')
        self.set_header('X-Content-Type-Options', 'nosniff')
        self.set_header('Strict-Transport-Security', 'max-age=31536000; includeSubdomains')
    
    def render(self, template_name, **kwargs):
        kwargs["current_url"] = self.request.uri
        self.set_secure_cookie(self.application.cookie_name, self.application.cookie_sec)
        super().render(template_name, **kwargs)
    
    def get_current_user(self):
        email = self.get_secure_cookie("user")
        if email is None:
            return None
        session = self.application.session_user_db
        user = (session.query(User,Contact)
            .filter(User.id == Contact.user_id)
            .filter(Contact.email == email.decode('utf-8'))
            .first())
        return user.Contact.email
    
    def check_permission(self, action):
        user = self.get_current_user()
        admin = self.is_admin_user()
        if action in self.perm_public or (user and action in self.perm_user) or (admin and action in self.perm_admin):
            pass # ok
        else:
            self.raise403()
    
    def is_admin_user(self):
        user = self.get_current_user()
        return user and user.admin

    #def files_in_dir(self, directory):
    #    return utils.num_of_files_in_dir_rec(directory)

    def raise400(self, msg=None):
        raise tornado.web.HTTPError(400, msg or 'Invalid request')

    def raise401(self, msg=None):
        raise tornado.web.HTTPError(401, msg or 'Not enough permissions to perform this action')

    def raise403(self, msg=None):
        raise tornado.web.HTTPError(403, msg or 'Not enough permissions to perform this action')

    def raise404(self, msg=None):
        raise tornado.web.HTTPError(404, msg or 'Object not found')

    def raise422(self, msg=None):
        raise tornado.web.HTTPError(422, msg or 'Invalid request')

    def raise500(self, msg=None):
        raise tornado.web.HTTPError(500, msg or 'Something is not right')