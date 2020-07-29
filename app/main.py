import os
import time
import logging
import hmac
import aiohttp
import jwt
from gidgethub.aiohttp import GitHubAPI
from flask import (abort, Flask, session, render_template,
                   session, redirect, url_for, request,
                   flash, jsonify)
from mlapp import GitHubApp

app = Flask(__name__)

path_to_private_key=os.getenv('PEM_FILE_PATH', "issue-insights.2020-07-27.private-key.pem")
app_id=os.getenv('GH_APP_ID', 74516)
webhook_secret=os.getenv('WEBHOOK_SECRET', "TestGithubInsights20Van")

def get_jwt(app_id):

    # TODO: read is as an environment variable
    pem_file = open(path_to_private_key, "rt").read()

    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + (10 * 60),
        "iss": app_id,
    }
    encoded = jwt.encode(payload, pem_file, algorithm="RS256")
    bearer_token = encoded.decode("utf-8")

    return bearer_token

@app.route("/event_handler", methods=["POST"])
def bot():
    "Handle payload"

    logging.debug("Request Data:\n%s", request.data)
    if not request.json:
        logging.error("Request is not a json request. Please fix.")
        # TODO(jlewi): What is the proper code invalid request?
        abort(400)

    logging.debug("Handling request with action: %s",
                  request.json.get('action', 'None'))
    # authenticate webhook to make sure it is from GitHub
    # verify_webhook(request)

    # Check if payload corresponds to an issue being opened
    if 'issue' not in request.json:
        logging.warning("Event is not for an issue with action opened.")
        return 'ok'

    # get metadata
    installation_id = request.json['installation']['id']
    issue_num = request.json['issue']['number']
    private = request.json['repository']['private']
    username, repo = request.json['repository']['full_name'].split('/')
    title = request.json['issue']['title']
    body = request.json['issue']['body']
    labels = request.json['issue']['labels']

    # Labels_list contains the list of labels
    labels_list = []
    for label in labels:
        labels_list.append(label['name'])

    # don't do anything if repo is private.
    if private:
        logging.info(f"Recieved a private issue which is being skipped")
        return 'ok'
    logging.info(f"Recieved {username}/{repo}#{issue_num}")
    
    # Check if payload corresponds to an issue being opened
    if 'action' not in request.json or request.json['action'] != 'opened':
        logging.warning("Event is not for an issue with action opened.")
        return 'ok'
    issue = get_issue_handle(installation_id, username, repo, issue_num)

    pull_requests = get_pull_requests(installation_id, username, repo)


    # make predictions with the model
    # with app.graph.as_default():
    #    predictions = app.issue_labeler.get_probabilities(body=body, title=title)
    #log to console
    # LOG.warning(f'issue opened by {username} in {repo} #{issue_num}: {title} \nbody:\n {body}\n')
    # LOG.warning(f'predictions: {str(predictions)}')

    message = get_display_message(pull_requests, installation_id, username, repo)

    # get the most confident prediction
    issue.add_labels("test-label")
    # message = str(labels_list)
    # Make a comment using the GitHub api
    comment = issue.create_comment(message)

    return 'ok'
    
def get_display_message(pull_requests, installation_id, username, repo):
    msg = ""
    msg += get_pr_display_message(pull_requests)
    msg += "\n\n\n"
    msg += get_important_files_display_msg(pull_requests, installation_id, username, repo)
    msg += "\n\n\n"
    msg += get_pr_authors_display_message(pull_requests)

    return msg

def get_pr_display_message(pull_requests):
    formatted_prs = [get_formatted_pr(pr) for pr in pull_requests]
    return "These are some of the Pull Requests which addressed similar issues: \n" + ''.join(formatted_prs)

def get_formatted_pr(pr):
    return "* ["+ pr.title +"]("+pr.html_url+") \n"

