# Wochen-Mahlzeiten-Planer Add-on

Ein einfacher Home Assistant Add-on für einen Wochen-Mahlzeiten-Planer mit Rezeptverwaltung.

## Installation

1. Füge dieses Repository zu Home Assistant als benutzerdefiniertes Add-on-Repository hinzu.
2. Installiere das Add-on „Wochen-Mahlzeiten-Planer“.
3. Starte das Add-on und öffne die Benutzeroberfläche über die Seitenleiste.

## Dateien

- `planner.py` – Streamlit-Anwendung für die Mahlzeitenplanung
- `run.py` – Startet die Streamlit-App mit den richtigen Parametern
- `requirements.txt` – Python-Abhängigkeiten
- `config.json` – Add-on-Konfiguration für Home Assistant
- `Dockerfile` – Container-Build für das Add-on

## Persistente Daten

Alle Mahlzeiten und Rezepte werden in `/data/meals.json` gespeichert, sodass sie nach einem Neustart erhalten bleiben.

## Hinweise

- Die App läuft über das Home Assistant Ingress-Panel (Port 5000).
- Rezepte und Mahlzeiten können jederzeit hinzugefügt, bearbeitet oder entfernt werden.