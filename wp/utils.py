import traceback
import xmlrpclib
import time
from time import mktime
from datetime import datetime

from django.template.defaultfilters import register # noqa
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from horizon import exceptions

from wp.post.post import Post


WORDPRESS_XMLRPC_URL = settings.WORDPRESS_XMLRPC_URL
WORDPRESS_USERNAME = settings.WORDPRESS_USERNAME
WORDPRESS_PASSWORD = settings.WORDPRESS_PASSWORD

def get_posts(self):
    try:
        server = xmlrpclib.ServerProxy(WORDPRESS_XMLRPC_URL)
        posts = server.wp.getPosts(0,WORDPRESS_USERNAME,WORDPRESS_PASSWORD)

        for post in posts:
            post['id'] = post['post_id']

        return [Post(**p) for p in posts]

    except:
        exceptions.handle(self.request,
                          _('Unable to retrieve list of posts.'))
        return []


def create_post(self, request, context):
    try:

        title = context.get('post_title')
        content = context.get('post_content')
        status = 'publish'

        server = xmlrpclib.ServerProxy(WORDPRESS_XMLRPC_URL)

        data = {'post_title': title, 'post_content': content, 'post_status': status}
        post_id = server.wp.newPost(0, WORDPRESS_USERNAME, WORDPRESS_PASSWORD, data)
        return post_id

    except:
        print "Exception inside utils.create_post"
        print traceback.format_exc()
        exceptions.handle(self.request,
                          _('Unable to create new post.'))
        return []


def delete_post(self, post_id):
    try:
        server = xmlrpclib.ServerProxy(WORDPRESS_XMLRPC_URL)
        return server.wp.deletePost(0, WORDPRESS_USERNAME, WORDPRESS_PASSWORD, post_id)
    except:
        print "Exception inside utils.delete_post"
        print traceback.format_exc()
        exceptions.handle(self.request,
                          _('Unable to delete post.'))
        return False


@register.filter
def parse_time(xmlrpcdt, default=None):
    try:
        struct = time.strptime(str(xmlrpcdt), "%Y%m%dT%H:%M:%S")
        dt = datetime.fromtimestamp(mktime(struct))
        return dt.strftime("%B %d, %Y at %H:%M")
    except Exception:
        print "Exception inside utils.parse_time"
        print traceback.format_exc()
        return default or ''
