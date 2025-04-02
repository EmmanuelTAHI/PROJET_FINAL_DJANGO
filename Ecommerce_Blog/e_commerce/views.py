from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth.models import User

from .form import AuthForm
from .models import Livre, Genre, Panier, ArticlePanier, Commande, Paiement
from django.contrib import messages


def index(request):
    livres = (Livre.objects.all())  # Récupère tous les livres
    return render(request, 'e_commerce/index.html', {'livres': livres})

def about(request):
    return render(request, 'e_commerce/about.html')

def shop(request):
    return render(request, 'e_commerce/shop.html')

def blog(request):
    return render(request, 'e_commerce/blog.html')

def contact(request):
    return render(request, 'e_commerce/contact.html')


def single_post(request):
    return render(request, 'e_commerce/single-post.html')

# Vue pour afficher les détails d'un livre
def single_product(request, livre_id):
    livre = get_object_or_404(Livre, id=livre_id)
    return render(request, 'e_commerce/single-product.html', {'livre': livre})

# ==============================
# 🔐 Authentification (Connexion, Inscription, Déconnexion)
# ==============================

def connexion(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')  # Vérifie si "Se souvenir de moi" est coché

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            if remember_me:
                # Prolonge la session à 30 jours (comme Amazon)
                request.session.set_expiry(30 * 24 * 60 * 60)  # 30 jours en secondes
            else:
                # La session expire à la fermeture du navigateur
                request.session.set_expiry(0)

            return redirect('index')

        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")

    return render(request, 'registration/login.html')

def deconnexion(request):
    logout(request)
    return redirect('index')


def inscription(request):
    if request.method == 'POST':
        form = AuthForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Désactiver le compte jusqu'à activation
            user.is_superuser = True  # On donne les droits admin
            user.is_staff = True
            user.save()

            # Génération du lien d'activation
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            domain = get_current_site(request).domain
            activation_link = f"http://{domain}/activate/{uid}/{token}/"

            # Contenu du mail
            subject = "Activation de votre compte"
            message = f"""
            Bonjour {user.username},

            Merci de vous être inscrit. Veuillez cliquer sur le lien ci-dessous pour activer votre compte :

            {activation_link}

            Si vous n'avez pas demandé cette inscription, ignorez cet email.

            Merci,
            L'équipe de support.
            """

            # Envoi du mail
            email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [user.email])
            email.send(fail_silently=False)
            return render(request, 'registration/login.html')  # Redirige l'utilisateur

    else:
        form = AuthForm()

    return render(request, 'registration/register.html', {'form': form})


def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        messages.error(request, "Le lien d'activation est invalide ou a expiré.")

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)  # Connexion automatique après activation
        return redirect("index")

    return render(request, "registration/activation_failed.html")  # Page d’erreur


# Vue pour afficher les livres d'une catégorie spécifique
def livres_par_categorie(request, categorie_id):
    categorie = get_object_or_404(Genre, id=categorie_id)
    livres = Livre.objects.filter(categorie=categorie)
    return render(request, 'livres/categorie.html', {'categorie': categorie, 'livres': livres})


# Vue pour ajouter un livre au panier
@login_required
def ajouter_au_panier(request, livre_id):
    livre = get_object_or_404(Livre, id=livre_id)
    panier, created = Panier.objects.get_or_create(utilisateur=request.user)
    article, created = ArticlePanier.objects.get_or_create(panier=panier, livre=livre)
    if not created:
        article.quantite += 1
        article.save()
    return redirect('voir_panier')


# Vue pour afficher le panier
@login_required
def voir_panier(request):
    panier, created = Panier.objects.get_or_create(utilisateur=request.user)
    articles = panier.articlepanier_set.all()
    return render(request, 'panier/voir.html', {'articles': articles})


# Vue pour supprimer un article du panier
@login_required
def supprimer_du_panier(request, article_id):
    article = get_object_or_404(ArticlePanier, id=article_id)
    article.delete()
    return redirect('voir_panier')


# Vue pour passer une commande
@login_required
def passer_commande(request):
    panier = get_object_or_404(Panier, utilisateur=request.user)
    articles = panier.articlepanier_set.all()
    if not articles:
        return redirect('voir_panier')

    prix_total = sum(article.livre.prix * article.quantite for article in articles)
    commande = Commande.objects.create(utilisateur=request.user, prix_total=prix_total)

    for article in articles:
        article.delete()

    return redirect('choisir_paiement', commande_id=commande.id)


# Vue pour choisir un mode de paiement
@login_required
def choisir_paiement(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id, utilisateur=request.user)
    if request.method == "POST":
        moyen_paiement = request.POST.get("moyen_paiement")
        transaction_id = f"TXN{commande.id}{request.user.id}"  # Simulation d'un ID de transaction
        paiement = Paiement.objects.create(commande=commande, moyen_paiement=moyen_paiement,transaction_id=transaction_id, montant=commande.prix_total)
        commande.statut = "Payé"
        commande.save()
        return redirect('confirmation_commande', commande_id=commande.id)

    return render(request, 'paiement/choisir.html', {'commande': commande})


# Vue pour afficher la confirmation de commande
@login_required
def confirmation_commande(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id, utilisateur=request.user)
    return render(request, 'commande/confirmation.html', {'commande': commande})