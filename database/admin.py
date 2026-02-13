
from django.contrib import admin

from .models import gene, clade, feature, feature_type, project_settings, transcript


admin.site.register(clade)
admin.site.register(gene)
admin.site.register(feature)
admin.site.register(feature_type)
admin.site.register(transcript)
admin.site.register(project_settings)