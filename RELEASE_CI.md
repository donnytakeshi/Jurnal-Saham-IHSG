# CI Release & Keystore Instructions

This document explains how to provide a keystore to the GitHub Actions CI and how the workflow performs signed release builds.

1) Generate a local keystore (optional, for local testing)

```bash
# create a python3.11 venv and install buildozer locally (optional)
python3.11 -m venv .venv311
source .venv311/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install buildozer cython==0.29.33

# generate a keystore for testing (uses scripts/generate_keystore.sh)
./scripts/generate_keystore.sh keystore/release.keystore releasekey android android
```

2) Create a base64-encoded keystore file for GitHub Secrets

On macOS:
```bash
openssl base64 -A -in keystore/release.keystore > keystore.b64
```

On Linux:
```bash
base64 --wrap=0 keystore/release.keystore > keystore.b64
```

3) Add the following GitHub repository secrets (Repository Settings → Secrets → Actions):

- `APK_KEYSTORE_BASE64` — contents of `keystore.b64` (the base64-encoded keystore)
- `APK_KEYSTORE_PASSWORD` — keystore password (example: `android`)
- `APK_KEY_PASSWORD` — key password (example: `android`)

You can set them via the GitHub CLI:

```bash
gh secret set APK_KEYSTORE_BASE64 --body "$(cat keystore.b64)"
gh secret set APK_KEYSTORE_PASSWORD --body "android"
gh secret set APK_KEY_PASSWORD --body "android"
```

4) CI behavior (what we changed)

- The CI will decode `APK_KEYSTORE_BASE64` and place the keystore at `keystore/release.keystore`.
- If both password secrets are present, the CI injects `android.release_keystore_passwd` and
  `android.release_keyalias_passwd` into `buildozer.spec` before running the build so the
  release can be signed automatically.
- The workflow will run a `release` build when pushing to the `main` branch and a `debug`
  build for other branches and pull requests.

5) Notes & security

- Never commit your keystore or passwords to the repository. The workflow expects the keystore
  to come from `APK_KEYSTORE_BASE64` and the passwords from `APK_KEYSTORE_PASSWORD`/`APK_KEY_PASSWORD`.
- For additional security, consider using GitHub Organization secrets or HashiCorp Vault.

6) Manually trigger a signed release locally

If you want to run a local release build and sign locally (requires configured Android SDK/NDK):

```bash
source .venv311/bin/activate
./scripts/generate_keystore.sh keystore/release.keystore releasekey android android
buildozer -v android release
```

Tag behavior & bumping version
------------------------------

The CI now reads the `version` field from `buildozer.spec` and creates a GitHub Release
tagged `v<version>` (for example, `v0.1` or `v1.2.3`). To control release tags, update the
`version` line in `buildozer.spec` before pushing to `main`.

Simple ways to bump the version locally:

- Edit `buildozer.spec` manually and change the `version =` value to the desired semantic version.

Example (change to 0.2.0):

```bash
sed -i '' 's/^version = .*/version = 0.2.0/' buildozer.spec   # macOS (BSD sed)
sed -i 's/^version = .*/version = 0.2.0/' buildozer.spec     # Linux (GNU sed)
```

- Commit and push the change to `main` to trigger the `release-build` job which will build,
  sign (if keystore secrets are provided), and create the GitHub Release with tag `v0.2.0`.

Notes
- Ensure your `version` follows semantic versioning (MAJOR.MINOR.PATCH) to keep releases predictable.
- If you prefer automated bumping (patch/minor on each release), I can add a CI step to increment
  the `version` automatically — let me know if you'd like that.
