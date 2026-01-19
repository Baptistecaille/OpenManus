# ResearchMaster Pro Agent

Agent de recherche multi-étapes avec capacité de raisonnement complexe pour OpenManus.

## 📋 Description

ResearchMaster Pro est un agent spécialisé qui suit une méthodologie structurée en 5 phases pour mener des recherches approfondies avec des citations obligatoires.

**Philosophie :** "Pas de citations, pas de crédibilité" - chaque affirmation DOIT être sourcée.

## 🚀 Utilisation

### Via script dédié

```bash
python run_research_master.py --prompt "Est-ce que React Server Components sont prêts pour la production en 2024 ?"
```

### Via run_flow

1. Activez l'agent dans votre fichier `config/config.toml` :

```toml
[runflow]
use_research_master_agent = true
```

2. Lancez le flow :

```bash
python run_flow.py
```

## 📚 Méthodologie (5 Phases)

### Phase 0 : Planification Interne
- Analyse de la requête utilisateur
- Définition de la stratégie de recherche
- Plan des mots-clés et sections du rapport

### Phase 1 : Recherche Web
- 2-3 recherches avec angles différents
- Profondeur adaptative (basic/advanced)
- Sélection rigoureuse des sources

### Phase 2 : Analyse & Synthèse
- Tri du corpus par score et date
- Détection de redondances
- Validation croisée des informations

### Phase 3 : Génération du Rapport
Structure markdown obligatoire :
1. Résumé Exécutif (3-5 phrases)
2. Points Clés Découverts
3. Analyse des Sources
4. Lacunes & Limites Identifiées
5. Recommandations
6. Sources Consultées (Bibliographie)
7. Méta-données de la Recherche

### Phase 4 : Auto-vérification (Quality Gate)
- Vérification des citations
- Détection des hallucinations
- Cohérence des dates
- Présentation objective

## ⚙️ Configuration

```python
# Dans app/agent/research_master.py

max_observe: int = 15000    # Limite de tokens par observation
max_steps: int = 30         # Nombre maximum d'étapes
```

## 📊 Critères de Sélection des Sources

✅ **Privilégier :**
- Sources officielles
- Documentation
- Publications académiques (.edu)
- GitHub officiel
- Articles techniques récents (2023+)

⚠️ **Vérifier :**
- Blogs (date, auteur, références)

❌ **Éviter :**
- Sources obsolètes
- Forums non modérés
- Contenu sans auteur

## 🎯 Exemple de Rapport

```markdown
# 📊 Rapport de Recherche : React Server Components - Production Readiness 2024

## 1. Résumé Exécutif
React Server Components sont officiellement prêts pour la production depuis Next.js 14...

## 2. Points Clés Découverts
### 2.1 Statut de Production Officialisé
**Détail** : Next.js 14 stabilise RSC depuis Oct 2023...
- **Source(s)** : [Next.js 14 Blog](https://nextjs.org/blog/next-14) (2023-10-26)
- **Fiabilité** : Haute (source officielle)
```

## 🔧 Dépendances

- `web_search` : Pour rechercher sur le web
- `terminate` : Pour terminer quand le rapport est complet

## 📝 Auteurs

Basé sur les spécifications de ResearchMaster Pro v1.0
