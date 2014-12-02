"""
Generates statistics about the persistence of content contributed
in Wikipedia.  This script expects one or two columns of TSV input
to stdin (<rev_id>, <page_id>) and will print a TSV dataset to
stdout:

* rev_id : int
* page_id : int
* user_id : int|None
* user_text : str
* token : str
* revs_persisted : int
* non_self_revs_persisted : int
* censored : bool

Usage:
    ./token_stats --api=<url>
                  [--include=<regex>] [--exclude=<regex>]
                  [--revert-radius=<num>] [--future-revisions=<num>]

Options:
    --api=<url>               The URL to a mediawiki API to query
    --include=<regex>         A regex to filter for interesting tokens to
                              include [default: <all>]
    --exclude=<regex>         A regex to exclude uninteresting tokens
                              [default: <none>]
    --revert-radius=<num>     The number of revisions a revert can cross
                              [default: 15]
    --future-revisions=<num>  The maximum number of revisions to process into
                              the future
                              [default: 15]
"""
import re
import sys
import traceback

import docopt
from mw.api import Session
from mw.lib import persistence


def read_rev_pages(f):
    
    for line in f:
        parts = line.strip().split("\t")
        
        rev_id = int(parts[0])
        
        if len(parts) == 2:
            page_id = int(parts[1])
        else:
            page_id = None
        
        yield rev_id, page_id
    
def encode(val):
    if val == None:
        return "NULL"
    elif type(val) == bytes:
        val = str(bytes, 'utf-8', "replace")
    else:
        val = str(val)
    
    return val.replace("\t", "\\t").replace("\n", "\\n")

def main():
    args = docopt.docopt(__doc__)
    session = Session(args['--api'])
    
    if args['--include'] == "<all>":
        include = lambda t: True
    else:
        include_re = re.compile(args['--include'], re.UNICODE)
        include = lambda t: bool(include_re.search(t))
        
    if args['--exclude'] == "<none>":
        exclude = lambda t: False
    else:
        exclude_re = re.compile(args['--exclude'], re.UNICODE)
        exclude = lambda t: bool(exclude_re.search(t))
    
    revert_radius = int(args['--revert-radius'])
    future_revisions = int(args['--future-revisions'])
    
    rev_pages = read_rev_pages(sys.stdin)
    run(rev_pages, session, include, exclude, revert_radius, future_revisions)
    
def run(rev_pages, session, include, exclude, revert_radius, future_revisions):
    
    print("\t".join(["rev_id", "page_id", "user_id", "user_text", "token",
                     "revs_persisted", "non_self_revs_persisted", "censored"]))
    
    for rev_id, page_id in rev_pages:
        try:
            rev, added, future_revs = \
                    persistence.api.score(session, rev_id, page_id=page_id,
                                          revert_radius=revert_radius,
                                          future_revisions=future_revisions,
                                          properties={'user', 'userid'})
        except:
            sys.stderr.write(traceback.format_exc() + "\n")
        
        for token in added:
            if include(token.text) and not exclude(token.text):
                print("\t".join(encode(v) for v in [
                    rev['revid'],
                    rev['page']['pageid'],
                    rev.get('userid'),
                    rev.get('user'),
                    token.text,
                    len(token.revisions)-1, # Discounted for the added revision
                    sum((rev.get('userid'), rev.get('user')) != \
                        (r.get('userid'), r.get('user')) \
                        for r in token.revisions),
                    len(future_revs) == 0 or \
                        future_revs[-1] == token.revisions[-1]
                ]))

if __name__ == "__main__": main()
