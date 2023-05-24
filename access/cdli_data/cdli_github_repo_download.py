import git
import yaml
config = yaml.safe_load(open("config.yml"))


def clone_cdli_repo():
    # repo = git.Repo(config['cdli_github_local'])
    # repo.remotes.origin.pull()
    # current = repo.head.commit
    # repo.remotes.origin.pull()
    # if current != repo.head.commit:
    #     print("It changed")
    # TODO: get this working
    pass

clone_cdli_repo()