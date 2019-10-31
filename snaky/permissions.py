import tools.dictionnary as dictionnary
from snaky.snaky_data import SnakyData
from tools.parsing import try_parse_int

database = SnakyData("data")


def change_permission(new_permission, command_data):
    message = command_data["message"]
    guild = command_data["guild"]
    guild_folder = command_data["guild_folder"]
    arguments = command_data["arguments"]
    command = arguments.split(' ')[0]

    if command_data["private"]:
        return "I cannot change permissions in a private chat ! ;w;"
    if len(arguments.split(' ')) < 2:
        return "Please enter the command and the roles >:["

    depricated = "enabled" if new_permission == "disabled" else "disabled"

    parsing = try_parse_int(arguments)
    role = None
    if parsing[1]:
        role_id = parsing[0]
        role = guild.get_role(role_id)
    elif arguments.split(' ', 1)[1] == "everyone":
        role = guild.default_role
    elif len(message.role_mentions) > 0:
        role = message.role_mentions[0]
    else:
        role = dictionnary.find(guild.roles, "name", arguments.split(' ', 1)[1], False)
    if role == None:
        return "B-b-but this role doesn't exist ;-;"
    else:
        base = {
            "disabled": {
                "disable": [guild.default_role.id],
                "enable": [guild.default_role.id]
            },
            "enabled": {}
        }
        permissions = database.get_data(
            guild_folder + "/permissions.json", base)
        if not command in permissions[new_permission]:
            permissions[new_permission][command] = []
        permissions[new_permission][command].append(role.id)
        if command in permissions[depricated] and role.id in permissions[depricated][command]:
            permissions[depricated][command].remove(role.id)
        database.replace_data(
            permissions, guild_folder + "/permissions.json")
        mention = role.mention if role != guild.default_role else role
        return f"I {new_permission} {command} for the role {mention} ^w^"


def check_permission(command_data):
    user = command_data["message"].author
    guild = command_data["guild"]
    guild_folder = command_data["guild_folder"]
    command = command_data["command"]

    default_role = guild.default_role
    base = {
        "disabled": {
            "disable": [default_role.id],
            "enable": [default_role.id]
        },
        "enabled": {}
    }
    permissions = database.get_data(guild_folder + "/permissions.json", base)

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
