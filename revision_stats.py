"""
Computes per-revision statistics about edit quality from token persistence
statistics.  Assumes that a TSV will be piped to <stdin> and that rows are
partitioned by rev_id.

* rev_id : int
* page_id : int
* user_id : int
* user_text : str
* tokens_added : int
* tokens_persisted : int
* sum_log_persistence : float
* censored : bool

Usage:
    revision_stats [--min-persistence=<num>] [--only-revisions-by-others]
                   [--include=<regex>] [--exclude=<regex>]

Options:
    --min-persistence=<num>     The minimum number of revisions a token must
                                survive before being considered "persisted"
                                [default: 5]
    --only-revisions-by-others  Only include revisions by other users
    --include=<regex>           A regex to filter for interesting tokens to
                                include [default: <all>]
    --exclude=<regex>           A regex to exclude uninteresting tokens
                                [default: <none>]
"""
import sys
from itertools import groupby
from math import log

import docopt


def encode(val):
    if val == None:
        return "NULL"
    elif type(val) == bytes:
        val = str(bytes, 'utf-8', "replace")
    else:
        val = str(val)
    
    return val.replace("\t", "\\t").replace("\n", "\\n")

def decode(val, type):
    if val == "NULL":
        return None
    else:
        return type(str(val).replace("\\t", "\t").replace("\\n", "\n"))

def read_token_stats(f):
    types = [int, int, int, str, str, int, int, bool]
    headers = f.readline().strip().split("\t")
    
    for line in f:
        values = [decode(v, t) for t, v in zip(types, line.strip().split("\t"))]
        
        yield {h:v for h, v in zip(headers, values)}
    

def main():
    args = docopt.docopt(__doc__)
    
    token_stats = read_token_stats(sys.stdin)
    
    min_persistence = int(args['--min-persistence'])
    only_revisions_by_others = bool(args['--only-revisions-by-others'])
    
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
    
    run(token_stats, min_persistence, only_revisions_by_others,
        include, exclude)
    
def run(token_stats, min_persistence, only_revisions_by_others,
        include, exclude):
    
    rev_token_stats = groupby(token_stats,
                               lambda ts: (ts['rev_id'], ts['page_id'],
                                           ts['user_id'], ts['user_text']))
    
    print("\t".join(["rev_id", "page_id", "user_id", "user_text",
                     "tokens_added", "tokens_persisted", "sum_log_persistence",
                     "censored"]))
    
    for (rev_id, page_id, user_id, user_text), token_stats in rev_token_stats:
        
        tokens_added = 0
        tokens_persisted = 0
        sum_log_persistence = 0
        censored = False
        
        for ts in token_stats:
            
            if include(ts['token']) and not exclude(ts['token']):
                tokens_added += 1
                
                if only_revisions_by_others:
                    if ts['non_self_revs_persisted'] > 0:
                        sum_log_persistence += \
                            log(ts['non_self_revs_persisted'])
                    
                    if ts['non_self_revs_persisted'] >= min_persistence:
                        tokens_persisted += 1
                    else:
                        if ts['censored']: censored = True
                else:
                    if ts['revs_persisted'] > 0:
                        sum_log_persistence += log(ts['revs_persisted'])
                    
                    if ts['revs_persisted'] >= min_persistence:
                        tokens_persisted += 1
                    else:
                        if ts['censored']: censored = True
                    
                
            
        
        print("\t".join(encode(v) for v in [
            rev_id,
            page_id,
            user_id,
            user_text,
            tokens_added,
            tokens_persisted,
            sum_log_persistence,
            censored
        ]))

if __name__ == "__main__": main()
