import os, sys
site_user_root_dir = '/home/t/timyr4rm/timyr4rm.beget.tech/public_html'
sys.path.insert(0, site_user_root_dir + '/diplom')
sys.path.insert(1, site_user_root_dir + '/venv/lib/python3.11/site-packages/')

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diplom.settings')

application = get_wsgi_application()