def get_important_files_display_msg(pull_requests, installation_id, username, repository):
    msg = "These are some files that you might want to take a look at to address this issue: \n"
    sorted_files = get_sorted_files(pull_requests)
    
    ghapp = get_app()
    repo_client = ghapp.get_installation(installation_id).repository(username, repository)

    file_count = 0
    max_file_count = 5

    for f in sorted_files:
        try:
            c = repo_client.file_contents(f[0])
            msg += get_formatted_file(f[0], username, repository)
            file_count += 1
            if file_count >= max_file_count:
                 break
        except Exception as e:
            logging.warning(e)
            logging.warning("File not found:" + f[0] + " does not exist on master.")
    return msg

def get_formatted_file(file, repo_owner, repo):
    return "* ["+ file +"](https://github.com/"+ repo_owner +"/"+ repo +"/tree/master/"+ file +") \n"

def get_sorted_files(pull_requests):
    file_dict = {}
    for pr in pull_requests:
        for f in pr.files():
            file_dict[f.filename] = file_dict.get(f.filename, 0) + (f.additions_count * (f.additions_count / max(f.deletions_count, 1)))

    return sorted(file_dict.items(), key=lambda x: x[1], reverse=True)

def get_pr_authors_display_message(pull_requests):
    authors = {pr.user.login for pr in pull_requests}
    formatted_authors = [get_formatted_author(a) for a in authors]
    return "These are the authors who contributed to fixing similar issues: \n" + ''.join(formatted_authors)

def get_formatted_author(author):
    return "* ["+ author +"](https://github.com/"+ author +") \n"

def get_app():
    "grab a fresh instance of the app handle."

    if not app_id:
        raise ValueError("APP_ID environment variable must be set.")
    key_file_path = path_to_private_key
    if not key_file_path:
        raise ValueError("GITHUB_APP_PEM_KEY environment variable must be set.")
    ghapp = GitHubApp(pem_path=key_file_path, app_id=app_id)
    return ghapp

def get_issue_handle(installation_id, username, repository, number):
    "get an issue object."
    ghapp = get_app()
    install = ghapp.get_installation(installation_id)
    return install.issue(username, repository, number)

def get_pull_requests(installation_id, username, repository):
    "get an issue object."
    ghapp = get_app()
    install = ghapp.get_installation(installation_id)
    pull_requests = install.repository(username, repository).pull_requests()
    return pull_requests

async def get_installation(gh, jwt, username):
    async for installation in gh.getiter(
        "/app/installations",
        jwt=jwt,
        accept="application/vnd.github.machine-man-preview+json",
    ):
        if installation["account"]["login"] == username:
            return installation

    raise ValueError(f"Can't find installation by that user: {username}")

async def get_installation_access_token(gh, jwt, installation_id):
    # doc: https: // developer.github.com/v3/apps/#create-a-new-installation-token

    access_token_url = (
        f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    )
    response = await gh.post(
        access_token_url,
        data=b"",
        jwt=jwt,
        accept="application/vnd.github.machine-man-preview+json",
    )
    # example response
    # {
    #   "token": "v1.1f699f1069f60xxx",
    #   "expires_at": "2016-07-11T22:14:10Z"
    # }

    return response

def verify_webhook(request):
    "Make sure request is from GitHub.com"
    
    # if we are testing, don't bother checking the payload

    if os.getenv('DEVELOPMENT_FLAG'): return True
    SIGNATURE_HEADER = 'X-Hub-Signature'
    # Inspired by https://github.com/bradshjg/flask-githubapp/blob/master/flask_githubapp/core.py#L191-L198
    if SIGNATURE_HEADER not in request.headers:
        logging.error("Request is missing header %s", SIGNATURE_HEADER)

    signature = request.headers[SIGNATURE_HEADER].split('=')[1]

    logging.warning(webhook_secret)
    mac = hmac.new(str.encode(webhook_secret), msg=request.data, digestmod='sha1')

    if not hmac.compare_digest(mac.hexdigest(), signature):
        LOG.warning('GitHub hook signature verification failed.')
        abort(400)

if __name__ == "__main__":
   
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='127.0.0.1', port=3000)