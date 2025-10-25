# 🔒 Security Guidelines

## Environment Variables

This project uses environment variables to store sensitive information like API keys and private keys. **NEVER commit these to Git.**

### Setup Instructions

1. **Copy the example file**
   ```bash
   cp .env.example .env
   ```

2. **Fill in your credentials**
   ```bash
   # Edit .env with your actual values
   nano .env  # or use any text editor
   ```

3. **Verify .env is ignored**
   ```bash
   # This should show .env in .gitignore
   cat .gitignore | grep .env
   ```

### Required Environment Variables

| Variable | Description | Where to Get |
|----------|-------------|--------------|
| `STELLAR_SECRET` | Stellar account secret key | From Stellar testnet account creation |
| `STELLAR_PUBLIC` | Stellar account public key | From Stellar testnet account creation |
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 | [OpenAI Platform](https://platform.openai.com/api-keys) |

### Security Best Practices

✅ **DO:**
- Use `.env` file for local development
- Use environment variables in production
- Add `.env` to `.gitignore` (already done)
- Use `.env.example` as a template (no real values)
- Rotate keys regularly

❌ **DON'T:**
- Hard-code API keys in source code
- Commit `.env` file to Git
- Share your `.env` file with others
- Use production keys in development

### What's Protected

The following files are automatically ignored by Git (see `.gitignore`):
```
.env
*.env
.env.local
.env.*.local
```

### Checking for Exposed Secrets

Before making the repository public, verify no secrets are committed:

```bash
# Check if .env is in git history
git log --all --full-history -- .env

# Search for potential API keys in code
grep -r "sk-" . --exclude-dir=.git

# Search for OPENAI_API_KEY values
grep -r "OPENAI_API_KEY=" . --exclude-dir=.git --exclude="*.md" --exclude=".env.example"
```

### For Competition Submission

When making the repository public:

1. ✅ Ensure `.env` is NOT committed
2. ✅ Ensure `.env.example` IS committed (template only)
3. ✅ All API keys are loaded via `os.getenv()` or `os.environ.get()`
4. ✅ No hardcoded secrets in code
5. ✅ Documentation explains how to set up `.env`

### GitHub Secrets (For CI/CD)

If you set up GitHub Actions, use [GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets):

```yaml
# .github/workflows/test.yml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  STELLAR_SECRET: ${{ secrets.STELLAR_SECRET }}
```

### Emergency: If You Accidentally Commit Secrets

If you accidentally commit `.env` or expose an API key:

1. **Immediately rotate the key**
   - For OpenAI: Create new API key and revoke old one
   - For Stellar: Create new testnet account

2. **Remove from Git history** (if already pushed)
   ```bash
   # WARNING: This rewrites history
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all
   
   git push origin --force --all
   ```

3. **Verify removal**
   ```bash
   git log --all --full-history -- .env
   ```

## Contact

If you discover a security vulnerability, please email [your-email] instead of opening a public issue.

