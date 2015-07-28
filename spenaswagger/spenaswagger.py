import argparse
from .swagit import swagit


def main():
    parser = argparse.ArgumentParser(description="Regenerate the API")
    parser.add_argument('--user', default="admin", help="API user", required=False)
    parser.add_argument('--password', default="admin", help="API password", required=True)
    parser.add_argument('--url', default="http://localhost", help="API url", required=True)

    args = parser.parse_args()

    datamodel = swagit(args.user, args.password, args.url)

    from .pyswagger import gen_py
    gen_py(datamodel)


if __name__ == "__main__":
    main()
