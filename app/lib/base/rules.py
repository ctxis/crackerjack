class RulesManager:
    def __init__(self, filesystem, rules_path):
        self.filesystem = filesystem
        self.rules_path = rules_path

    def get_rules(self):
        return self.filesystem.get_files(self.rules_path)

    def is_valid_rule(self, rule):
        rules = self.get_rules()
        return rule in rules

    def get_rule_path(self, rule):
        if not self.is_valid_rule(rule):
            return ''

        rules = self.get_rules()
        rule = rules[rule]
        return rule['path']
