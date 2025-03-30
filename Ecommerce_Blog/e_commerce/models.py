from django.db import models
from django.contrib.auth.models import User

# Modèle pour les catégories de livres
class Genre(models.Model):

    class Meta:
        verbose_name = "Genre"
        verbose_name_plural = "Genres"

    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom

# Modèle pour les livres
class Livre(models.Model):
    class Meta:
        verbose_name = "Livre"
        verbose_name_plural = "Livres"

    titre = models.CharField(max_length=255)
    couverture = models.ImageField(upload_to="livres/")
    auteur = models.CharField(max_length=255)
    resume = models.TextField()
    genre_id = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)
    prix = models.IntegerField()
    stock = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre

# Modèle pour le panier d'achat
class Panier(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

# Modèle pour les articles dans le panier
class ArticlePanier(models.Model):
    panier = models.ForeignKey(Panier, on_delete=models.CASCADE)
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantite} x {self.livre.titre}"

# Modèle pour les commandes
class Commande(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    prix_total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(
        max_length=20,
        choices=[('En attente', 'En attente'), ('Payé', 'Payé'), ('Expédié', 'Expédié'), ('Annulé', 'Annulé')],
        default='En attente'
    )

    def __str__(self):
        return f"Commande {self.id} - {self.statut}"

# Modèle pour les paiements
class Paiement(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    moyen_paiement = models.CharField(
        max_length=20,
        choices=[('Orange Money', 'Orange Money'),
                 ('Moov Money', 'Moov Money'),
                 ('MTN Money', 'MTN Money'),
                 ('Wave', 'Wave'),
                 ('Carte Bancaire', 'Carte Bancaire')],
        default='Carte Bancaire'
    )
    transaction_id = models.CharField(max_length=255, unique=True)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.moyen_paiement} - {self.montant}FCFA"
