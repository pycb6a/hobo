==========
Annotation
==========
Hobo is a small test to check your web application quickly, it parses pages and verifies some assertions

==============
How to install
==============
Execute in shell next commands:

.. code:: shell

    $ hg clone https://hg@bitbucket.org/pycb6a/hobo
    $ cd hobo
    $ virtualenv .venv
    $ . .venv/bin/activate
    $ pip install -r requirements.txt

=============
How to set up
=============
Change config.yml:

.. code:: yaml

    site:
      url: http://example.com           # web application's url
      auth_path: /login/auth            # (optional) path to the authorization page
      login: admin                      # (optional) username
      password: admin                   # (optional) password
    settings:
      feed_uri: items.json              # uri to export parsed data
      download_delay: 0.5               # wait before downloading consecutive pages
      concurrent_requests: 3            # a maximum number of simultaneous requests
    #  closespider_itemcount: 3         # (optional, debug) Scrapy's CLOSESPIDER_ITEMCOUNT
    rule:                               # a behaviour for crawling the site
      deny:                             # single regular expressions that the urls must match in order to be excluded
        - contacts
        - form
      tags:                             # tags to consider when extracting links.
        - a
        - area
    assertions:                         # a list of the assertions
      -
        key: status_code                # unique key
        attribute: status               # an attribute of Scrapy's Response object (status, header, text)
        matcher:                        # unittest assert methods (https://docs.python.org/3/library/unittest.html#assert-methods)
          - equal                       # -> assertEqual
          - 200
        description: HTTP status code   # a description of the assertion
      -
        key: content_type
        attribute: headers
        field: Content-Type             # a header's field
        matcher:
          - text/html
          - in                          # text/html in content_type (assertIn('text/html', content_type))
          -                             # used if a scraped item isn't the first argument
        description: Content type
      -
        key: title
        attribute: text
        selector:                       # used to select certain part of the html
          by: xpath                     # a way of extracting data (xpath, css, re)
          path: //title                 # a XPATH/CSS query or a regular expression to apply
          extract: first                # extract all data or a first element (first, all)
        matcher:
          -
          - is not none
        description: Page title

=============
How to launch
=============
Execute in shell the next command:

.. code:: shell

    $ python -m test


===================
How to get a report
===================
JUnit-like report is generated in `test-reports` directory after finishing tests