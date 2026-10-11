# Installation

The practice app ships as two stand-in installers attached to each GitHub Release.

## Linux (`EdgeApp-practice-<version>.run`)

```bash
sha256sum -c EdgeApp-practice-0.1.0.run.sha256
chmod +x EdgeApp-practice-0.1.0.run
./EdgeApp-practice-0.1.0.run /opt/edge-app-practice
cd /opt/edge-app-practice
python3.11 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Windows (`EdgeApp-practice-<version>.msi`)

The `.msi` is a stand-in: it is a zip archive with an `.msi` name. Check it, then extract it:

```powershell
Get-FileHash -Algorithm SHA256 EdgeApp-practice-0.1.0.msi   # compare with the .sha256 file
Copy-Item EdgeApp-practice-0.1.0.msi app.zip
Expand-Archive app.zip -DestinationPath C:\edge-app-practice
```

Then create a Python 3.11 virtual environment, install `requirements.txt` and run `uvicorn` as on Linux.

## Configuration

Copy `.env.example` to `.env` next to the app. Every `PRACTICE_*` setting is optional.
