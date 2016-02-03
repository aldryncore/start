import start


def test_expandvars():
    env = {"NAME": "Fry"}

    tests = [
        # just vars
        ('$NAME', 'Fry', env),
        ('${NAME}', 'Fry', env),
        ('${NAME:-Zoidberg}', 'Fry', env),
        ('${NAME:-Zoidberg}', 'Zoidberg', {}),

        # quoted
        ('"$NAME"', '"Fry"', env),
        ('"${NAME}"', '"Fry"', env),
        ('"${NAME:-Zoidberg}"', '"Fry"', env),
        ('"${NAME:-Zoidberg}"', '"Zoidberg"', {}),

        # single quoted
        ("'$NAME'", "'Fry'", env),

        # multiple vars and special characters
        (
            '$FRY ${ZOIDBERG:-whoopwhoop} ${NOTZOIDBERG:-whoopwhoop}',
            'Fry Zoidberg whoopwhoop',
            {
                'FRY': "Fry",
                "AMY": "Amy",
                "ZOIDBERG": "Zoidberg",
            }
        ),

        # inside echo statements
        ('echo "Hi $NAME"', 'echo "Hi Fry"', env),
        ('echo "Hi ${NAME}"', 'echo "Hi Fry"', env),
        ('echo "Hi ${NAME:-Zoidberg}"', 'echo "Hi Fry"', env),
        ('echo "Hi ${NAME:-Zoidberg}"', 'echo "Hi Zoidberg"', {}),

        # unquoted echo statements
        ('echo Hi $NAME', 'echo Hi Fry', env),
        ('echo Hi ${NAME}', 'echo Hi Fry', env),
        ('echo Hi ${NAME:-default}', 'echo Hi Fry', env),
        ('echo Hi ${NAME:-default}', 'echo Hi default', {}),

        # special cases
        ('${LS_CMD} -lAF', 'ls -lAF', {'LS_CMD': "ls"}),
        ('\\', '\\', {}),
        ('\\\\', '\\\\', {}),
    ]
    for test in tests:
        assert test[1] == start.expandvars(test[0], env=test[2])


def test_parse_command():
    env = {"NAME": "Fry"}
    tests = [
        # just vars
        ('"$NAME"', ['Fry'], env),
        ('${NAME}', ['Fry'], env),
        ('${NAME:-Zoidberg}', ['Fry'], env),
        ('${NAME:-Zoidberg}', ['Zoidberg'], {}),

        # inside echo statements
        ('echo "Hi $NAME"', ['echo', 'Hi Fry'], env),
        ('echo "Hi ${NAME}"', ['echo','Hi Fry'], env),
        ('echo "Hi ${NAME:-Zoidberg}"', ['echo', 'Hi Fry'], env),
        ('echo "Hi ${NAME:-Zoidberg}"', ['echo', 'Hi Zoidberg'], {}),

        # unquoted echo statements
        ('echo Hi $NAME', ['echo', 'Hi', 'Fry'], env),
        ('echo Hi ${NAME}', ['echo','Hi', 'Fry'], env),
        ('echo Hi ${NAME:-Zoidberg}', ['echo', 'Hi', 'Fry'], env),
        ('echo Hi ${NAME:-Zoidberg}', ['echo', 'Hi', 'Zoidberg'], {}),

        # special cases
        ('${LS_CMD} -lAF', ['ls', '-lAF'], {'LS_CMD': "ls"}),
    ]
    for test in tests:
        assert test[1] == start.parse_command(test[0], env=test[2])
