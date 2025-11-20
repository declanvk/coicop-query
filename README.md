# coicop-query

Tool for querying COICOP categories

## Development

This tool bakes an sqlite database into the package structure. In order to initialize that value, you must run

```bash
uv run python -c "import coicop_query; import sys; sys.exit(coicop_query.bake());" --verbose
```

ahead of running or building or publishing the command.
