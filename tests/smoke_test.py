from coicop_query import get_cmd, query_cmd
import argparse

get_cmd.run(argparse.Namespace(code="02"))
query_cmd.run(
    argparse.Namespace(
        query='"video game" AND "consoles"',
        max_level=4,
        min_level=2,
        limit=10,
        select="code,title,intro",
        sort="level:DESC,code:ASC",
    )
)
