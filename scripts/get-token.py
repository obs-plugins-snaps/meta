# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "pygithub>=2.9.1",
# ]
# ///

import os

from github import Auth, GithubIntegration

APP_ID = os.environ["GITHUB_APP_ID"]
INSTALLATION_ID = int(os.environ["GITHUB_APP_INSTALLATION_ID"])
PRIVATE_KEY = os.environ["GITHUB_APP_PEM_FILE"]


def main() -> None:
    auth = Auth.AppAuth(APP_ID, PRIVATE_KEY)

    # GithubIntegration binds the HTTP requester needed to call GitHub's token API
    integration = GithubIntegration(auth=auth)

    # Fetch the token object and extract the string
    access_token = integration.get_access_token(INSTALLATION_ID)
    print(access_token.token)


if __name__ == "__main__":
    main()
