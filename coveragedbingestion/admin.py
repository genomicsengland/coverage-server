from django.contrib import admin
from django import forms

from .models import SampleIngestion, GeneCollection, PropertyDefinition, CollectionProperty


class GeneCollectionForm(forms.ModelForm):
    class Meta:
        fields = ['property_type', 'value']
        model = CollectionProperty

    def clean_value(self):
        if self.cleaned_data.get('property_type').property_type == 'float':
            try:
                float(self.cleaned_data.get('value'))
            except ValueError:
                raise forms.ValidationError('Please provide a valid float value')

        elif self.cleaned_data.get('property_type').property_type == 'integer':
            try:
                int(self.cleaned_data.get('value'))
            except ValueError:
                raise forms.ValidationError('Please provide a valid integer value')
        return self.cleaned_data.get('value')


class SampleIngestionAdmin(admin.ModelAdmin):
    list_display = ['name', 'input_file', 'gene_collection', 'task', 'seconds']


class CollectionPropertyInline(admin.TabularInline):
    form = GeneCollectionForm
    model = CollectionProperty


class PropertyDefinitionAdmin(admin.ModelAdmin):
    list_display = ['property_name', 'property_type']


class GeneCollectionAdmin(admin.ModelAdmin):
    list_display = ['name']
    inlines = [CollectionPropertyInline]


admin.site.register(SampleIngestion, SampleIngestionAdmin)
admin.site.register(GeneCollection, GeneCollectionAdmin)
admin.site.register(PropertyDefinition, PropertyDefinitionAdmin)
