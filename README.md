## ZenScanner Cli


### How to run ?


When using for the first time, just use `python main.py auth` and the first login routine will start


If you seek help on how to use the cli:

`python main.py -h`

`python main.py auth -h`

`python main.py runscan -h`

`python main.py credentials -h`

`python main.py repos -h`

`python main.py access_token -h`


### Install


Clone repository


```
git clone https://github.com/zenika-open-source/zenscanner-cli.git
cd zenscanner-cli
```

Install requirements


```
pip3 install -r requirements.txt
```


Do the first auth


```
python ./main.py auth
```

It will ask you for login/password and address of the API (Careful: the address MUST end with a '/')

Profit !



### How to use it to run scan on local directories?


Create a new credential (Skip this if you have already registered a repo in the API for the scan or if the repository is public)

```
python main.py credentials add -l CREDLABEL -t CREDTYPE -v CREDVALUE
```
Note the UUID given by the API (We'll call it CREDUUID)

(Some checks are made internaly so make sure CREDVALUE is of the right shape for CREDTYPE)

If you want to list credentials just do

```
python main.py credentials list
```

Create a new repo (Skip this if you already have registered a repo in the API for the scan)


```
python main.py repos add -c CREDUUID -u REPOURL -n REPONAME
```

REPOURL and REPONAME are arbitrary and only informational for now. You could for exemple do:

```
python main.py repos add -c CREDUUID -u local_testrepo -n testrepo
```
Note the UUID given by the API (We'll call it REPOUUID) and the AuthKey

If you want to list repositories just do

```
python main.py repos list
```

### Run the scan in a CI 

```
python main.py runscan -H "http://apiAddress:apiPort/" -a AuthKey -r REPOUID -d /path/to/local/directory
```

Note: The `-H` switch is only there for CI and is not mandatory for everyday usage. Also, this command could be used entirely inside a CI if you have setup a repo just like above.


### How to generate Access Tokens ?


Once authenticated, just use the following command:

```
python main.py access_token add
```

It will generate a random name (for exemple, zenscannercli_Pv5PA3hf) and make the call to generate a new token. You can specify a name if needed with the `-l` switch

To list already generated access tokens use `list` or don't use any argument:

```
python main.py access_token list
```


