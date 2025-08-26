#!/bin/bash

echo "🔑 Generisanje novog SSH ključa za GitHub Actions..."

# Generisanje novog SSH ključa bez passphrase-a
ssh-keygen -t rsa -b 4096 -f ~/.ssh/github_actions -N "" -C "github-actions@todo.emikon.rs"

# Kopiranje javnog ključa u authorized_keys
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys

# Postavljanje pravilnih dozvola
chmod 600 ~/.ssh/github_actions
chmod 644 ~/.ssh/github_actions.pub
chmod 600 ~/.ssh/authorized_keys

echo "✅ SSH ključ generisan!"
echo ""
echo "🔑 Privatni ključ (kopirajte ovo u GitHub Secrets kao SSH_PRIVATE_KEY):"
echo "=========================================="
cat ~/.ssh/github_actions
echo "=========================================="
echo ""
echo "📋 Javni ključ:"
cat ~/.ssh/github_actions.pub
echo ""
echo "📝 Instrukcije:"
echo "1. Kopirajte privatni ključ (iznad) u GitHub Secrets"
echo "2. Naziv: SSH_PRIVATE_KEY"
echo "3. Vrednost: ceo sadržaj privatnog ključa"
