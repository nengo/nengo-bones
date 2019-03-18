def pytest_addoption(parser):
    parser.addoption("--test-arg", action="store_true", default=False,
                     help="Used to test custom pytest arguments")
