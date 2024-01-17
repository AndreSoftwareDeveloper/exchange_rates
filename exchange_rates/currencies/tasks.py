from django_q.tasks import Schedule
from datetime import datetime

from .currency_data_manager import CurrencyDataManager

update_error = None


def update_exchange_rates_task():
    global update_error
    update_error = CurrencyDataManager.update_exchange_rates()


now = datetime.now()
next_run_time = now.replace(hour=12, minute=0, second=0, microsecond=0)

scheduled_time = Schedule(
    func='tasks.update_exchange_rates_task',
    name='update_exchange_rates_task',
    schedule_type=Schedule.DAILY,
    repeats=-1,
    next_run=next_run_time,
)

scheduled_time.save()
