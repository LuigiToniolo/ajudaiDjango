from django.apps import AppConfig


class AjudaiDjangoAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ajudai_django_app'

    def ready(self):
        # Enable WAL mode for SQLite to improve concurrency
        from django.db.backends.signals import connection_created
        
        def set_sqlite_pragma(sender, connection, **kwargs):
            if connection.vendor == 'sqlite':
                cursor = connection.cursor()
                # WAL mode allows concurrent reads during writes
                cursor.execute('PRAGMA journal_mode=WAL;')
                # NORMAL sync is faster and still safe with WAL
                cursor.execute('PRAGMA synchronous=NORMAL;')
                # Set busy timeout at connection level too
                cursor.execute('PRAGMA busy_timeout=30000;')
        
        connection_created.connect(set_sqlite_pragma)