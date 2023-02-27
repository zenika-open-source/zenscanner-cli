#!/bin/env -S python3 -OO -B
#-*- coding:utf-8 -*-

from argparse import ArgumentParser
from runscan import client
from configHandler import configHandler
from localAuth import localAuth
from sys import platform
from repoManager import repoManager
from tokenManager import tokenManager
from credManager import credManager
from logs import log


def createParser():
    parser = ArgumentParser()

    subparser = parser.add_subparsers(dest='subparser_name')


    ''' python main.py auth ... '''
    auth = subparser.add_parser("auth", help='setup or verify authentication')
    auth.add_argument("-v", "--verify", help="verify the token from the config file", action="store_true")
    auth.add_argument("-r", "--reauth", help="regenerate token for this cli", action="store_true")


    ''' python main.py runscan ... '''
    upload = subparser.add_parser("runscan", help="upload and run scan for project")
    upload.add_argument("-a", "--authkey", help="provide authkey for CI authentication (otherwise uses config file)")
    upload.add_argument("-H", "--host", help="API host to upload to (required if you use authkey)")
    upload.add_argument("-d", "--directory", help="directory of the repository", required=True)
    upload.add_argument("-r", "--repo", help="uuid of the repository", required=True)


    ''' python main.py repos ... '''
    repos = subparser.add_parser("repos", help="setup, list or delete repos")
    repos_sub = repos.add_subparsers(dest="repos_action")
    repo_add = repos_sub.add_parser("add", help="registers a new repo")
    repo_del = repos_sub.add_parser("del", help="delete a registered repo")
    repo_get = repos_sub.add_parser("get", help="get informations for given repository")
    repo_list = repos_sub.add_parser("list", help="list registered repos (default)")
    repo_scan = repos_sub.add_parser("scan", help="scan registered repos")
    repo_list_scan_result = repos_sub.add_parser("list-results", help="list all scan results for given repo")
    repo_get_scan_result = repos_sub.add_parser("get-result", help="get result from given scan")
    repo_update = repos_sub.add_parser("update", help="update a registered repo")
    

    ''' python main.py repos list ... '''
    repo_list.add_argument("-s", "--search", help="Keyword to grep inside repo name")


    ''' python main.py repos add ... '''
    repo_add.add_argument("-c", "--credential", help="cred uuid to use")
    repo_add.add_argument("-u", "--url", help="url of the repository", required=True)
    repo_add.add_argument("-n", "--name", help="name of the repository", required=True)
    repo_add.add_argument("-sc", "--source_control", help="type of source control (git, svn)")
    

    ''' python main.py repos del ... '''
    repo_del.add_argument("-r", "--repoUuid", help="uuid of the repository to delete", required=True)


    ''' python main.py repos get ... '''
    repo_get.add_argument("-r", "--repoUuid", help="uuid of the repository to get details of", required=False)
    repo_get.add_argument("-k", "--keyword", help="keyword to search inside repo url/name", required=False)


    ''' python main.py repos scan ... '''
    repo_scan.add_argument("-r", "--repoUuid", help="uuid of the repository to scan", required=True)
    repo_scan.add_argument("-b", "--branch", help="specific branch to scan, if not default")


    ''' python main.py repos list-results ... '''
    repo_list_scan_result.add_argument("-r", "--repoUuid", help="uuid of the repository to the scan result from", required=True)


    ''' python main.py repos get-result ... '''
    repo_get_scan_result.add_argument("-r", "--repoUuid", help="uuid of the repository to the scan result from", required=True)
    repo_get_scan_result.add_argument("-t", "--task", help="uuid of the task from the scan", required=True)


    ''' python main.py repos update ... '''
    repo_update.add_argument("-r", "--repoUuid", help="uuid of the repository to update", required=True)
    repo_update.add_argument("-n", "--name", help="new name for the repository")
    repo_update.add_argument("-u", "--url", help="new url for the repository")
    repo_update.add_argument("-c", "--credential", help="new cred for the repository")


    ''' python main.py access_token ... '''
    access_token = subparser.add_parser("access_token", help='setup, list or delete access tokens')
    access_token_sub = access_token.add_subparsers(dest="access_token_action")
    access_token_add = access_token_sub.add_parser("add", help="generate a new access token")
    access_token_del = access_token_sub.add_parser("del", help="delete a registered access token")
    access_token_list = access_token_sub.add_parser("list", help="list registered access_token (default)")
    access_token_check = access_token_sub.add_parser("check", help="check access_token validity")

    ''' python main.py access_token add ... '''
    access_token_add.add_argument("-l", "--label", help="label of the future token")

    ''' python main.py access_token del ... '''
    access_token_del.add_argument("-t", "--token", help="token to delete", required=True)

    ''' python main.py access_token list ... '''
    ''' pas d'option '''

    ''' python main.py access_token check ... '''
    access_token_check.add_argument("-t", "--token", help="token to check", required=True)


    ''' python main.py credential ... '''
    credential = subparser.add_parser("credentials", help='setup, list or delete credentials')
    credential_sub = credential.add_subparsers(dest="credential_action")
    credential_add = credential_sub.add_parser("add", help="generate a new access token")
    credential_del = credential_sub.add_parser("del", help="delete a registered access token")
    credential_list = credential_sub.add_parser("list", help="list registered credential (default)")
    credential_update = credential_sub.add_parser("update", help="update registered credential")

    ''' python main.py credential add ... '''
    credential_add.add_argument("-l", "--label", help="label of the future cred", required=True)
    credential_add.add_argument("-v", "--value", help="value of the future cred", required=True)
    credential_add.add_argument("-t", "--type", help="type of the future cred", required=True)

    ''' python main.py credential del ... '''
    credential_del.add_argument("-u", "--uuid", help="uuid of the cred to delete", required=True)

    ''' python main.py credential update ... '''
    credential_update.add_argument("-u", "--uuid", help="uuid of the cred to update", required=True)
    credential_update.add_argument("-l", "--label", help="new label of the cred")
    credential_update.add_argument("-v", "--value", help="new value of the cred")
    credential_update.add_argument("-t", "--type", help="new type of cred")

    ''' python main.py credential list ... '''
    ''' pas d'option '''

    return parser


