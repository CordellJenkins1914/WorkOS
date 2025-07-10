import os
from flask import Flask, render_template, redirect, request, session, url_for
from workos import WorkOSClient
from dotenv import load_dotenv
load_dotenv()


WORKOS_API_KEY   = os.environ["WORKOS_API_KEY"]
WORKOS_CLIENT_ID = os.environ["WORKOS_CLIENT_ID"]
ORG_ID       = os.environ["TEST_ORG_ID"]
DIRECTORY_ID = os.environ["TEST_DIRECTORY_ID"]


workos = WorkOSClient(
    api_key=WORKOS_API_KEY,
    client_id=WORKOS_CLIENT_ID,
)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))

@app.route("/")
def index():
    
    return render_template("index.html", user=session.get("user"))

@app.route("/success")
def success():
    user = session.get("user")
    return render_template("login_successful.html", user=user)


@app.route("/auth")
def auth():

    organization_id = ORG_ID

    redirect_uri = "http://127.0.0.1:5000/callback"

    authorization_url = workos.sso.get_authorization_url(
        organization_id=organization_id, redirect_uri=redirect_uri
    )

    return redirect(authorization_url)

@app.route("/callback")
def callback():
    if "error" in request.args:
        return f"SSO Error: {request.args['error_description']}", 400

    code = request.args.get("code")
    if code is None:
        return redirect(url_for("index"))

    pat = workos.sso.get_profile_and_token(code)
    profile = pat.profile

    session["user"] = {
        "name":  f"{profile.first_name} {profile.last_name}",
        "email": profile.email,
        "org":   profile.organization_id,
    }

    return redirect(url_for("success"))

@app.route("/admin-portal")
def admin_portal():
    portal_link = workos.portal.generate_link(
        organization_id=ORG_ID,  # ← your Test Org ID
        intent="sso",
    )
    return redirect(portal_link.link)


@app.route("/directory")
def directory():
    if "user" not in session:
        return redirect(url_for("index"))

    EMAIL   = session["user"]["email"].lower()
    DIR_ID  = DIRECTORY_ID

    dir_users = workos.directory_sync.list_users(
        directory_id=DIR_ID
    ).data
    me = next(u for u in dir_users if u.email and u.email.lower() == EMAIL)


    if not me.role or me.role.slug != "admin":
        return render_template("error.html",
            message="Access denied: admins only"), 403

    groups = workos.directory_sync.list_groups(directory_id=DIR_ID).data
    group_list = []
    for g in groups:
        members = workos.directory_sync.list_users(
            directory_id=DIR_ID,
            group_id=g.id
        ).data
        group_list.append({"group": g, "members": members})

    return render_template("directory.html", group_list=group_list)




@app.route("/group_details")
def group_details():
    user_email = session["user"]["email"].lower()


    all_users = workos.directory_sync.list_users(
        directory_id=DIRECTORY_ID
    ).data
    directory_user = next(
        (u for u in all_users if u.email and u.email.lower() == user_email),
        None
    )
    if not directory_user:
        return "User not found in directory", 404

    user_groups = workos.directory_sync.list_groups(
        directory_id=DIRECTORY_ID,
        user_id=directory_user.id
    ).data

    group_list = []
    for grp in user_groups:
        members = workos.directory_sync.list_users(
            directory_id=DIRECTORY_ID,
            group_id=grp.id
        ).data
        group_list.append({
            "group":   grp,
            "members": members,
        })

    return render_template(
        "group_details.html",
        group_list=group_list,
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(port=5000, debug=True)
