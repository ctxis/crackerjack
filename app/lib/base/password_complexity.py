class PasswordComplexityManager:
    def __init__(self, min_length, min_lower, min_upper, min_digits, min_special):
        self.min_length = int(min_length)
        self.min_lower = int(min_lower)
        self.min_upper = int(min_upper)
        self.min_digits = int(min_digits)
        self.min_special = int(min_special)

    def meets_requirements(self, password):
        if len(password) < self.min_length:
            return False

        lower = upper = digits = special = 0
        for c in password:
            if c.islower():
                lower += 1
            elif c.isupper():
                upper += 1
            elif c.isdigit():
                digits += 1
            else:
                special += 1

        if lower < self.min_lower:
            return False
        elif upper < self.min_upper:
            return False
        elif digits < self.min_digits:
            return False
        elif special < self.min_special:
            return False

        return True

    def get_requirement_description(self):
        desc = []
        desc.append("Minimum Length is " + str(self.min_length))
        desc.append("Minimum Lowercase: " + str(self.min_lower))
        desc.append("Minimum Uppercase: " + str(self.min_upper))
        desc.append("Minimum Digits: " + str(self.min_digits))
        desc.append("Minimum Special: " + str(self.min_special))

        return ", ".join(desc)
