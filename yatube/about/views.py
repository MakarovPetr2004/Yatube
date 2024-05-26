from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'


class AboutWebsiteMapView(TemplateView):
    template_name = 'about/map.html'


class AboutContactsView(TemplateView):
    template_name = 'about/contacts.html'
