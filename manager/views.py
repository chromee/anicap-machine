from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.


class TopView(TemplateView):
    template_name = "top.html"

    def get(self, request, *args, **kwargs):
        context = super(TopView, self).get_context_data(**kwargs)
        return render(self.request, self.template_name, context)

