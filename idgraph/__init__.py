# -*- coding: utf-8 -*-

import argparse
import json
import os
import requests
import shlex
import sys
from IPython.display import Markdown


JINJA2_ENABLED = True
try:
    import jinja2
except ImportError:  # pragma: no cover
    JINJA2_ENABLED = False

JMESPATH_ENABLED = True
try:
    import jmespath
except ImportError:  # pragma: no cover
    JMESPATH_ENABLED = False

__author__ = """John Bjorn Nelson"""
__email__ = 'jbn@abreka.com'
__version__ = '0.0.1'


DEFAULT_ADDR = "localhost:8080"

def parse_line_magic_args(line):
    parser = argparse.ArgumentParser(prog="%%dgraph", description="Cell magic for dgraph", add_help=False)

    parser.add_argument("--json", dest="as_json", action="store_true", default=False,
                        help="Send command as JSON instead of RDF or GraphQL")
    parser.add_argument("--addr", dest="addr", default=DEFAULT_ADDR,
                        help="Address of dgraph")
    parser.add_argument("--mutate", dest="mutate", action="store_true", default=False,
                        help="Do a mutation")
    parser.add_argument("--alter", dest="alter", action="store_true", default=False,
                        help="Do an alteration")
    parser.add_argument("--skip", dest="skip", action="store_true", default=False,
                        help="Do not send this cell for execution")
    parser.add_argument("--into", dest="into", default="",
                        help="store output json into variable")
    parser.add_argument("--jmespath", dest="jmespath", default="",
                        help="extract response via a jmespath")
    parser.add_argument("--as-jinja", dest="interpolate_jinja", action="store_true", default=False,
                        help="Interpolate as a jinja2 template")
    parser.add_argument('--print-jinja', dest='print_jinja',
                        action='store_true', default=False,
                        help="Print interpolated jinja source then bail.")

    parser.add_argument("--full-resp", dest="full_resp", action="store_true", default=False,
                        help="Report full response instead of data only")

    args = parser.parse_args(shlex.split(line))

    if args.addr == DEFAULT_ADDR:
        override_addr = os.environ.get('DGRAPH_ADDR')
        if override_addr:
            args.addr = override_addr

    return args


def to_markdown_listing(code, kind):
    tmpl = "```{kind}\n{code}\n```\n".format(kind=kind, code=code)
    return Markdown(data=tmpl)


CONTENT_TYPE_MAP = {
    True: {},
    False: {
        'alter': 'application/graphql+-',
        'mutate': 'application/rdf',
        'query': 'application/graphql+-'
    }
}

ENDPOINTS = {
    'query': "/query",
    'mutate': "/mutate?commitNow=true",
    'alter': "/alter"
}


def get_user_ns():
    return sys.modules['__main__']


def write_into(name, obj):
    vars(get_user_ns())[name] = obj


JSON_MIME = 'application/json'


def load_and_interpolate_jinja2(src, ns):
    # The FileSystemLoader should operate in the current working directory.
    # By assumption, extended jinja templates aren't temporary files --
    # the user wrote them by hand. They are part of code you would want in
    # your repository!
    fs_loader = jinja2.FileSystemLoader(os.getcwd())
    tmpl_env = jinja2.Environment(loader=fs_loader,
                                  variable_start_string="<<",
                                  variable_end_string=">>",
                                  block_start_string="<%",
                                  block_end_string="%>")

    # The final template -- the one that may extend a custom template --
    # may be in the current directory or in a temporary one. So, it's
    # passed as a string.
    tmpl = tmpl_env.from_string(src)

    return tmpl.render(**ns)


def execute_request(args, cell):
    assert not (args.mutate and args.alter), "It's alter either mutate, not both"

    kind = 'query'
    if args.mutate:
        kind = 'mutate'
    elif args.alter:
        kind = 'alter'

    headers = {
        'Content-type': CONTENT_TYPE_MAP[args.as_json].get(kind, JSON_MIME)
    }
    url = "http://{}{}".format(args.addr, ENDPOINTS[kind])

    return requests.post(url, headers=headers, data=cell.encode('utf8')).json()


def dgraph(line, cell):
    args = parse_line_magic_args(line)
    if args.skip:
        return Markdown("Execution skipped. Remove `--skip` flag to execute.")

    if args.interpolate_jinja:

        if not JINJA2_ENABLED:
            print("Please install jinja2", file=sys.stderr)
            print("$ pip install jinja2", file=sys.stderr)
            return

        cell = load_and_interpolate_jinja2(cell, vars(get_user_ns()))

        # TODO: Find appropriate language override in kind?
        if args.print_jinja:
            return to_markdown_listing(cell, "text")

    resp = full_resp = execute_request(args, cell)

    # If full_resp is not set and there is a data field, limit the returned
    # response to just that to make things less noisy. If jmespath is set
    # execute the search and return the result.

    if args.jmespath != '':

        if not JMESPATH_ENABLED:
            print("Please install jmespath", file=sys.stderr)
            print("$ pip install jmespath", file=sys.stderr)
            return

        resp = jmespath.search(args.jmespath, resp)

    elif not args.full_resp and 'data' in resp:
        resp = resp['data']

    # Mimicking expected behavior with `_` auto-assignment in IPython this
    # magic assigns the *filtered* result to `_dgraph` and the full result
    # to `_dgraph_full`. However, if the user specifies an `into` argument
    # assignment goes to `{into}` and `{into}_full` instead.
    output_var = args.into if args.into != '' else '_dgraph'
    write_into(output_var, resp)
    write_into(output_var + "_full", full_resp)

    # When an error occurs, this magic writes it to stderr so that it is
    # clearly a different interaction (should be written to a red
    # background in Jupyter.) Only the error messages are written.
    # Full inspection via `_dgraph_full` still possible.
    if 'errors' in full_resp and not full_resp.get('data'):
        for error in full_resp['errors']:
            print(error.get("message"), file=sys.stderr)
    else:
        return to_markdown_listing(json.dumps(resp, indent="    "), "json")


def load_ipython_extension(ipython):  # pragma: no cover
    ipython.register_magic_function(dgraph, magic_kind='cell')
