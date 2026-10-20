from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from .config import ROOT, DB_PATH, HOST, PORT
from .db import initialize, table_counts
from .repository import Repository
from .importers import import_csv, import_json
from .analytics import MARKETS
from .reporting import generate_report
from .provider_manager import ProviderManager


def build_parser():
    p=argparse.ArgumentParser(prog="matchsieve",description="Local-first MatchSieve research workspace")
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('init',help='Create/update the local SQLite schema')
    c=sub.add_parser('counts',help='Show local archive counts')
    ic=sub.add_parser('import-csv',help='Import fixtures or historical results from CSV'); ic.add_argument('path'); ic.add_argument('--source-key',default='csv_import'); ic.add_argument('--source-url')
    ij=sub.add_parser('import-json',help='Import fixtures/results from JSON'); ij.add_argument('path'); ij.add_argument('--source-key',default='json_import')
    ls=sub.add_parser('fixtures',help='List stored fixtures'); ls.add_argument('--search',default=''); ls.add_argument('--limit',type=int,default=50)
    rs=sub.add_parser('research',help='Build a QQR evidence report from local stored data'); rs.add_argument('--fixture-id',type=int,required=True); rs.add_argument('--market',choices=list(MARKETS),default='RESEARCH_BRIEF'); rs.add_argument('--ollama',action='store_true')
    pr=sub.add_parser('providers',help='Show source catalogue and enabled status')
    fe=sub.add_parser('fetch',help='Fetch from one explicitly enabled provider'); fe.add_argument('--provider',required=True,choices=['sportscore','openligadb','football_data_org']); fe.add_argument('--date'); fe.add_argument('--status',default='upcoming'); fe.add_argument('--competition'); fe.add_argument('--league'); fe.add_argument('--season'); fe.add_argument('--date-from'); fe.add_argument('--date-to')
    sv=sub.add_parser('serve',help='Launch the local mobile-friendly research desk'); sv.add_argument('--host',default=HOST); sv.add_argument('--port',type=int,default=PORT)
    se=sub.add_parser('search-kb',help='Search saved research/knowledge documents'); se.add_argument('query'); se.add_argument('--limit',type=int,default=10)
    sub.add_parser('index-kb',help='Refresh Markdown knowledge-base indexes and current weekly digest')
    ex=sub.add_parser('export-fixtures',help='Export all canonical fixtures/results to CSV for Excel review'); ex.add_argument('--path',default=None)
    ea=sub.add_parser('export-archive',help='Stream all archive tables to line-delimited JSON for backup/handoff'); ea.add_argument('--path',default=None)
    si=sub.add_parser('sync-inbox',help='Import new CSV/JSON files from data/inbox and refresh knowledge indexes'); si.add_argument('--inbox',default=None); si.add_argument('--reimport-unchanged',action='store_true')
    return p


def main():
    args=build_parser().parse_args()
    if args.command=='init': print(f"Local database ready: {initialize()}"); return
    repo=Repository()
    if args.command=='counts': print(json.dumps(table_counts(repo.db_path),indent=2)); return
    if args.command=='import-csv': print(json.dumps(import_csv(args.path,repo,args.source_key,args.source_url),indent=2,ensure_ascii=False)); return
    if args.command=='import-json': print(json.dumps(import_json(args.path,repo,args.source_key),indent=2,ensure_ascii=False)); return
    if args.command=='fixtures': print(json.dumps(repo.list_fixtures(args.search,args.limit),indent=2,ensure_ascii=False)); return
    if args.command=='research':
        result=generate_report(args.fixture_id,args.market,repo,args.ollama)
        print(json.dumps({k:result[k] for k in ('report_id','path','status','llm_used')},indent=2)); return
    if args.command=='providers': print(json.dumps(ProviderManager(repo).catalog(),indent=2)); return
    if args.command=='fetch':
        kwargs={}
        if args.provider=='sportscore': kwargs={'date':args.date or __import__('datetime').datetime.now(__import__('datetime').timezone.utc).date().isoformat(),'status':args.status,'competition':args.competition}
        elif args.provider=='openligadb': kwargs={'league':args.league or '', 'season':args.season or ''}
        else: kwargs={'date_from':args.date_from or args.date or __import__('datetime').datetime.now(__import__('datetime').timezone.utc).date().isoformat(),'date_to':args.date_to or args.date or __import__('datetime').datetime.now(__import__('datetime').timezone.utc).date().isoformat(),'competition':args.competition}
        print(json.dumps(ProviderManager(repo).fetch(args.provider,**kwargs),indent=2)); return
    if args.command=='search-kb': print(json.dumps(repo.search_knowledge(args.query,args.limit),indent=2,ensure_ascii=False)); return
    if args.command=='index-kb':
        from .kb_writer import refresh_indexes
        print(json.dumps(refresh_indexes(repo),indent=2,ensure_ascii=False)); return
    if args.command=='export-fixtures':
        from .exports import export_fixtures_csv
        print(json.dumps(export_fixtures_csv(repo,Path(args.path) if args.path else None),indent=2,ensure_ascii=False)); return
    if args.command=='export-archive':
        from .exports import export_archive_jsonl
        print(json.dumps(export_archive_jsonl(repo,Path(args.path) if args.path else None),indent=2,ensure_ascii=False)); return
    if args.command=='sync-inbox':
        from .inbox_sync import sync_inbox
        print(json.dumps(sync_inbox(repo,Path(args.inbox) if args.inbox else None,args.reimport_unchanged),indent=2,ensure_ascii=False)); return
    if args.command=='serve':
        from .webserver import serve
        serve(args.host,args.port,repo); return

if __name__=='__main__': main()
