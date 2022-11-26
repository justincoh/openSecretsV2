import requests
from urllib.parse import urlencode

class RateLimitError(Exception):
  def __init__(self, message):
    super().__init__(message)

class ClientError(Exception):
  def __init__(self, message):
    super().__init__(message)

class Client(object):
  def __init__(self, api_key=""):
    self.api_key = api_key
    self.BASE_URL = "http://www.opensecrets.org/api/?apikey={api_key}&method={method}&output=json&{params}"

  def fetch(self, method, **kwargs):
    params = urlencode(kwargs)
    url = self.BASE_URL.format(api_key=self.api_key, method=method, params=params)

    res = requests.get(url)
    
    if res.status_code == 400 and res.text == "call limit has been reached":
      raise RateLimitError(res.text)

    if res.status_code != 200:
      raise ClientError(f"{res.content}")

    return res.json()["response"]


  def get_legislators_for_state(self, state_code=""):
    """
    Fetch legislators by state
    https://www.opensecrets.org/api/?method=getLegislators&output=doc
    """
    res = self.fetch("getLegislators", id=state_code)
    
    # this is an array of legislators
    return res["legislator"]

  
  def get_legislator_by_cid(self, cid=""):
    """
    Same endpoint, same parameter key, but different output format
    https://www.opensecrets.org/api/?method=getLegislators&output=doc
    """
    res = self.fetch("getLegislators", id=cid)
    
    # this is a single legislator from the same endpoint
    return res["legislator"]


  def get_candidate_summary(self, cid="", cycle=None):
    """
    Summary of fundraising information for candidate
    'cycle' is an even year, e.g. 2016, 2018, 2020
    blank means get most recent
    https://www.opensecrets.org/api/?method=candSummary&output=doc
    """

    kwargs = {"id": cid}

    if cycle:
      kwargs["cycle"] = cycle

    res = self.fetch("candSummary", **kwargs)
    """
    cand.json()["response"]["summary"]["@attributes"]
    Out[73]:
    {'cand_name': 'Norcross, Don',
    'cid': 'N00036154',
    'cycle': '2022',
    'state': 'NJ',
    'party': 'D',
    'chamber': 'H',
    'first_elected': '2014',
    'next_election': '2022',
    'total': '2018825.46',
    'spent': '2862551.42',
    'cash_on_hand': '1080937.77',
    'debt': '0',
    'origin': 'Center for Responsive Politics',
    'source': 'https://www.opensecrets.org/members-of-congress/summary?cid=N00036154&cycle=2022',
    'last_updated': '10/19/2022'}
    """
    return res["summary"]["@attributes"]

  def get_candidate_contributors(self, cid="", cycle=None):
    """
    Summary of candidate's top contributing organizations
    'cycle' is an even year, e.g. 2016, 2018, 2020
    blank cycle means get most recent cycle
    https://www.opensecrets.org/api/?method=candContrib&output=doc
    """

    kwargs = {"cid": cid}

    if cycle:
      kwargs["cycle"] = cycle

    res = self.fetch("candContrib", **kwargs)
    # OpenSecrets docs claims this *must* be displayed with published data
    # candContrib.json()["response"]["contributors"]["@attributes"]["notice"]
    # candContrib.json()["response"]["contributors"]["@attributes"]["cycle"] # cycle for extra clarity

    """
    # candContrib.json()["response"]["contributors"]["contributor"]
    # This gives a list of objects that look like the below
    {'@attributes': {'org_name': 'L3Harris Technologies',
      'total': '20040',
      'pacs': '20000',
    'indivs': '40'}},
      """
    return res["contributors"]["contributor"]

  def get_candidate_top_ten_industries(self, cid="", cycle=""):
    """
    Top ten industries contributing to a given candidate
    cycle indicates even numbered election year
    blank cycle means most recent
    https://www.opensecrets.org/api/?method=candIndustry&output=doc
    """
    kwargs = {"cid": cid}

    if cycle:
      kwargs["cycle"] = cycle

    res = self.fetch("candIndustry", **kwargs)
    # industries.json()["response"]["industries"]["@attributes"]["last_updated"]
    # industries.json()["response"]["industries"]["@attributes"]["cycle"]
    """
    industries.json()["response"]["industries"]["industry"]
    # This gives a 10-item list of objects that look like the below
    {'@attributes': {'industry_code': 'K01',
    'industry_name': 'Lawyers/Law Firms',
    'indivs': '2936543',
    'pacs': '191000',
    'total': '3127543'}}
    """
    industries = res["industries"]
    return {
      "data": industries["industry"],
      "last_updated": industries["@attributes"]["last_updated"],
      "cycle": industries["@attributes"]["cycle"],
    }

  def get_candidate_total_by_sector(self, cid="", cycle=""):
    """
    https://www.opensecrets.org/api/?method=candSector&output=doc
    """
    kwargs = {"cid": cid}

    if cycle:
      kwargs["cycle"] = cycle

    res = self.fetch("candSector", **kwargs)
    """
    # sectors.json()["response"]["sectors"]["@attributes"]["last_updated"]
    # sectors.json()["response"]["sectors"]["@attributes"]["cycle"]
    # sectors.json()["response"]["sectors"]["sector"]
    returns a list of objects that look like
    {'@attributes': {'sector_name': 'Transportation',
    'sectorid': 'M',
    'indivs': '238492',
    'pacs': '216526',
    'total': '455018'}}
    """
    sectors = res["sectors"]

    return {
      "data": sectors["sector"],
      "last_updated": sectors["@attributes"]["last_updated"],
      "cycle": sectors["@attributes"]["cycle"]
    }
