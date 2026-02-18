# Play Store Preflight Checklist

Last updated: 2026-02-18
Project: Book of Mormon Mobile (`org.donov.mobile_app`)

Status key:
- `[x]` Done
- `[ ]` Pending
- `[-]` Unknown / needs confirmation

## 1) Play Console Account

- [ ] Play Console account created and one-time fee paid.
- [ ] Account verification (ID/device/etc.) complete.
- [-] Account type confirmed (`Personal` vs `Organization`).
- [-] If `Personal` and created after 2023-11-13: closed-testing gate plan ready.

Notes:
- This repo/session does not include Play Console account state; confirm directly in Play Console.

## 2) Release Artifact (AAB)

- [x] Release packaging script added: `release_playstore_aab.ps1`.
- [ ] Build release Android App Bundle (`.aab`) for upload.
- [ ] Confirm `.aab` exists under `dist/`.
- [ ] Version bump strategy confirmed for each upload.

Current status:
- We have repeatedly built and installed debug APKs successfully.
- We have not yet confirmed a packaged release AAB in this session.

Suggested command:
```powershell
cd C:\dev\Book_of_Mormon_local
briefcase package android
```

Automated script:
```powershell
cd C:\dev\Book_of_Mormon_local
powershell -ExecutionPolicy Bypass -File .\release_playstore_aab.ps1
```

## 3) Android / Policy Technical Requirements

- [x] App is Android-targeted and actively buildable.
- [x] `INTERNET` permission explicitly declared in `pyproject.toml` for remote chart image fetch.
- [ ] Confirm target SDK/API level meets current Play requirement at release time.

Current status:
- Build pipeline is stable from `C:\dev\Book_of_Mormon_local`.
- Target SDK should be verified from final release manifest/Gradle output before upload.

## 4) App Signing

- [ ] Play App Signing enrollment completed for this app in Play Console.
- [ ] Upload key/keystore generated, stored, and backed up.

Notes:
- Not verifiable from this repo alone.

## 5) Store Listing Assets

- [ ] App name finalized for listing.
- [x] Listing draft template added: `PLAY_STORE_LISTING_TEMPLATE.md`.
- [ ] 512x512 icon prepared.
- [ ] Feature graphic prepared.
- [ ] Phone screenshots prepared.
- [x] Privacy policy draft added: `PRIVACY_POLICY.md`.
- [ ] Privacy Policy URL prepared and reachable (host this file publicly).
- [ ] Support contact email set.

## 6) App Content Declarations

- [ ] Data Safety form completed.
- [ ] Content rating questionnaire completed.
- [ ] Target audience and content declaration completed.
- [ ] Ads declaration set correctly.
- [ ] App access/reviewer instructions added if login/protected content exists.

## 7) Testing Tracks and Release Flow

- [ ] Internal testing track upload done.
- [ ] Closed/Open testing done as needed.
- [ ] Production rollout plan prepared.
- [-] If required by account type, closed test gate criteria satisfied.

## 8) Project-Specific Stability Gate (Current App)

- [x] Emulator-safe launch flow documented in `ANDROID_RUNBOOK.md`.
- [x] Live patch flow exists: `patch_android_live.ps1`.
- [x] Build from `C:\dev\Book_of_Mormon_local` to avoid OneDrive file locks.
- [x] Chart rendering now uses image output with offline fallback.
- [x] Chart rendering moved off UI thread to avoid ANR/hang.
- [x] App launches successfully after live patch.
- [x] Runtime app ID aligned with package: `org.donov.mobile_app`.

## 9) Final Go/No-Go Before Upload

- [ ] AAB generated from latest commit.
- [ ] Smoke test on clean emulator/device build.
- [ ] Version + changelog finalized.
- [ ] All Play Console warnings resolved.
- [ ] Ready for first track submission.

---

## Quick Next Steps (Recommended Order)

1. Generate AAB from `C:\dev\Book_of_Mormon_local`.
2. Confirm target SDK/API and version metadata in release output.
3. Prepare listing assets + privacy policy URL.
4. Complete Data Safety/content forms.
5. Upload to Internal testing first.
