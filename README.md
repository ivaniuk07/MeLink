# MeLink

MeLink is a Django application for creating a personal page with social media, portfolio and project links. The interface is in Ukrainian.

## Features

- Three-step editor: profile details, links and appearance.
- Unique profile address, photo upload (PNG/JPEG, up to 5 MB) and live preview.
- Add or delete up to 20 links; hide individual links without deleting them.
- HTTP/HTTPS URL validation and atomic link updates.
- Purple, dark and light themes.
- Public profile page and a button to copy its URL.
- Edit the existing profile from the same browser session.
- Responsive layout and accessible form labels.

## Stack

Python 3.10+, Django 5.2.17, Django REST framework 3.18.3, SQLite, Pillow, Django Templates, CSS and vanilla JavaScript. Python 3.12 is recommended for local setup.

## Run locally

```sh
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/ and choose **Створити**. Keep the terminal running. Stop the server with Ctrl+C.

On Windows, activate the environment with `venv\Scripts\activate`.

A local secret key is generated once in `.local-secret`, which is ignored by Git. SQLite data and uploaded files are also excluded from Git.

## Demo walkthrough

1. Open the homepage and follow either of its two create buttons.
2. Enter a name, short bio, description and unique address; optionally upload a photo.
3. Add a GitHub URL and another link. Toggle one link off to demonstrate visibility.
4. Choose a theme and open the public page.
5. Copy its URL. Open it in a private browser window to see the visitor view.
6. In the original browser, select **Редагувати** to update the existing profile.

The copied localhost URL works only on the computer running the app. Sharing with other people requires hosting.

## Data model

`Profile` stores name, bio, description, unique address, photo path and theme.

`Link` belongs to a profile through a foreign key with cascade deletion. It stores title, URL, sort order and visibility. Links are ordered by `sort_order`, then ID.

## Routes

| URL | Purpose |
| --- | --- |
| `/` | Homepage |
| `/create/` | Create or update the session's profile |
| `/create_links/` | Edit the profile's links |
| `/appearance/` | Choose a theme |
| `/profile/<address>/` | Public profile |
| `/api/profiles/<address>/` | Read-only JSON representation of a public profile and its visible links |
| `POST /api/profiles/` | Create a profile and optionally its links |
| `/admin/` | Django administration |

Example API requests: `GET /api/profiles/oleksii/` returns a profile and only its visible links; `POST /api/profiles/` creates a profile and optional links from JSON.

## Validation and tests

```sh
python manage.py check
python manage.py test
```

The tests cover the complete creation flow, session ownership, duplicate addresses, invalid links, atomic updates, hidden links, ordering, link limits, themes, photo validation, HTML escaping, static assets, the profile API response and the two homepage create links.

## Session ownership and scope

This is an interview/demo project with session-based editing, not a complete account system. A browser session owns one profile. Visitors cannot edit a profile just by knowing its URL. Clearing cookies or losing the session removes access to the editor; cross-device login and account recovery are not implemented. A profile becomes publicly accessible after the first step is saved, even before the remaining steps are completed.

The next development steps would be account authentication, profile ownership linked to users, draft/publish states, upload cleanup and deployment configuration. The local development server is not intended for production.

## Configuration

Optional environment variables:

- `DJANGO_SECRET_KEY`: explicit secret key; required when debug is disabled.
- `DJANGO_DEBUG`: defaults to `True` for local development.
- `DJANGO_ALLOWED_HOSTS`: comma-separated hosts; defaults to localhost and loopback addresses.
- `DJANGO_DB_PATH`: SQLite file path; defaults to `db.sqlite3`.
- `DJANGO_MEDIA_ROOT`: upload directory; defaults to `media/`.

Uploaded images are served by Django only in debug mode. A production deployment must configure static/media serving, HTTPS and secure cookies separately.