def main():
    ch = configHandler()
    config = ch.getConfig()

    if platform != 'linux':
        log('init', 'CLI only compatible with Linux for now')

    parser = createParser()
    args = parser.parse_args()

    if args.subparser_name == 'runscan':
        if not config and not args.host:
            parser.error("runscan requires --host or a valid config (see auth)")

        host = args.host if args.host else config.url
        cli = client(args.authkey, host)
        return cli.runscan(args.directory, args.repo)

    if args.subparser_name == 'auth':

        if args.verify and args.reauth:
            parser.error("cannot have --verify and --reauth")

        lAuth = localAuth(
            config        = config,
            configHandler = ch,
            firstLogin    = (args.reauth is True or config is None),
            verify        = args.verify,
            )
    
    if args.subparser_name == 'repos':

        if args.repos_action in [None, "list"]:
            rm = repoManager(
                config = config,    
                keyword = args.search if args.repos_action else None
            )
            
            rm.listRepo()

        if args.repos_action == "add":
            rm = repoManager(
                config   = config,
                credUuid = args.credential,
                name     = args.name,
                url      = args.url,
                source_control = args.source_control
            )
            
            rm.newRepo()

        if args.repos_action == "del":
            rm = repoManager(
                config = config,
                repoUuid = args.repoUuid,
            )

            rm.delRepo()
            
        
        if args.repos_action == "get":
            if not args.repoUuid and not args.keyword:
                parser.error("must have either -r/--repoUuid or -k/--keyword")

            rm = repoManager(
                config = config,
                repoUuid = args.repoUuid,
                keyword = args.keyword,
            )

            rm.getRepo()


        if args.repos_action == "scan":
            rm = repoManager(
                config = config,
                repoUuid = args.repoUuid,
                branch = args.branch,
            )

            rm.scanRepo()


        if args.repos_action == "list-results":
            rm = repoManager(
                config = config,
                repoUuid = args.repoUuid,
            )

            rm.listResults()


        if args.repos_action == "get-result":
            rm = repoManager(
                config = config,
                repoUuid = args.repoUuid,
                task_id = args.task,
            )

            rm.getResult()


        if args.repos_action == "update":

            rm = repoManager(
                config   = config,
                repoUuid = args.repoUuid,
                name     = args.name,
                url      = args.url,
                credUuid = args.credential
            )

            rm.updateRepo()
    
    if args.subparser_name == 'access_token':
        if args.access_token_action in [None, "list"]:
            tm = tokenManager(
                config    = config,
            )

            tm.listToken()

        if args.access_token_action == "add":
            tm = tokenManager(
                config = config,
                tokenLabel = args.label
            )

            tm.newToken()

        if args.access_token_action == "del":
            tm = tokenManager(
                config = config,
                tokenUuid = args.token
            )

            tm.delToken()

        if args.access_token_action == "check":
            tm = tokenManager(
                config = config,
                tokenUuid = args.token
            )

            tm.checkToken()

    if args.subparser_name == 'credentials':
        if args.credential_action in [None, "list"]:
            cm = credManager(
                config = config,
            )

            cm.listCred()

        if args.credential_action == "add":
            cm = credManager(
                config = config,
                type = args.type,
                label = args.label,
                value = args.value
            )

            cm.newCred()

        if args.credential_action == "del":
            cm = credManager(
                config = config,
                uuid = args.uuid
            )

            cm.delCred()


        if args.credential_action == "update":
            cm = credManager(
                config = config,
                uuid = args.uuid,
                type = args.type,
                label = args.label,
                value = args.value
            )

            cm.updateCred()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("init", "Interrupt: Bye.")
        exit(0)
