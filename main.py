from parser import parser_flow
from metaflow import Runner
if __name__ == "__main__":
    with Runner('parser.py', show_output=False).run() as running:
        if running.status == 'failed':
            print(f'❌ {running.run} failed:')
        elif running.status == 'successful':
            print(f'✅ {running.run} succeeded:')
        print(f'-- stdout --\n{running.stdout}')
        print(f'-- stderr --\n{running.stderr}')

    # Runner(parser_flow()).run()
