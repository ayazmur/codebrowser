import os
import subprocess
from django.core.management import execute_from_command_line


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_browser.settings')
    
    execute_from_command_line(['manage.py', 'migrate'])
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    
    import uvicorn
    from web_browser.asgi import application
    
    uvicorn.run(application, host='0.0.0.0', port=8000)


if __name__ == '__main__':
    main()
