# File: email_format.pt
# Author: Alexander Rymdeko-Harvey(@Killswitch-GUI)
# License: BSD 3-Clause
# Copyright (c) 2016, Alexander Rymdeko-Harvey 
# All rights reserved. 
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met: 
#  * Redistributions of source code must retain the above copyright notice, 
#    this list of conditions and the following disclaimer. 
#  * Redistributions in binary form must reproduce the above copyright 
#    notice, this list of conditions and the following disclaimer in the 
#    documentation and/or other materials provided with the distribution. 
#  * Neither the name of  nor the names of its contributors may be used to 
#    endorse or promote products derived from this software without specific 
#    prior written permission. 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
# POSSIBILITY OF SUCH DAMAGE.

import requests


class email_format(object):
  '''
  Base clase for init of the package. This will handle
  the initial object creation for conducting basic functions.
  '''

  def __init__(self, verbose=False):
    pass



class emailhunter_exception(Exception):
    pass

class email_hunter(object):
  '''
  A class to query emailhunter free and paid API.
  This will allow you gather a already determined 
  format potentialy.

  email = pass a single str() email
  verbose = for verbose cli print statment's 
  api_key = opt apikey for paid emailhunter members
  '''
  EMAILHUNTER_TRIAL_BASE_URL = 'https://emailhunter.co/trial/v1/search?offset=0&domain='
  EMAILHUNTER_API_BASE_URL = 'https://api.emailhunter.co/v1/search?domain='
  EMAILHUNTER_URL_FORMAT = '&format=json'
  EMAILHUNTER_API_KEY = '&api_key='


  STATUS_CODE_MSG = { 200 : "The request was successful.", 401 : "No valid API key provided.", 500 : "Something went wrong on Email Hunter's end."}
  STATUS_CODE_OK = 200
  STATUS_CODE_UNAUTH = 401
  STATUS_CODE_SER_SRT = 500
  STATUS_CODE_SER_STP = 599


  def __init__(self, api_key='', timeout=5, retrytime=3, useragent='', verbose=False):

    self.api_key = str(api_key)
    self.useragent = str(useragent)
    self.timeout = int(timeout)
    self.retrytime = int(retrytime)
    self.verbose = bool(verbose)

  def emailhunter_format(self, domain):
    '''
    A function to use EmailHunter to use their
    SON API to detect the email format.
    '''
    try:
      if not self.api_key:
        # build the trial url for email hunter
        url = self.EMAILHUNTER_TRIAL_BASE_URL + str(domain) + self.EMAILHUNTER_URL_FORMAT
      else:
        # build the API url for email hunter
        url = self.EMAILHUNTER_API_BASE_URL + str(domain) + EMAILHUNTER_API_KEY + self.apikey + self.EMAILHUNTER_URL_FORMAT
    except ValueError as ve:
      raise emailhunter_exception("Error building url: %s" % (ve))
    ru = request_url(useragent=self.useragent, timeout=self.timeout, retrytime=self.retrytime, statuscode=True)
    r, status = ru.request_url(url)
    self.emailhunter_status_code(status)
    json_results = r.json()
    return self.domain_search_json(json_results)


  def emailhunter_status_code(self, status):
    '''
    Takes in a status code from
    the request to parse.
    '''
    if status == self.STATUS_CODE_OK:
      return 
    if status == self.STATUS_CODE_UNAUTH:
      raise emailhunter_exception("Error making reauest EmailHunter: %s" % (self.STATUS_CODE_MSG[self.STATUS_CODE_UNAUTH]))
    if status >= self.STATUS_CODE_SER_SRT and status <= STATUS_CODE_SER_STP:
      raise emailhunter_exception("Error making reauest EmailHunter: %s" % (self.STATUS_CODE_MSG[self.STATUS_CODE_SER_SRT]))
    else:
      raise emailhunter_exception("[ERROR] Unknown EmailHunter request status code: %s" % (status))

  def domain_search_json(self, json):
    '''
    Takes in JSON formated from EmailHunter.
    json = json object from requets
    '''
    patternDict = {}
    if json['status'] == "success":
      if json['pattern']:
        pattern = json['pattern']
        if pattern:
            patternDict['pattern'] = True
            patternDict['email_format'] = str(pattern)
    else:
      patternDict['pattern'] = False
    return patternDict

class request_url_exception(Exception):
    pass

class request_url(object):
  '''
  A requests class for making basic,
  web request with robust features that
  are used offten.
  '''

  def __init__(self, useragent='', timeout=5, retrytime=3, statuscode=False, raw=False, verbose=True):

      self.useragent = str(useragent)
      self.timeout = int(timeout)
      self.retrytime = int(retrytime)
      self.statuscode = bool(statuscode)
      self.raw = bool(raw)
      verbose = bool(verbose)

  def request_url(self, url):
    """
    A very simple request function
    This is setup to handle the following parms:

    url = the passed in url to request
    useragent = the useragent to use
    timeout = how long to wait if no "BYTES" rec

    Exception handling will also retry on the event of
    a timeout and warn the user.
    """
    rawhtml = ""
    r = requests.get(url, timeout=self.timeout)
    try:
        r = requests.get(url, timeout=self.timeout)
        rawhtml = r.content
    except requests.exceptions.Timeout:
        #  set up for a retry
        if self.verbose:
            p = ' [!] Request for url timed out, retrying: ' + url
        r = requests.get(url, headers=self.UserAgent, timeout=self.retrytime)
        rawhtml = r.content
    except requests.exceptions.TooManyRedirects:
        # fail and move on, alert user
        if self.verbose:
            p = ' [!] Request for url resulted in bad url: ' + url
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        if self.verbose:
            p = ' [!] Request for url resulted in major error: ' + str(e)
    except Exception as e:
        p = ' [!] Request for url resulted in unhandled error: ' + str(e)
    # just return blank data if failed
    # to prevent bails
    if self.statuscode:
        # return status code and html
        status = r.status_code
        return r, status
    elif self.raw:
        # return raw request object
        return r
    else:
        return rawhtml
