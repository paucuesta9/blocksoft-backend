from io import BytesIO

from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from dotenv import load_dotenv
from api.permission import TokenAuth
import os
import requests
import zipfile
import json
import base64

load_dotenv()

@api_view(['POST'])
@permission_classes((TokenAuth,))
def githubAccessToken(request):
    """
    POST:
    {
        "code": "..."
    }
    """
    code = request.data.get('code')
    if code is None:
        return Response({"error": "No code provided."}, status=400)
    url = "https://github.com/login/oauth/access_token"
    headers = {
        "Accept": "application/json"
    }
    data = {
        "client_id": os.getenv("GITHUB_CLIENT_ID"),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
        "code": code
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code != 200:
        return Response({"error": "Invalid code."}, status=400)
    access_token = response.json().get('access_token')
    user = request.user
    user.githubToken = access_token
    user.save()
    return Response({"success": "Access token successfully linked to user."}, status=200)

@api_view(['GET'])
@permission_classes((TokenAuth,))
def githubUserRepos(request):
    """
    GET:
    {
        "access_token": "..."
    }
    """
    github_access_token = request.user.githubToken
    if github_access_token is None:
        return Response({"error": "No access token linked to user."}, status=404)

    headers = {
        "Authorization": "token " + github_access_token
    }

    github_url_user = "https://api.github.com/user"
    response = requests.get(github_url_user, headers=headers)

    github_url_repos_user = "https://api.github.com/search/repositories?q=user:" + response.json().get('login')
    response = requests.get(github_url_repos_user, headers=headers)

    if response.status_code != 200:
        return Response({"error": "Invalid access token."}, status=400)
    return Response(response.json(), status=200)

@api_view(['GET'])
@permission_classes((TokenAuth,))
def githubRepoFiles(request, repoName):
    github_access_token = request.user.githubToken
    if github_access_token is None:
        return Response({"error": "No access token linked to user."}, status=404)

    headers = {
        "Authorization": "token " + github_access_token
    }

    github_url_user = "https://api.github.com/user"
    response = requests.get(github_url_user, headers=headers)

    if response.status_code != 200:
        return Response({"error": "Invalid access token."}, status=400)

    user_login = response.json().get('login')
    github_url_repo_files = "https://api.github.com/repos/" + user_login + "/" + repoName + "/zipball"
    response = requests.get(github_url_repo_files, headers=headers)



    if response.status_code != 200:
        return Response({"error": "Invalid access token."}, status=400)
    else:
        with open(f'{user_login}_{repoName}.zip', 'wb') as fh:
            fh.write(response.content)
        file = open(f'{user_login}_{repoName}.zip', 'rb')
        response = HttpResponse(file, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=' + f'{user_login}_{repoName}.zip'
        return response

@api_view(['POST'])
@permission_classes((TokenAuth,))
def createRepo(request):
    """
    POST:
    {
        "repoName": "...",
        "description": "...",
        "private": true/false
        "code": zip file
    }
    """

    github_access_token = request.user.githubToken
    if github_access_token is None:
        return Response({"error": "No access token linked to user."}, status=404)



    code = request.FILES.get('code')
    if code is None:
        return Response({"error": "No code provided."}, status=400)

    headers = {
        "Authorization": "token " + github_access_token
    }

    data = json.dumps({
        "name": request.data.get('repoName'),
        "description": request.data.get('description').strip(),
        # "private": request.data.get('private') == 'true' or request.data.get('private') == True
        "private": True
    })

    print(data)

    # POST https://api.github.com/user/repos
    github_url_user = "https://api.github.com/user/repos"
    response = requests.post(github_url_user, headers=headers, data=data)
    print('POST https://api.github.com/user/repos')
    print(response.json())
    if response.status_code != 201:
        return Response({"error": response.json().get('errors')[0].get('message')}, status=400)

    repo_name = response.json().get('full_name')

    with open('temp.zip', 'wb') as fh:
        fh.write(code.read())
    with zipfile.ZipFile('temp.zip', 'r') as zipObj:
        zipObj.extractall(response.json().get('full_name'))
    os.remove('temp.zip')

    os.chdir(response.json().get('full_name'))
    os.system('git init')
    os.system('git add .')
    os.system('git commit -m "initial commit"')
    os.system('git remote add origin https://' + github_access_token + '@github.com/' + repo_name + '.git"')
    os.system('git push origin master')
    os.chdir('../..')
    return Response({"success": "Repo created successfully.", "url": "https://github.com/" + repo_name}, status=201)

#     github_url_repo_files = "https://api.github.com/repos/" + repo_name
#
# #     create first commit
#     data = json.dumps({
#         "message": "Initial commit",
#         "committer": {
#             "name": "Github API",
#             "email": request.user.email or "pcuesta@stp.es"
#         },
#         "content": base64.b64encode(bytes(request.data.get('repoName'), 'utf-8')).decode('utf-8')
#     })
#
#     response = requests.put(github_url_repo_files + "/contents/readme.md", headers=headers, data=data)
#     print(response.json())
#     if response.status_code != 201:
#         return Response({"error": "Invalid access token."}, status=400)
#
#     # POST https://api.github.com/repos/{user}/{repo}/git/blobs
#
#     github_url_repo_blobs = "https://api.github.com/repos/" + repo_name + "/git/blobs"
#
#     filesArray = []
#     for root, dirs, files in os.walk(repo_name):
#         for file in files:
#             content = bytes(open(os.path.join(root, file), 'rb').read())
#             encoded = base64.b64encode(content).decode('utf-8')
#             data = {
#                 "content": encoded,
#                 "encoding": "base64"
#             }
#             response_blob = requests.post(github_url_repo_blobs, headers=headers, data=json.dumps(data))
#             if response_blob.status_code != 201:
#                 return Response({"error": "Invalid access token."}, status=400)
#             filesArray.append({
#                 "path": os.path.join(root, file).replace('\\', '/').replace(repo_name, ''),
#                 "mode": "100644",
#                 "type": "blob",
#                 "sha": response_blob.json().get('sha')
#                 # "url": response_blob.json().get('url'),
#             })
#     # GET https://api.github.com/repos/{user}/{repo}/git/trees/{branch}
#     github_url_repo_trees = "https://api.github.com/repos/" + repo_name + "/git/trees/main"
#     response_tree = requests.get(github_url_repo_trees, headers=headers)
#     print('GET https://api.github.com/repos/{user}/{repo}/git/trees/{branch}')
#     print(response_tree.json())
#     if response_tree.status_code != 200:
#         return Response({"error": "Invalid access token."}, status=400)
#     tree_sha = response_tree.json().get('sha')
#     print(tree_sha)
#
#     # POST https://api.github.com/repos/{user}/{repo}/git/trees
#     github_url_repo_trees_new = "https://api.github.com/repos/" + repo_name + "/git/trees"
#     data = {
#         "tree": filesArray,
#         "base_tree": tree_sha
#     }
#     print(data)
#     response_tree = requests.post(github_url_repo_trees_new, headers=headers, data=json.dumps(data))
#     print('POST https://api.github.com/repos/{user}/{repo}/git/trees')
#     print(response_tree.json())
#     # POST https://api.github.com/repos/{user}/{repo}/git/commits
#     github_url_repo_commits = "https://api.github.com/repos/" + repo_name + "/git/commits"
#     data = {
#         "message": "Initial commit",
#         "tree": response_tree.json().get('sha'),
#         "parents": [tree_sha]
#     }
#     response_commit = requests.post(github_url_repo_commits, headers=headers, data=json.dumps(data))
#     print('POST https://api.github.com/repos/{user}/{repo}/git/commits')
#     print(response_commit.json())
#     if response_commit.status_code != 201:
#         return Response({"error": "Invalid access token."}, status=400)
#
#     # GET https://api.github.com/repos/BRO3886/git-db-example/git/refs/heads/{branch}
#     github_url_repo_refs = "https://api.github.com/repos/" + repo_name + "/git/refs/heads/main"
#
#     response_head = requests.get(github_url_repo_refs, headers=headers)
#     print('GET https://api.github.com/repos/{user}/{repo}/git/refs/heads/{branch}')
#     print(response_head.json())
#
#     if response_head.status_code != 200:
#         return Response({"error": "Invalid access token."}, status=400)
#
#     # PATCH https://api.github.com/repos/{user}/{repo}/git/refs/heads/{branch}
#     data = {
#         "sha": response_commit.json().get('sha')
#     }
#     github_url_repo_refs_new = "https://api.github.com/repos/" + repo_name + "/git/refs/heads/main"
#     response_head = requests.patch(github_url_repo_refs_new, headers=headers, data=json.dumps(data))
#     print('PATCH https://api.github.com/repos/{user}/{repo}/git/refs/heads/{branch}')
#     print(response_head.json())
#     if response_head.status_code != 200:
#         return Response({"error": "Invalid access token."}, status=400)
#     return Response({"success": "Successfully pushed to github.", "url": "https://github.com/" + repo_name}, status=200)