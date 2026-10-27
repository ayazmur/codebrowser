import os
import sys
import django


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_browser.settings')
    django.setup()
    
    from django.core.management import execute_from_command_line
    
    # Run migrations
    execute_from_command_line(['manage.py', 'migrate', '--noinput'])
    
    # Run collectstatic
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    
    # Start the server
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])


if __name__ == '__main__':
    main()
