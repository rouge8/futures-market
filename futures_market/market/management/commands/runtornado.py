from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import os
import sys

class Command(BaseCommand):
    option_list = BaseCommand.option_list + ()
    help = "Starts a Tornado Web."
    args = '[optional port number, or ipaddr:port]'

    def handle(self, addrport='', *args, **options):
        import django
        from django.core.handlers.wsgi import WSGIHandler
        from tornado import httpserver, wsgi, ioloop, web

	sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
	sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)

        if args:
            raise CommandError('Usage is runserver %s' % self.args)
        if not addrport:
            addr = ''
            port = '8000'
        else:
            try:
                addr, port = addrport.split(':')
            except ValueError:
                addr, port = '', addrport
        if not addr:
            addr = '127.0.0.1'

        if not port.isdigit():
            raise CommandError("%r is not a valid port number." % port)

        quit_command = (sys.platform == 'win32') and 'CTRL-BREAK' or 'CONTROL-C'

        def inner_run():
            from django.conf import settings
            from tornado_static import StaticFileHandler, FallbackHandler

            print "Validating models..."
            self.validate(display_num_errors=True)
            print "\nDjango version %s, using settings %r" % (django.get_version(), settings.SETTINGS_MODULE)
            print "Server is running at http://%s:%s/" % (addr, port)
            print "Quit the server with %s." % quit_command

            wsgi_app = wsgi.WSGIContainer(WSGIHandler())
            if settings.STATIC_ROOT == '':
		    application = web.Application([
			(r"/static/(.*)", StaticFileHandler, {"path": "/home/andy/projects/dln-futures-market/futures_market/market/static"}),
			(r".*", FallbackHandler, dict(fallback=wsgi_app))
		    ])
            else:
		    application = web.Application([
			(r".*", FallbackHandler, dict(fallback=wsgi_app))
		    ])


            http_server = httpserver.HTTPServer(application)
            http_server.listen(int(port), address=addr)
            ioloop.IOLoop.instance().start()

        inner_run()
