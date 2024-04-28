#!/usr/bin/env python3

import argparse
import sys
import webbrowser
from getpass import getpass
import diskcache as dc

cache = dc.Cache('tmp')

def get_from_cache(key, prompt):
    """ Retrieve a value from the cache or prompt the user for it if not available. """
    value = cache.get(key)
    if value is None:
        value = input(f"Enter value for {key}: ")
        cache.set(key, value)
    return value

def main():
    parser = argparse.ArgumentParser(description='Manage JWT tokens with diskcache.')
    parser.add_argument('--env', help='Override the ENV value in the URL')
    parser.add_argument('--set-env', help='Set DEFAULT_ENV in the cache')
    parser.add_argument('--expiry', type=int, help='Set DEFAULT_EXPIRY in the cache')
    parser.add_argument('--renew', action='store_true', help='Renew the JWT token')
    parser.add_argument('--exp-var', help='Set the name of the environment variable for export')
    parser.add_argument('--export', action='store_true', help='Export JWT token to environment variable')

    args = parser.parse_args()

    if args.set_env:
        cache.set('DEFAULT_ENV', args.set_env)
    if args.expiry:
        cache.set('DEFAULT_EXPIRY', args.expiry)

    env = args.env if args.env else get_from_cache('DEFAULT_ENV', 'Default environment (ENV)')
    resolve_path = get_from_cache('RESOLVE_PATH', 'Resolve path (e.g., ID=123)')
    default_expiry = int(get_from_cache('DEFAULT_EXPIRY', 'Default expiry (seconds)'))

    jwt_token = cache.get('jwt_token')

    if args.renew or not jwt_token:
        url = f'https://auth.{env}.foo.net/{resolve_path}'
        webbrowser.open(url)
        print("Please paste the JWT token:")
        jwt_token = getpass()
        cache.set('jwt_token', jwt_token, expire=default_expiry)

    if args.export or jwt_token:
        exp_var = args.exp_var if args.exp_var else 'JWT_TOKEN'
        print(f"export {exp_var}={jwt_token}")

    sys.stdout.write(jwt_token)

if __name__ == '__main__':
    main()
