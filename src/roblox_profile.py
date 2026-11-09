from random import choice, randint, random
from string import ascii_lowercase, digits

class RobloxProfile:
    FIRST = [
        'Shadow', 'Flame', 'Wolf', 'Tiger', 'Dragon', 'Phoenix', 'Hunter', 'Ghost', 'Legend', 'Galaxy', 'Frost',
        'Sonic', 'Crystal', 'Silver', 'Dark', 'Power', 'Magic', 'Light', 'Alpha', 'King', 'Queen', 'Master',
        'Hero', 'Knight', 'Beast', 'Ultra', 'Storm', 'Blaze', 'Ice', 'Sky', 'Thunder', 'Raven', 'Fox', 'Lion',
        'Eagle', 'Night', 'Viper', 'Blade', 'Falcon', 'Claw', 'Venom', 'Echo', 'Mystic', 'Cyber', 'Nova', 'Orbit',
        'Pixel', 'Glitch', 'Byte', 'Circuit', 'Spark', 'Neon', 'Rogue', 'Stealth', 'Fusion', 'Prism', 'Wraith',
        'Saber', 'Pulse', 'Zero', 'Fury', 'Ninja', 'Gamer', 'Lava', 'Craft', 'Block', 'Code', 'Rocket', 'Moon',
        'Turbo', 'Lucky', 'Flash', 'Arrow', 'Ace', 'Omega', 'Chaos', 'Void', 'Rift', 'Toxic', 'Golden', 'Blizzard',
        'Inferno', 'Vortex', 'Aqua', 'Hyper', 'Drift', 'Haze', 'Craze', 'Giga', 'Rider'
    ]

    SUFFIX = [
        '', '', '', '', 'YT', 'TV', 'GG', 'Live', 'FPS', 'XD', 'Pro', 'HD',
        'Plays', 'Builds', 'Codes', 'OP', 'Alt', 'Real', 'Zone', 'Core'
    ]

    @staticmethod
    def _rand_prefix():
        chars = ascii_lowercase + digits

        return ''.join(choice(chars) for _ in range(randint(3, 4)))

    @staticmethod
    def _leet(text: str) -> str:
        mapping = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7'}
        out = []

        for ch in text:
            if ch.lower() in mapping and random() < 0.15:
                out.append(mapping[ch.lower()])
            else:
                out.append(ch)

        return ''.join(out)

    @staticmethod
    def get_username():
        while True:
            prefix = RobloxProfile._rand_prefix()

            part1 = choice(RobloxProfile.FIRST)
            part2 = choice(RobloxProfile.FIRST)

            while part2.lower() == part1.lower():
                part2 = choice(RobloxProfile.FIRST)

            use_underscore = random() < 0.4

            if use_underscore:
                username = prefix + '_' + part1 + part2
            else:
                username = prefix + part1 + part2

            suffix = choice(RobloxProfile.SUFFIX)
            if suffix:
                username += suffix

            if random() < 0.6:
                username += str(randint(1, 9999))

            if random() < 0.15:
                username = RobloxProfile._leet(username)

            username = ''.join(c for c in username if c.isalnum() or c == '_')

            if username.count('_') > 1:
                username = username.replace('_', '', username.count('_') - 1)

            if 3 <= len(username) <= 20:
                return username

    @staticmethod
    def get_password() -> str:
        return f'Generated${randint(1000000, 9999999)}'

    @staticmethod
    def get_birth_day() -> str:
        days = [str(i).zfill(2) for i in range(1, 29)]
        months = [str(i).zfill(2) for i in range(1, 13)]
        years = [str(x) for x in range(1997, 2007)]

        return f'{choice(years)}-{choice(months)}-{choice(days)}T23:00:00.000Z'

    @staticmethod
    def get_gender() -> int:
        return randint(1, 2)