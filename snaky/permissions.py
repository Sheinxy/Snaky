from snaky.snaky_data import SnakyData

database = SnakyData("data")


def parse_int(value, default=-1):
    try:
        return int(value)
    except:
        return default


def change_permission(new_permission, command_data):
    if not command_data["private"]:
        server = command_data["server"]
        server_folder = command_data["server_folder"]
        arguments = command_data["arguments"]
        command = arguments.split(' ')[0]

        depricated = "enabled" if new_permission == "disabled" else "disabled"

        role_id = parse_int(arguments.split(' ')[0])
        role = server.get_role(role_id)
        if role == None:
            return "B-b-but this role doesn't exist ;-;"
        else:
            default_role = server.default_role
            base = {
                "disabled": {
                    "disable": [default_role.id],
                    "enable": [default_role.id]
                },
                "enabled": {}
            }
            permissions = database.get_data(
                server_folder + "/permissions.json", base)
            if not command in permissions[new_permission]:
                permissions[new_permission][command] = []
            permissions[new_permission][command].append(role_id)
            if command in permissions[depricated] and role_id in permissions[depricated][command]:
                permissions[depricated][command].remove(role_id)
            database.replace_data(
                permissions, server_folder + "/permissions.json")

            return "I %s %s for the role %s ^w^" % (new_permission, command, role.name)

def check_permission(command_data):
    user = command_data["message"].author
    server = command_data["server"]
    server_folder = command_data["server_folder"]
    command = command_data["command"]

    default_role = server.default_role
    base = {
        "disabled": {
            "disable": [default_role.id],
            "enable": [default_role.id]
        },
        "enabled": {}
    }
    permissions = database.get_data(server_folder + "/permissions.json", base)

    if user.guild_permissions.administrator or not command in permissions["disabled"]:
        return True

    highest_disabling = -1
    for role_id in permissions["disabled"][command]:
        for i in range(0, len(user.roles)):
            if role_id == user.roles[i].id:
                highest_disabling = i
    highest_enabling = -1
    if command in permissions["enabled"]:
        for role_id in permissions["enabled"][command]:
            for i in range(0, len(user.roles)):
                if role_id == user.roles[i].id:
                    highest_enabling = i

    return highest_disabling < highest_enabling and not user.bot
