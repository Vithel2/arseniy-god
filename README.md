# Арсений God — сборка APK (лёгкий вариант)

Вся игра упакована в один файл www.zip (~7 МБ). Сборка сама его распакует.

1. github.com -> New repository -> Create
2. Add file -> Upload files -> перетащи 6 объектов: www.zip, config.xml, package.json, README.md, папки res и .github -> Commit
3. Actions -> Build APK -> Run workflow -> ждать ~6 минут
4. Artifacts -> ArseniyGod-APK -> внутри ArseniyGod.apk

Интернет игре не нужен: всё внутри APK.


## Firestore rules for multiplayer

The current client-side Firestore rules are in `firestore.rules`. Copy them into Firebase Console → Firestore Database → Rules. The client still computes scores locally; rules restrict score writes to monotonic increases by each participant, but this is not anti-cheat. Competitive rewards should be granted by a trusted server/Cloud Function after validating a match.
