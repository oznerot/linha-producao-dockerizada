def print_with_color(string, color=None):

    match color:
        case 'red':
            print("\033[91m{}\033[00m" .format(string))
        case 'green':
            print("\033[92m{}\033[00m" .format(string))
        case 'yellow':
            print("\033[93m{}\033[00m" .format(string))
        case 'light purple':
            print("\033[94m{}\033[00m" .format(string))
        case 'purple':
            print("\033[95m{}\033[00m" .format(string))
        case 'cyan':
            print("\033[96m{}\033[00m" .format(string))
        case 'light gray':
            print("\033[97m{}\033[00m" .format(string))
        case 'blue':
            print("\033[34m{}\033[00m" .format(string))
        case _:
            print("\033[98m{}\033[00m" .format(string))