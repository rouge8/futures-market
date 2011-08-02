from django.conf.urls.defaults import *
from django.conf import settings
import re

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    # loads urls from market.urls
    (r'', include('market.urls')),
)

# Prefix all the above patterns with URL_PREFIX
# Note: All urls must begin with ^, and URL_PATTERN must begin with /
if settings.URL_PREFIX:
    prefixed_urlpattern = []
    for pat in urlpatterns:
        pat.regex = re.compile(r"^%s/%s" % (settings.URL_PREFIX[1:], pat.regex.pattern[1:]))
        prefixed_urlpattern.append(pat)
    urlpatterns = prefixed_urlpattern
