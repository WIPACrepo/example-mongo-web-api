from rest_tools.server import Auth, from_environment

default_config = {
    'AUTH_SECRET': 'secret',
}
config = from_environment(default_config)

print(Auth(config['AUTH_SECRET']).create_token("sub"))
