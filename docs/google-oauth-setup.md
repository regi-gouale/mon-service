# Configuration OAuth Google

Ce guide explique comment configurer l'authentification OAuth 2.0 avec Google pour l'application Church Team Management.

## Prérequis

- Un compte Google
- Accès à la [Google Cloud Console](https://console.cloud.google.com/)

## Étapes de configuration

### 1. Créer un projet Google Cloud

1. Accédez à la [Google Cloud Console](https://console.cloud.google.com/)
2. Cliquez sur le sélecteur de projet en haut de la page
3. Cliquez sur **Nouveau projet**
4. Nommez votre projet (ex: `church-team-management`)
5. Cliquez sur **Créer**

### 2. Activer l'API Google+ (ou People API)

1. Dans le menu de navigation, allez dans **APIs & Services** > **Bibliothèque**
2. Recherchez **Google+ API** ou **People API**
3. Cliquez sur l'API puis sur **Activer**

### 3. Configurer l'écran de consentement OAuth

1. Allez dans **APIs & Services** > **Écran de consentement OAuth**
2. Sélectionnez le type d'utilisateur :
   - **Interne** : Uniquement pour les utilisateurs de votre organisation Google Workspace
   - **Externe** : Pour tous les utilisateurs (nécessite vérification pour la production)
3. Cliquez sur **Créer**
4. Remplissez les informations requises :
   - **Nom de l'application** : Church Team Management
   - **E-mail d'assistance utilisateur** : votre email
   - **Logo de l'application** : (optionnel)
   - **Domaines autorisés** : votre domaine de production (ex: `churchteam.app`)
   - **Coordonnées du développeur** : votre email
5. Cliquez sur **Enregistrer et continuer**

#### Scopes requis

Ajoutez les scopes suivants :

| Scope     | Description                                   |
| --------- | --------------------------------------------- |
| `openid`  | Authentification OpenID Connect               |
| `email`   | Accès à l'adresse email                       |
| `profile` | Accès aux informations de profil (nom, photo) |

### 4. Créer les identifiants OAuth 2.0

1. Allez dans **APIs & Services** > **Identifiants**
2. Cliquez sur **Créer des identifiants** > **ID client OAuth**
3. Sélectionnez **Application Web**
4. Configurez :
   - **Nom** : Church Team Management Web Client
   - **Origines JavaScript autorisées** :
     - Développement : `http://localhost:3000`
     - Production : `https://votre-domaine.com`
   - **URI de redirection autorisés** :
     - Développement : `http://localhost:3000/api/auth/callback/google`
     - Production : `https://votre-domaine.com/api/auth/callback/google`
5. Cliquez sur **Créer**
6. **Copiez** le `Client ID` et le `Client Secret` affichés

### 5. Configurer les variables d'environnement

Ajoutez les valeurs obtenues dans votre fichier `.env` :

```bash
# OAuth2 (Google)
GOOGLE_CLIENT_ID=123456789-xxxxxxxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxxxxxxxx
GOOGLE_REDIRECT_URI=http://localhost:3000/api/auth/callback/google
```

## Configuration par environnement

### Développement

```bash
GOOGLE_REDIRECT_URI=http://localhost:3000/api/auth/callback/google
```

### Staging

```bash
GOOGLE_REDIRECT_URI=https://staging.votre-domaine.com/api/auth/callback/google
```

### Production

```bash
GOOGLE_REDIRECT_URI=https://votre-domaine.com/api/auth/callback/google
```

> ⚠️ **Important** : En production, assurez-vous que l'URI de redirection utilise HTTPS.

## Vérification de la configuration

Pour vérifier que la configuration OAuth est correcte, vous pouvez utiliser le endpoint de santé :

```bash
curl http://localhost:8000/api/v1/health
```

Le champ `google_oauth_configured` doit être `true` si les variables sont correctement configurées.

## Dépannage

### Erreur "redirect_uri_mismatch"

Cette erreur se produit lorsque l'URI de redirection dans votre application ne correspond pas exactement à celui configuré dans Google Console.

**Solution** :

1. Vérifiez que `GOOGLE_REDIRECT_URI` correspond exactement à l'URI configuré
2. Attention aux différences http/https
3. Attention aux slashs finaux

### Erreur "access_denied"

**Causes possibles** :

- L'utilisateur a refusé les permissions
- L'application n'est pas en mode "production" et l'utilisateur n'est pas un testeur

**Solution** :

1. Ajoutez l'utilisateur comme testeur dans l'écran de consentement OAuth
2. Ou soumettez l'application pour vérification Google

### Client ID ou Secret invalide

**Solution** :

1. Vérifiez qu'il n'y a pas d'espaces ou caractères invisibles dans les variables
2. Régénérez les credentials si nécessaire

## Sécurité

- **Ne committez jamais** les credentials dans le code source
- Utilisez des **secrets managers** en production (AWS Secrets Manager, HashiCorp Vault, etc.)
- **Rotation des secrets** : Régénérez périodiquement le Client Secret
- Configurez des **restrictions d'API** dans Google Console pour limiter l'usage

## Ressources

- [Documentation Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Guide de vérification OAuth](https://support.google.com/cloud/answer/9110914)
