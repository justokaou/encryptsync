# 🔐 SECURITY.md

## 🧠 Context

EncryptSync uses GPG key pairs to securely encrypt and decrypt files for synchronization purposes.

If your machines use full disk encryption and the GPG key pair is stored locally, it is usually acceptable **not** to require a passphrase every time — especially when using it for automated sync with tools like Syncthing or Nextcloud. In this case, local security is enforced by full disk encryption, and the GPG key is considered protected.

However, on a machine without disk encryption, using GPG without a passphrase is **not recommended**. For better security, it is advised to set a passphrase on your private key.

The problem: by default, GPG will ask for the passphrase **every time** a file is decrypted — making usage impractical for automation.

---

## ✅ Suggested Solution

To reduce user friction while keeping a passphrase enabled, GPG allows you to cache the passphrase temporarily.

### ✏ Modify `~/.gnupg/gpg-agent.conf`

```bash
default-cache-ttl 3600
max-cache-ttl 7200
```

- `default-cache-ttl` sets the default time (in seconds) that a cached passphrase will be remembered (e.g. 1 hour)  
- `max-cache-ttl` sets the maximum time before forgetting the cached passphrase, even if used repeatedly (e.g. 2 hours)

After editing this file, reload the agent:

```bash
gpg-connect-agent reloadagent /bye
```

---

## ⚠️ Warning

This solution offers a **convenient compromise** but is **not as secure** as entering the passphrase on every use. You should:

- Always use disk encryption on devices storing private keys  
- Avoid storing private keys unprotected (even with a cache) on shared or exposed systems  
- Consider using hardware tokens (Yubikey, smartcards) for higher assurance

---

## 📌 Summary

| Setup                         | Recommendation                             |  
|------------------------------|--------------------------------------------|  
| Disk encryption + local key  | ✅ OK to cache passphrase for automation   |  
| No disk encryption           | ⚠️ Use passphrase, consider hardware token |
