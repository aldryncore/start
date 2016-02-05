import start
import pytest


@pytest.mark.parametrize("cmd,output,env", [
    # just vars
    ('$NAME', b'Fry', {"NAME": "Fry"}),
    ('${NAME}', b'Fry', {"NAME": "Fry"}),
    ('${NAME:-Zoidberg}', b'Fry', {"NAME": "Fry"}),
    ('${NAME:-Zoidberg}', b'Zoidberg', {}),

    # quoted
    ('"$NAME"', b'"Fry"', {"NAME": "Fry"}),
    ('"${NAME}"', b'"Fry"', {"NAME": "Fry"}),
    ('"${NAME:-Zoidberg}"', b'"Fry"', {"NAME": "Fry"}),
    ('"${NAME:-Zoidberg}"', b'"Zoidberg"', {}),

    # single quoted
    ("'$NAME'", b"'Fry'", {"NAME": "Fry"}),

    # multiple vars and special characters
    (
        '$FRY ${ZOIDBERG:-whoopwhoop} ${NOTZOIDBERG:-whoopwhoop}',
        b'Fry Zoidberg whoopwhoop',
        {
            'FRY': "Fry",
            "AMY": "Amy",
            "ZOIDBERG": "Zoidberg",
        }
    ),

    # inside echo statements
    ('echo "Hi $NAME"', b'echo "Hi Fry"', {"NAME": "Fry"}),
    ('echo "Hi ${NAME}"', b'echo "Hi Fry"', {"NAME": "Fry"}),
    ('echo "Hi ${NAME:-Zoidberg}"', b'echo "Hi Fry"', {"NAME": "Fry"}),
    ('echo "Hi ${NAME:-Zoidberg}"', b'echo "Hi Zoidberg"', {}),

    # unquoted echo statements
    ('echo Hi $NAME', b'echo Hi Fry', {"NAME": "Fry"}),
    ('echo Hi ${NAME}', b'echo Hi Fry', {"NAME": "Fry"}),
    ('echo Hi ${NAME:-default}', b'echo Hi Fry', {"NAME": "Fry"}),
    ('echo Hi ${NAME:-default}', b'echo Hi default', {}),

    # special cases
    ('${LS_CMD} -lAF', b'ls -lAF', {'LS_CMD': "ls"}),
    ('\\', b'\\', {}),
    ('\\\\', b'\\\\', {}),
])
def test_expandvars(cmd, output, env):
    assert output == start.expandvars(cmd, env=env)


@pytest.mark.parametrize("cmd,output,env", [
    # just vars
    ('"$NAME"', [b'Fry'], {"NAME": "Fry"}),
    ('${NAME}', [b'Fry'], {"NAME": "Fry"}),
    ('${NAME:-Zoidberg}', [b'Fry'], {"NAME": "Fry"}),
    ('${NAME:-Zoidberg}', [b'Zoidberg'], {}),

    # inside echo statements
    ('echo "Hi $NAME"', [b'echo', b'Hi Fry'], {"NAME": "Fry"}),
    ('echo "Hi ${NAME}"', [b'echo', b'Hi Fry'], {"NAME": "Fry"}),
    ('echo "Hi ${NAME:-Zoidberg}"', [b'echo', b'Hi Fry'], {"NAME": "Fry"}),
    ('echo "Hi ${NAME:-Zoidberg}"', [b'echo', b'Hi Zoidberg'], {}),

    # unquoted echo statements
    ('echo Hi $NAME', [b'echo', b'Hi', b'Fry'], {"NAME": "Fry"}),
    ('echo Hi ${NAME}', [b'echo', b'Hi', b'Fry'], {"NAME": "Fry"}),
    ('echo Hi ${NAME:-Zoidberg}', [b'echo', b'Hi', b'Fry'], {"NAME": "Fry"}),
    ('echo Hi ${NAME:-Zoidberg}', [b'echo', b'Hi', b'Zoidberg'], {}),

    # special cases
    ('${LS_CMD} -lAF', [b'ls', b'-lAF'], {'LS_CMD': "ls"}),

    # tricky cases
    # ------------

    # shell string concatenation
    (
        ''' echo 'I want a single quote here: -> '"'"' <- ' '''.strip(),
        [b'echo', b"I want a single quote here: -> ' <- "],
        {}
    ),
    # shell string concatenation II
    (
        ''' echo "I want a single quote here: -> ' <- " '''.strip(),
        [b'echo', b"I want a single quote here: -> ' <- "],
        {}
    ),
    # shell string concatenation III
    (
        ''' echo "I want a double quote here: -> \\" <- " '''.strip(),
        [b'echo', b'I want a double quote here: -> " <- '],
        {}
    ),
    # subshell
    (
        ''' echo "I want a command result here: -> `cd /;pwd` <- " '''.strip(),
        [b'echo', b'I want a command result here: -> / <- '],
        {}
    ),
])
def test_parse_command(cmd, output, env):
    assert output == start.parse_command(cmd, env=env)


@pytest.mark.parametrize("cmd,output", [
    (
        (
            'web: echo "Hi"\n'
            '# comment for other\n'
            'other: echo "other"'
        ),
        {
            'web': 'echo "Hi"',
            'other': 'echo "other"',
        }
    ),
    (
        (
            'web: run --concurrency=${CONCURRENCY:-4}\n'
            'other: echo "other"'
        ),
        {
            'web': 'run --concurrency=${CONCURRENCY:-4}',
            'other': 'echo "other"',
        }
    ),
])
def test_procfile_parsing(cmd, output):
    parsed_procfile = start.parse_procfile(cmd)
    for service, command in output.items():
        assert parsed_procfile.processes[service] == command
