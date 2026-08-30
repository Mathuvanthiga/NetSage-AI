# NetSage AI – Complete Working Demo

## Run in VS Code

1. Open this `NetSage_AI` folder.
2. Open Terminal.
3. Install packages:

```powershell
py -m pip install -r requirements.txt
```

4. Start the application:

```powershell
py -m streamlit run app.py
```

If `py` is unavailable, use `python` instead.

The browser will open the NetSage AI interface.

## Features
- 30 Packet Tracer troubleshooting cases
- Diagnose screen
- Symptom/topology/show-output input
- Root cause, confidence, evidence, OSI layer and concept
- Next command and suggested fix
- Mandatory Accept/Edit/Reject human review
- Saved review history
- Issue/severity dashboard
- Responsible AI correction examples
- Existing deterministic Python checker

## Rule checker

```powershell
py checker\checker.py
```

This offline student-project version does not automatically change Cisco configurations. It demonstrates the AI-assisted + human-review workflow. An external LLM/API can be connected later using `prompts/diagnose_prompt.md`.
