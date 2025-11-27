from coicop_query import get_cmd, query_cmd
import argparse

print("Running `coicop get 02`...")
get_cmd.run(argparse.Namespace(code="02"))
print('\nRunning `coicop query ... \'"video game" AND "consoles"\'`...')
query_cmd.run(
    argparse.Namespace(
        query='"video game" AND "consoles"',
        max_level=4,
        min_level=2,
        limit=10,
        select="code,title,intro",
        sort="level:DESC,code:ASC",
        excludes_query=None,
    )
)
print('\nRunning `coicop query "alcoholic" --excludes-query "food"`...')
query_cmd.run(
    argparse.Namespace(
        query="alcoholic",
        select="code,title,excludes",
        max_level=None,
        min_level=None,
        limit=None,
        sort=None,
        excludes_query="food",
    )
)
