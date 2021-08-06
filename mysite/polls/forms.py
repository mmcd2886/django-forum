from django import forms
from bootstrap_datepicker_plus import DatePickerInput, TimePickerInput

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'start_date', 'end_date', 'start_time', 'end_time']
        widgets = {
            'start_date':DatePickerInput().start_of('event days'),
            'end_date':DatePickerInput().end_of('event days'),
            'start_time':TimePickerInput().start_of('party time'),
            'end_time':TimePickerInput().end_of('party time'),
        }