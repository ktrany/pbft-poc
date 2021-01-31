#! /usr/bin/env python3
import git
import index
import os


class WebHookHandler:

    def __init__(self):
        pass

    def getDockerFile(self, branch):
        # checkout branch and pull
        # repoCloneUrl = "https://github.com/ktrany/pbftTestProject.git"
        repoCloneUrl = index.REPO_CLONE_URL
        localRepo = index.LOCAL_REPO
        
        repo = None
        
        # only clone if local repo does not exist yet
        if os.path.isdir(localRepo):
            repo = git.Repo(localRepo)
        else:
            repo = git.Repo.clone_from(repoCloneUrl, localRepo)

        repo.git.checkout(branch)
        # repo.remotes.origin.pull()

        # read file
        dockerfile = ''
        fileLocation = f'{localRepo}/Dockerfile'

        with open(fileLocation) as f:
            dockerfile = f.read()

        return dockerfile