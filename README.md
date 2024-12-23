# Prkpass - FileVault2

## Description:
Automates the process of retrieving
recovery keys with serial numbers from Jamf Pro via its API,
storing them securely in a password store (e.g., pass).
It also handles pagination for API responses, ensuring 
that large sets of data are processed correctly and efficiently.
Additionally, it organizes the stored keys by serial number
in a date-stamped directory structure.

## Notes:
- The jamf api filvevault endpoint does not include serial 
  numbers in the response payload, only jamf ids.

## Setup and usage of pass key store:

1. Create or import an existing a gpg key.

https://docs.github.com/en/authentication/managing-commit-signature-verification/generating-a-new-gpg-key

```
gpg --import private.key
```
2. Verify the key is in your gpg store:
```
gpg --list-keys
```
3. You may need to set the trust level of the key also:

https://yanhan.github.io/posts/2014-03-04-gpg-how-to-trust-imported-key/

## Setup Shell:

1. Install unix password manager https://www.passwordstore.org/.
2. `git clone` this repo to `$HOME/repos`.
3. Add to `.zshrc` or `.bashrc`. This will define the password store used by `prkpass`:

 ```
prkpass() {
    PASSWORD_STORE_DIR=$HOME/repos/prkstore pass $@
}
```
4. If zsh completion is required also add this to `.zshrc`:
```
compdef _pass prkpass
zstyle ':completion::complete:prkpass::' prefix "$HOME/repos/prkstore"
```
5. Reload shell:
```
source ~/.zshrc
```

## Usage:
Passing the capture date and device serial to the function will output the required key in the console. You will get prompted for the gpg key passphrase.

```
$ prkpass 2023-12-19/C1FFPF6P7N
EEGP-A3HA-AOY7-UGGN-QJVO-TWH7
```