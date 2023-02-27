from logs import log, dbg
from pprint import pprint
from json import loads


class paginationHandler(object):
    def __init__(self, session=None, request=None, params=None, per_page=10):
        self.session = session
        self.request = request
        self.params = params
        self.per_page = per_page


    def get(self):
        done = False
        count = 1
        content = []

        while not done:
            self.params['per_page'] = self.per_page
            self.params['page'] = count
            dbg("paginationHandler.get", self.params)
            if (r := self.session.get(self.request, params=self.params)).status_code == 200:
                data = loads(r.text)
                total = data["count"]
                response_content = data["items"]
                dbg("paginationHandler.get", "per_page: {}".format(self.per_page))
                dbg("paginationHandler.get", "len(content): {}".format(len(content)))
                for item in response_content:
                    if not item in content:
                        content.append(item)

                if len(response_content) == self.per_page:
                    self.per_page += self.per_page # x2
                    count = count // 2

                if len(content) == total:
                    done = True

                count = count + 1
            else:
                log("paginationHandler.get", "Something wrong happened while requesting paginated data")
                dbg("paginationHandler.get", "CODE: {}".format(r.status_code))
                dbg("paginationHandler.get", r.text)
                return False
        return content


        
