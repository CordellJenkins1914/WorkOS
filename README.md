# WorkOS Flask Demo

This repository demonstrates a Flask application integrated with WorkOS’s core identity features:

* **Single Sign-On (SSO)** via WorkOS SSO
* **Admin Portal** deep-link for customer self-service configuration
* **Directory Sync**: listing groups and members, with admin-only access control

## Features

1. **SSO Authentication**

   * `/auth` & `/callback` routes implement OAuth 2.0 Authorization Code flow via WorkOS
   * User profile is retrieved and stored in session

2. **Admin Portal Integration**

   * `/admin-portal` route deep-links into WorkOS’s hosted Admin Portal (intent: `sso`)

3. **Directory Sync**

   * `/directory`: lists all groups and their members (admin-only)
   * `/group_details`: shows only the logged-in user’s groups and corresponding members

4. **Access Control**

   * Only users assigned the **admin** role (via Directory Sync roles) can access the full directory
   * Non-admins see a friendly error page

## Prerequisites

* Python 3.12+
* pip
* A [WorkOS account](https://dashboard.workos.com/) with a **Test Organization** and **Test Directory**
* Environment variables:

  * `WORKOS_API_KEY`
  * `WORKOS_CLIENT_ID`
  * `FLASK_SECRET_KEY`
  * `TEST_ORG_ID` (optional override)
  * `TEST_DIRECTORY_ID` (optional override)

## Installation

```bash
git clone <https://github.com/CordellJenkins1914/WorkOS.git>
cd <WorkOS>
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Create a `.env` file at the project root:

```ini
WORKOS_API_KEY=sk_test_...
WORKOS_CLIENT_ID=client_...
FLASK_SECRET_KEY=your-random-secret
# Optional overrides (defaults are in app.py):
# TEST_ORG_ID=org_...
# TEST_DIRECTORY_ID=directory_...
```

## Running the App

```bash
source venv/bin/activate
python app.py
```

Visit `http://127.0.0.1:5000`:

* Click **Log in with SSO** to authenticate
* After login, you’ll see links to:

  * **Manage SSO via Admin Portal**
  * **View Your Directory** (user’s own groups)
  * **View Groups & Members** (all groups & members, admin-only)

## Routes

| Endpoint         | Description                                         |
| ---------------- | --------------------------------------------------- |
| `/`              | Home / login link                                   |
| `/auth`          | Initiate SSO                                        |
| `/callback`      | SSO callback & session setup                        |
| `/success`       | Login success page                                  |
| `/admin-portal`  | Deep-link to WorkOS Admin Portal                    |
| `/directory`     | Admin-only: list all groups & members               |
| `/group_details` | Per-user: list only logged-in user’s groups/members |
| `/logout`        | Clear session & return to home                      |

## Project Structure

```
├── app.py                # Flask application
├── templates/            # Jinja2 templates
│   ├── index.html
│   ├── login_successful.html
│   ├── directory.html
│   ├── group_details.html
│   └── error.html
├── requirements.txt      # pip dependencies
└── .env                  # environment variables (not tracked)
