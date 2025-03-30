from django.contrib import admin
from .models import Livre, Genre, Panier, ArticlePanier, Commande, Paiement

class LivreAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'prix', 'genre_id', 'created_at')  # Correction ici
    search_fields = ('titre', 'auteur')
    list_filter = ('genre_id',)

class GenreAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)

class PanierAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'date_creation')

class ArticlePanierAdmin(admin.ModelAdmin):
    list_display = ('panier', 'livre', 'quantite')

class CommandeAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'prix_total', 'statut', 'created_at')
    list_filter = ('statut',)

class PaiementAdmin(admin.ModelAdmin):
    list_display = ('commande', 'moyen_paiement', 'transaction_id', 'montant', 'created_at')
    list_filter = ('moyen_paiement',)

admin.site.register(Livre, LivreAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Panier, PanierAdmin)
admin.site.register(ArticlePanier, ArticlePanierAdmin)
admin.site.register(Commande, CommandeAdmin)
admin.site.register(Paiement, PaiementAdmin)