from core.pipeline_runner import PipelineRunner

runner = PipelineRunner()

results = runner.analyze_today()

print()

print("Matches:", len(results))

print()

if results:

    context = results[0]

    print(context.match.home_team)

    print(context.match.away_team)

    print()

    print(context.features.to_dict())

    print()

    print(context.results)