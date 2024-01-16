from django.contrib import messages
from django.http import HttpResponse
from django.template import loader

from .currency_data_manager import CurrencyDataManager
from .forms import CurrencyForm
from .tasks import update_error


def currencies(request):
    template = loader.get_template('currencies.html')
    messages.error(request, update_error)
    statistics = {}

    if request.method == 'POST':
        form = CurrencyForm(request.POST)
        if form.is_valid():
            selected_currency_pairs = form.cleaned_data['currency_pairs']
            saving_message = CurrencyDataManager.save_selected_columns(selected_currency_pairs)

            if isinstance(saving_message, str):
                messages.error(request, saving_message)
            else:
                for key, value in saving_message.items():
                    statistics[key] = f"{value}"

            messages.success(request, f'Data for the following exchange rates: {selected_currency_pairs} '
                                      f'has been saved!')
    else:
        form = CurrencyForm()

    context = {'form': form, 'statistics': statistics}
    return HttpResponse(template.render(context, request))
