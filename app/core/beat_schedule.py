from celery.schedules import crontab

from app.core.celery import celery_app

celery_app.conf.beat_schedule = {
    'fetch_accounts_hourly': {
        'task': 'app.core.tasks.fetch_tasks.sync_accounts',
        'schedule': crontab(hour='8,12,17', minute=55),
        'options': {
            'expires': 3600,
        }
    },
    'send_accounts_hourly': {
        'task': 'app.core.tasks.send_tasks.send_all_companies',
        'schedule': crontab(hour='9,13,18', minute=0),
        'options': {
            'expires': 3600,
        }
    },
    'fetch_transactions_hourly': {
        'task': 'app.core.tasks.fetch_tasks.sync_transactions',
        'schedule': crontab(minute=55),
        'options': {
            'expires': 3600,
        }
    },
    'send_transactions_hourly': {
        'task': 'app.core.tasks.send_tasks.send_all_company_transactions',
        'schedule': crontab(minute=0),
        'options': {
            'expires': 3600,
        }
    },
    'delete_old_audit_logs': {
        'task': 'app.core.tasks.delete_logs.delete_old_logs',
        'schedule': crontab(hour=2, minute=0),
        'kwargs': {'days': 30, 'batch_size': 1000}
    },
    'send_daily_reports': {
        'task': 'app.core.tasks.send_tasks.send_daily_reports',
        'schedule': crontab(hour=18, minute=0),
        'options': {
            'expires': 3600,
        }
    }
}
